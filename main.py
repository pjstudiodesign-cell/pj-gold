import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. Estilo PJ Gold
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #0d0d0d; }
        h1, h2, h3 { color: #D4AF37 !important; }
        label { color: #D4AF37 !important; font-weight: bold !important; }
        .stButton>button {
            background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%) !important;
            color: #000000 !important; font-weight: 900 !important; width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

# 2. Conexão
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1PduECxYhVlp8QC5lTu2nasRQbBPGtDI8vEhs1qL6IgE"
conn = st.connection("gsheets", type=GSheetsConnection)

def buscar_dados(aba):
    try:
        return conn.read(spreadsheet=URL_PLANILHA, worksheet=aba, ttl=0).dropna(how='all')
    except:
        return pd.DataFrame()

# 3. PDF
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"ORÇAMENTO: {cliente}", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, f"Serviço: {servico}\nValor: R$ {valor:.2f}\nPrazo: {prazo}\nPagamento: {pgto}")
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 4. Interface
def main():
    aplicar_estilo()
    st.sidebar.title("⚜️ PJ Gold")
    menu = ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"]
    escolha = st.sidebar.radio("Navegar:", menu)
    
    df_projetos = buscar_dados("Projetos")
    df_config = buscar_dados("Config_Empresa")

    if escolha == "Painel":
        st.title("⚜️ Painel")
        if not df_projetos.empty:
            v_total = pd.to_numeric(df_projetos['valor'], errors='coerce').sum()
            st.metric("Total de Projetos", f"R$ {v_total:,.2f}")

    elif escolha == "Novo Job":
        st.title("⚜️ Novo Job")
        with st.form("orc_form"):
            n = st.text_input("Cliente"); tel = st.text_input("WhatsApp")
            v = st.number_input("Valor", min_value=0.0)
            ser = st.text_area("Serviço")
            if st.form_submit_button("SALVAR"):
                if n and ser:
                    novo = pd.DataFrame([{"cliente":n,"servico":ser,"valor":v,"status":"Em Produção","data_inicio":datetime.now().strftime("%d/%m/%Y"),"telefone":tel}])
                    try:
                        # Tenta salvar - se o Secrets não estiver lá, ele dará o erro
                        df_atualizado = pd.concat([df_projetos, novo], ignore_index=True)
                        conn.update(spreadsheet=URL_PLANILHA, data=df_atualizado, worksheet="Projetos")
                        st.success("Salvo com sucesso!")
                    except:
                        st.error("ERRO DE PERMISSÃO: A planilha precisa da chave JSON no arquivo secrets.toml.")

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Gestão")
        st.write(df_projetos)

    elif escolha == "Configurações":
        st.title("⚜️ Configurações")
        st.write("Configurações da Empresa")

if __name__ == "__main__":
    main()
