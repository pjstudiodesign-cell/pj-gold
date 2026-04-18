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
        div[data-testid="metric-container"] {
            background-color: #111111;
            border: 1px solid #333;
            padding: 20px;
            border-radius: 10px;
        }
        [data-testid="stMetricValue"] { color: #FFD700 !important; }
        [data-testid="stMetricLabel"] { color: #ffffff !important; }
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%) !important;
            color: #000000 !important;
            font-weight: 900 !important;
            border-radius: 8px !important;
            text-transform: uppercase;
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
            background-color: #1a1a1a !important;
            color: #FFD700 !important;
            border: 1px solid #333 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# 3. Conexão e Funções de Dados
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados_projetos():
    try:
        df = conn.read(worksheet="Página1", ttl=0)
        return df if df is not None else pd.DataFrame(columns=["id", "cliente", "servico", "valor", "status_integral", "prazo", "pagamento", "obs", "telefone"])
    except:
        return pd.DataFrame(columns=["id", "cliente", "servico", "valor", "status_integral", "prazo", "pagamento", "obs", "telefone"])

def ler_config():
    try:
        df_conf = conn.read(worksheet="Config", ttl=0)
        if df_conf is not None and not df_conf.empty:
            return df_conf.iloc[0].to_dict()
    except: pass
    return {"nome_studio": "PJ GOLD", "slogan": "Elite Service", "contato": "", "email": "", "endereco": ""}

# 4. Função de PDF
def gerar_pdf_orcamento(cliente, telefone, servico, valor, pgto, prazo, obs, info_empresa):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(10, 10, 10); pdf.rect(0, 0, 210, 65, 'F')
    pdf.set_y(12); pdf.set_font("Arial", 'B', 22); pdf.set_text_color(255, 215, 0)
    pdf.cell(0, 12, str(info_empresa.get('nome_studio', 'PJ GOLD')).upper(), ln=True, align='C')
    pdf.set_font("Arial", 'I', 10); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 6, str(info_empresa.get('slogan', 'Elite Service')), ln=True, align='C')
    pdf.set_y(75); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 11)
    pdf.cell(100, 8, f"CLIENTE: {str(cliente).upper()}", ln=0)
    pdf.cell(0, 8, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
    pdf.ln(10); pdf.set_font("Arial", 'B', 13); pdf.cell(0, 10, "DETALHES DO SERVICO", ln=True)
    pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}\n\nObs: {obs}")
    pdf.set_y(-45); pdf.set_font("Arial", 'B', 18); pdf.set_text_color(184, 134, 11)
    pdf.cell(0, 15, f"TOTAL: R$ {valor:,.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 5. Interface
def main():
    aplicar_estilo()
    df = ler_dados_projetos()
    info_f = ler_config()
    
    st.sidebar.markdown(f"<h2 style='color:#FFD700; text-align:center;'>⚜️ {info_f.get('nome_studio', 'PJ GOLD')}</h2>", unsafe_allow_html=True)
    escolha = st.sidebar.radio("Navegar:", ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"])

    if escolha == "Painel":
        st.title(f"💰 Painel {info_f.get('nome_studio', 'PJ GOLD')}")
        tr, tp = 0.0, 0.0
        if not df.empty and 'valor' in df.columns:
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
            tr = df[df['status_integral'] == 'Recebido']['valor'].sum()
            tp = df[df['status_integral'] != 'Recebido']['valor'].sum()
        c1, c2 = st.columns(2)
        c1.metric("Total em Caixa", f"R$ {tr:,.2f}")
        c2.metric("A Receber", f"R$ {tp:,.2f}")

    elif escolha == "Novo Job":
        st.title("➕ Novo Contrato")
        with st.form("orc"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Cliente")
            t = c2.text_input("WhatsApp")
            v = st.number_input("Valor", min_value=0.0)
            ser = st.text_area("Serviço")
            obs = st.text_area("Observações")
            if st.form_submit_button("SALVAR"):
                try:
                    nova = pd.DataFrame([{"id": len(df)+1, "cliente": n, "telefone": t, "servico": ser, "valor": v, "status_integral": "Pendente", "prazo": "7 dias", "pagamento": "50/50", "obs": obs}])
                    conn.update(worksheet="Página1", data=pd.concat([df, nova], ignore_index=True))
                    st.success("✅ Salvo! Gere o PDF abaixo.")
                    st.session_state['pdf_pronto'] = {"n":n,"t":t,"ser":ser,"v":v,"obs":obs}
                except Exception as e:
                    st.error(f"Erro de Permissão: Altere o Google Sheets para 'Editor'.")

        if 'pdf_pronto' in st.session_state:
            p = st.session_state['pdf_pronto']
            pdf = gerar_pdf_orcamento(p['n'], p['t'], p['ser'], p['v'], "50/50", "7 dias", p['obs'], info_f)
            st.download_button("📩 BAIXAR PDF", pdf, f"Orc_{p['n']}.pdf")

    elif escolha == "Configurações":
        st.title("⚙️ Configurações")
        with st.form("conf"):
            nome = st.text_input("Empresa", info_f.get('nome_studio', ''))
            slogan = st.text_input("Slogan", info_f.get('slogan', ''))
            if st.form_submit_button("SALVAR"):
                try:
                    conn.update(worksheet="Config", data=pd.DataFrame([{"nome_studio": nome, "slogan": slogan, "contato": "", "email": "", "endereco": ""}]))
                    st.success("Configurações Salvas!"); st.rerun()
                except: st.error("Erro: Planilha precisa estar como 'Editor'.")

if __name__ == "__main__": main()
