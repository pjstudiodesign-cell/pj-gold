import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 1. Configuração da Página
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

# 2. Estilo Visual Premium
def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #0d0d0d; }
        h1, h2, h3 { color: #D4AF37 !important; }
        [data-testid="stSidebarNav"] span { color: #ffffff !important; font-weight: bold !important; }
        .st-emotion-cache-p5msec, .st-emotion-cache-1h9usn2, p { color: #ffffff !important; }
        label { color: #D4AF37 !important; font-weight: bold !important; }
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%) !important;
            color: #000000 !important;
            font-weight: 900 !important;
            border-radius: 8px !important;
            width: 100% !important;
            border: none !important;
            height: 3em !important;
            text-transform: uppercase;
        }
        section[data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #D4AF37; }
        .stMetric { background-color: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #333; }
        [data-testid="stMetricValue"] { color: #D4AF37 !important; }
        </style>
    """, unsafe_allow_html=True)

# 3. Conexão
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1PduECxYhVlp8QC5lTu2nasRQbBPGtDI8vEhs1qL6IgE"
conn = st.connection("gsheets", type=GSheetsConnection)

def buscar_dados():
    try:
        df = conn.read(spreadsheet=URL_PLANILHA, worksheet="Projetos", ttl=0)
        return df.dropna(how='all')
    except:
        return pd.DataFrame(columns=["cliente", "servico", "valor", "status", "data_inicio", "telefone", "valor_entrada", "status_entrada", "valor_final", "status_final", "status_integral", "prazo_salvo", "pagamento_salvo", "revisao_salva", "obs_salva"])

def buscar_config():
    try:
        df = conn.read(spreadsheet=URL_PLANILHA, worksheet="Config_Empresa", ttl=0)
        return df.dropna(how='all')
    except:
        return pd.DataFrame([{"nome": "PJ Gold", "slogam": "Studio Criativo", "contato": "", "endereco": ""}])

# 4. Geração de PDF
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs, config):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(20, 20, 20); pdf.rect(0, 0, 210, 65, 'F')
        pdf.set_y(12); pdf.set_font("Arial", 'B', 20); pdf.set_text_color(212, 175, 55)
        n_emp = config['nome'].iloc[0] if not config.empty else "PJ Gold"
        s_emp = config['slogam'].iloc[0] if not config.empty else ""
        pdf.cell(0, 12, n_emp, ln=True, align='C')
        pdf.set_font("Arial", 'I', 10); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 6, s_emp, ln=True, align='C')
        pdf.set_y(75); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
        pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
        pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
        pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "1. DESCRICAO DO SERVICO", ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}")
        pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "2. CONDICOES", ln=True)
        pdf.set_font("Arial", '', 11); pdf.cell(0, 8, f"- Prazo: {prazo} | Revisões: {rev}", ln=True)
        pdf.cell(0, 8, f"- Forma de Pagamento: {pgto}", ln=True)
        pdf.set_y(-40); pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

# 5. Interface
def main():
    aplicar_estilo()
    st.sidebar.title("⚜️ PJ Gold")
    menu = ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"]
    escolha = st.sidebar.radio("Navegar:", menu)
    
    df = buscar_dados()
    df_config = buscar_config()

    if escolha == "Painel":
        st.title("⚜️ Painel PJ Gold")
        total_rec = 0.0; total_pend = 0.0
        if not df.empty:
            for _, r in df.iterrows():
                v_total = pd.to_numeric(r['valor'], errors='coerce') or 0
                if r.get('status_integral') == 'Recebido': total_rec += v_total
                else:
                    total_rec += (pd.to_numeric(r.get('valor_entrada', 0), errors='coerce') if r.get('status_entrada') == 'Recebido' else 0)
                    total_rec += (pd.to_numeric(r.get('valor_final', 0), errors='coerce') if r.get('status_final') == 'Recebido' else 0)
            total_pend = (pd.to_numeric(df['valor'], errors='coerce').sum() or 0) - total_rec
        col1, col2 = st.columns(2)
        with col1: st.metric("Total em Caixa", f"R$ {total_rec:,.2f}")
        with col2: st.metric("A Receber", f"R$ {total_pend:,.2f}")

    elif escolha == "Novo Job":
        st.title("⚜️ Novo Orçamento")
        with st.form("orc_form"):
            c1, c2 = st.columns(2); n = c1.text_input("Cliente"); tel = c2.text_input("WhatsApp")
            v = st.number_input("Valor Total", min_value=0.0, step=0.01)
            ser = st.text_area("Serviço"); obs_in = st.text_input("Observações")
            c3, c4, c5 = st.columns(3); prz = c3.text_input("Prazo", "10 dias úteis")
            rev = c4.selectbox("Revisões", ["Padrão", "1", "2", "3", "Ilimitadas"])
            pag = c5.text_input("Pagamento", "50% entrada / 50% entrega")
            if st.form_submit_button("SALVAR NA NUVEM"):
                if n and ser:
                    novo = pd.DataFrame([{"cliente":n,"servico":ser,"valor":v,"status":"Em Produção","data_inicio":datetime.now().strftime("%d/%m/%Y"),"telefone":tel,"valor_entrada":v/2,"status_entrada":"Pendente","valor_final":v/2,"status_final":"Pendente","status_integral":"Pendente","prazo_salvo":prz,"pagamento_salvo":pag,"revisao_salva":rev,"obs_salva":obs_in}])
                    # Técnica para evitar UnsupportedOperationError
                    updated_df = pd.concat([df, novo], ignore_index=True).dropna(how='all')
                    conn.update(spreadsheet=URL_PLANILHA, data=updated_df, worksheet="Projetos")
                    st.success("Salvo!"); st.rerun()

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Gestão e Financeiro")
        if df.empty: st.info("Sem projetos.")
        else:
            for i, r in df.iterrows():
                with st.expander(f"📌 {r['cliente']} | R$ {float(r['valor']):.2f}"):
                    st.write(f"**Serviço:** {r['servico']}")
                    col1, col2, col3 = st.columns(3)
                    s_int = col1.selectbox("Integral", ["Pendente", "Recebido"], index=0 if r.get('status_integral') == "Pendente" else 1, key=f"i{i}")
                    s_ent = col2.selectbox("Entrada", ["Pendente", "Recebido"], index=0 if r.get('status_entrada') == "Pendente" else 1, key=f"e{i}")
                    s_fin = col3.selectbox("Final", ["Pendente", "Recebido"], index=0 if r.get('status_final') == "Pendente" else 1, key=f"f{i}")
                    if st.button("Atualizar", key=f"at{i}"):
                        df.at[i, 'status_integral'] = s_int; df.at[i, 'status_entrada'] = s_ent; df.at[i, 'status_final'] = s_fin
                        conn.update(spreadsheet=URL_PLANILHA, data=df, worksheet="Projetos")
                        st.success("OK!"); st.rerun()
                    if st.button("PDF", key=f"pdf{i}"):
                        pdf = gerar_pdf_orcamento(r['cliente'], r['servico'], r['valor'], r.get('pagamento_salvo',''), r.get('prazo_salvo',''), r.get('revisao_salva',''), r.get('obs_salva',''), df_config)
                        st.download_button("Baixar", pdf, f"Orc_{r['cliente']}.pdf", key=f"dl{i}")

    elif escolha == "Configurações":
        st.title("⚜️ Configurações da Empresa")
        with st.form("config_form"):
            n_v = df_config['nome'].iloc[0] if not df_config.empty else "PJ Gold"
            nome_emp = st.text_input("Nome da Empresa", n_v)
            if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
                nova_config = pd.DataFrame([{"nome": nome_emp, "slogam": "", "contato": "", "endereco": ""}])
                conn.update(spreadsheet=URL_PLANILHA, data=nova_config, worksheet="Config_Empresa")
                st.success("Salvo!"); st.rerun()

if __name__ == "__main__":
    main()
