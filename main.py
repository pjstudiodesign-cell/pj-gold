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
        h1, h2, h3, p, span, label { color: #FFD700 !important; font-weight: bold !important; }
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%) !important;
            color: #000000 !important; font-weight: 900 !important;
            border-radius: 8px !important; width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

# 3. Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados():
    try:
        return conn.read(ttl=0) # ttl=0 força o sistema a ler o dado mais novo sempre
    except:
        return pd.DataFrame(columns=["id", "cliente", "servico", "valor", "status_integral", "status_entrada", "status_final", "telefone", "obs_salva", "prazo_salvo", "pagamento_salvo", "revisao_salva"])

def salvar_dados(df):
    conn.update(data=df)
    st.cache_data.clear()

# 4. Funções de PDF (Adaptadas para ler da planilha)
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(10, 10, 10); pdf.rect(0, 0, 210, 65, 'F')
    pdf.set_y(12); pdf.set_font("Arial", 'B', 20); pdf.set_text_color(255, 215, 0)
    pdf.cell(0, 12, "PJ Gold", ln=True, align='C')
    pdf.set_y(75); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
    pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
    pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "ESCOPO DO SERVICO", ln=True)
    pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}")
    pdf.ln(10); pdf.set_font("Arial", 'B', 20); pdf.set_text_color(184, 134, 11)
    pdf.cell(0, 15, f"INVESTIMENTO: R$ {valor:,.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 5. Interface Principal
def main():
    aplicar_estilo()
    df = ler_dados()
    
    st.sidebar.markdown("<h2 style='color:#FFD700; text-align:center;'>⚜️ PJ Gold</h2>", unsafe_allow_html=True)
    menu = ["Painel", "Novo Job", "Gestão de Projetos"]
    escolha = st.sidebar.radio("Navegar:", menu)

    if escolha == "Painel":
        st.title("💰 Dashboard de Elite (Google Sheets)")
        if not df.empty:
            total_rec = df[df['status_integral'] == 'Recebido']['valor'].sum()
            total_pend = df[df['status_integral'] != 'Recebido']['valor'].sum()
            c1, c2 = st.columns(2)
            c1.metric("Total Recebido", f"R$ {total_rec:,.2f}")
            c2.metric("Pendente", f"R$ {total_pend:,.2f}")
        else:
            st.info("Nenhum dado encontrado na planilha.")

    elif escolha == "Novo Job":
        st.title("➕ Cadastrar Novo Contrato")
        with st.form("orc_form"):
            n = st.text_input("Nome do Cliente")
            ser = st.text_area("Descrição do Serviço")
            v = st.number_input("Valor", min_value=0.0)
            prz = st.text_input("Prazo", "7 dias úteis")
            pag = st.text_input("Pagamento", "50/50")
            if st.form_submit_button("SALVAR NA PLANILHA"):
                novo_id = len(df) + 1
                nova_linha = pd.DataFrame([{
                    "id": novo_id, "cliente": n, "servico": ser, "valor": v, 
                    "status_integral": "Pendente", "status_entrada": "Pendente",
                    "status_final": "Pendente", "prazo_salvo": prz, "pagamento_salvo": pag
                }])
                df = pd.concat([df, nova_linha], ignore_index=True)
                salvar_dados(df)
                st.success("Salvo no Google Sheets!")

    elif escolha == "Gestão de Projetos":
        st.title("📂 Controle de Jobs")
        if not df.empty:
            for i, r in df.iterrows():
                with st.expander(f"⚜️ {r['cliente']} - R$ {r['valor']}"):
                    st.write(f"Serviço: {r['servico']}")
                    status = st.selectbox("Status", ["Pendente", "Recebido"], index=0 if r['status_integral'] == "Pendente" else 1, key=f"sel{i}")
                    if st.button("Atualizar", key=f"btn{i}"):
                        df.at[i, 'status_integral'] = status
                        salvar_dados(df)
                        st.rerun()
                    
                    pdf = gerar_pdf_orcamento(r['cliente'], r['servico'], r['valor'], r['pagamento_salvo'], r['prazo_salvo'], "", "")
                    st.download_button("Baixar PDF", pdf, f"Orcamento_{r['cliente']}.pdf", key=f"pdf{i}")

if __name__ == "__main__":
    main()
