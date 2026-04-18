import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import requests

# 1. Configuração e Estilo PJ Gold (Inalterado)
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

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

# 2. Configuração de Links (Onde a mágica acontece)
# Cole o link da sua planilha aqui para LEITURA
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1PduECxYhVlp8QC5lTu2nasRQbBPGtDI8vEhs1qL6IgE/gviz/tq?tqx=out:csv&sheet="

def buscar_dados(aba):
    try:
        url = f"{URL_PLANILHA}{aba}"
        return pd.read_csv(url).dropna(how='all')
    except:
        return pd.DataFrame()

# 3. Gerador de PDF Original
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs, config):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(20, 20, 20); pdf.rect(0, 0, 210, 65, 'F')
        pdf.set_y(12); pdf.set_font("Arial", 'B', 20); pdf.set_text_color(212, 175, 55)
        n_emp = config['nome'].iloc[0] if not config.empty else "PJ Gold"
        pdf.cell(0, 12, n_emp, ln=True, align='C')
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

# 4. Interface
def main():
    aplicar_estilo()
    st.sidebar.title("⚜️ PJ Gold")
    menu = ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"]
    escolha = st.sidebar.radio("Navegar:", menu)
    
    df_projetos = buscar_dados("Projetos")
    df_config = buscar_dados("Config_Empresa")

    if escolha == "Painel":
        st.title("⚜️ Painel PJ Gold")
        total_rec = 0.0
        if not df_projetos.empty:
            total_rec = pd.to_numeric(df_projetos.get('valor', 0), errors='coerce').sum()
        st.metric("Volume em Projetos", f"R$ {total_rec:,.2f}")

    elif escolha == "Novo Job":
        st.title("⚜️ Novo Orçamento")
        with st.form("orc_form"):
            c1, c2 = st.columns(2); n = c1.text_input("Cliente"); tel = c2.text_input("WhatsApp")
            v = st.number_input("Valor Total", min_value=0.0, step=0.01)
            ser = st.text_area("Serviço"); obs_in = st.text_input("Observações")
            prz = st.text_input("Prazo", "10 dias úteis")
            rev = st.selectbox("Revisões", ["Padrão", "1", "2", "3", "Ilimitadas"])
            pag = st.text_input("Pagamento", "50% entrada / 50% entrega")
            
            if st.form_submit_button("SALVAR NA NUVEM"):
                st.warning("Paulo, o Google bloqueou a gravação direta. Para liberar, use o menu 'Configurações'.")

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Gestão")
        if df_projetos.empty: st.info("Sem projetos.")
        else:
            for i, r in df_projetos.iterrows():
                with st.expander(f"📌 {r['cliente']} | R$ {r['valor']}"):
                    if st.button("Gerar PDF", key=f"pdf{i}"):
                        pdf = gerar_pdf_orcamento(r['cliente'], r.get('servico',''), r['valor'], r.get('pagamento_salvo',''), r.get('prazo_salvo',''), r.get('revisao_salva',''), r.get('obs_salva',''), df_config)
                        st.download_button("Baixar PDF", pdf, f"Orc_{r['cliente']}.pdf", key=f"dl{i}")

    elif escolha == "Configurações":
        st.title("⚜️ Configurações")
        st.info("Para salvar dados, o Google exige uma Service Account agora. Como você está cansado, use a planilha diretamente por enquanto e o sistema fará a leitura automática.")
        st.write(f"[Acesse sua Planilha aqui]({URL_PLANILHA.split('/gviz/')[0]})")

if __name__ == "__main__":
    main()
