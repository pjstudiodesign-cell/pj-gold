import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. Configuração da Página
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

# 2. Estilo Visual PJ GOLD
def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #050505; }
        [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
            background-color: #050505 !important;
            border-right: 1px solid #FFD700;
        }
        [data-testid="stSidebarNav"] span, [data-testid="stSidebar"] p, label {
            color: #FFD700 !important;
            font-weight: bold !important;
        }
        h1, h2, h3, p, span { color: #FFD700 !important; }
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%) !important;
            color: #000000 !important;
            font-weight: 900 !important;
            border-radius: 8px !important;
            width: 100% !important;
            text-transform: uppercase;
            height: 3em !important;
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
            background-color: #1a1a1a !important;
            color: #FFD700 !important;
            border: 1px solid #333 !important;
        }
        [data-testid="stMetricValue"] { color: #FFD700 !important; }
        [data-testid="stMetricLabel"] { color: #ffffff !important; }
        </style>
    """, unsafe_allow_html=True)

# 3. Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados_projetos():
    try:
        return conn.read(worksheet="Página1", ttl=0)
    except:
        return pd.DataFrame(columns=["id", "cliente", "servico", "valor", "status_integral", "prazo", "pagamento", "obs"])

def ler_config():
    try:
        df_conf = conn.read(worksheet="Config", ttl=0)
        if df_conf is not None and not df_conf.empty:
            return df_conf.iloc[0].to_dict()
    except:
        pass
    return {"nome_studio": "PJ GOLD", "slogan": "Elite Service", "contato": "", "email": "", "endereco": ""}

# 4. Funções de PDF
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, obs, info_empresa):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(10, 10, 10); pdf.rect(0, 0, 210, 65, 'F')
    pdf.set_y(12); pdf.set_font("Arial", 'B', 22); pdf.set_text_color(255, 215, 0)
    pdf.cell(0, 12, str(info_empresa['nome_studio']).upper(), ln=True, align='C')
    pdf.set_font("Arial", 'I', 10); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 6, str(info_empresa['slogan']), ln=True, align='C')
    
    pdf.set_y(75); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
    pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
    
    pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "1. ESCOPO DO SERVICO", ln=True)
    pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}")
    
    if obs:
        pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "2. EXIGENCIAS / OBSERVACOES", ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{obs}")
    
    pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "3. CONDICOES", ln=True)
    pdf.set_font("Arial", '', 11); pdf.cell(0, 8, f"- Prazo: {prazo} | Pagamento: {pgto}", ln=True)
    
    pdf.set_y(-45); pdf.set_font("Arial", 'B', 20); pdf.set_text_color(184, 134, 11)
    pdf.cell(0, 15, f"INVESTIMENTO: R$ {valor:,.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 5. Interface
def main():
    aplicar_estilo()
    df = ler_dados_projetos()
    info_f = ler_config()
    
    st.sidebar.markdown(f"<h2 style='color:#FFD700; text-align:center;'>⚜️ {info_f['nome_studio']}</h2>", unsafe_allow_html=True)
    menu = ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"]
    escolha = st.sidebar.radio("Navegar:", menu)

    if escolha == "Painel":
        st.title("💰 Dashboard de Elite")
        if not df.empty:
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
            total_rec = df[df['status_integral'] == 'Recebido']['valor'].sum()
            total_pend = df[df['status_integral'] != 'Recebido']['valor'].sum()
            c1, c2 = st.columns(2)
            c1.metric("Total Recebido", f"R$ {total_rec:,.2f}")
            c2.metric("A Receber", f"R$ {total_pend:,.2f}")
        else: st.info("Sem dados na planilha.")

    elif escolha == "Novo Job":
        st.title("➕ Novo Contrato")
        with st.form("orc"):
            col1, col2 = st.columns(2)
            n = col1.text_input("Cliente")
            v = col2.number_input("Valor", min_value=0.0)
            ser = st.text_area("Descrição do Serviço")
            ob_cli = st.text_area("Exigências ou Observações do Cliente")
            
            col3, col4 = st.columns(2)
            prz = col3.text_input("Prazo", "7 dias")
            pag = col4.text_input("Pagamento", "50/50")
            
            if st.form_submit_button("SALVAR E GERAR"):
                nova = pd.DataFrame([{"id": len(df)+1, "cliente": n, "servico": ser, "valor": v, "status_integral": "Pendente", "prazo": prz, "pagamento": pag, "obs": ob_cli}])
                conn.update(worksheet="Página1", data=pd.concat([df, nova], ignore_index=True))
                st.success("Job Salvo com Sucesso!"); st.rerun()

    elif escolha == "Gestão de Projetos":
        st.title("📂 Controle de Projetos")
        if not df.empty:
            for i, r in df.iterrows():
                with st.expander(f"⚜️ {r['cliente']} | R$ {r['valor']}"):
                    st.write(f"**Serviço:** {r['servico']}")
                    if 'obs' in r and r['obs']:
                        st.write(f"**Exigências:** {r['obs']}")
                    
                    status = st.selectbox("Status", ["Pendente", "Recebido"], index=0 if r['status_integral']=="Pendente" else 1, key=f"s{i}")
                    if st.button("Atualizar Status", key=f"u{i}"):
                        df.at[i, 'status_integral'] = status
                        conn.update(worksheet="Página1", data=df); st.rerun()
                    
                    obs_val = r['obs'] if 'obs' in r else ""
                    pdf = gerar_pdf_orcamento(r['cliente'], r['servico'], r['valor'], r['pagamento'], r['prazo'], obs_val, info_f)
                    st.download_button("Baixar PDF", pdf, f"Orc_{r['cliente']}.pdf", key=f"p{i}")
        else: st.warning("Nenhum projeto encontrado.")

    elif escolha == "Configurações":
        st.title("⚙️ Configurações do Studio")
        with st.form("conf"):
            nome = st.text_input("Nome do Studio", info_f['nome_studio'])
            slogan = st.text_input("Slogan", info_f['slogan'])
            if st.form_submit_button("SALVAR CONFIGS"):
                df_conf = pd.DataFrame([{"nome_studio": nome, "slogan": slogan, "contato": "", "email": "", "endereco": ""}])
                conn.update(worksheet="Config", data=df_conf)
                st.success("Configurações atualizadas!"); st.rerun()

if __name__ == "__main__":
    main()
