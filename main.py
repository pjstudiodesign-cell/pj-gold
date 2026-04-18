import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os

# 1. Configuração da Página
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

# 2. Estilo Visual Premium (PJ Gold) - MANTIDO INTEGRALMENTE
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
        .stDownloadButton>button p { color: #000000 !important; font-weight: 900 !important; }
        section[data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #D4AF37; }
        .stMetric { background-color: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #333; }
        [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 1.2em !important; }
        [data-testid="stMetricValue"] { color: #D4AF37 !important; }
        </style>
    """, unsafe_allow_html=True)

# 3. Conexão Blindada com Google Sheets
# Substitui o SQLite para os dados nunca mais sumirem
conn = st.connection("gsheets", type=GSheetsConnection)

def buscar_dados():
    return conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/1Zt6iC9D9fC9W3Ea_Z0I6_kI1R4u_F9mS3A0Q7K9R8E0", worksheet="Projetos")

# 4. Geração de PDF (MANTIDO INTEGRALMENTE)
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(20, 20, 20)
        pdf.rect(0, 0, 210, 65, 'F')
        pdf.set_y(12)
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 12, "PJ Gold", ln=True, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 6, "Elite Service", ln=True, align='C')
        pdf.set_y(75); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
        pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
        pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
        pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "1. DESCRICAO DO SERVICO", ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}")
        if obs:
            pdf.ln(2); pdf.set_font("Arial", 'B', 11); pdf.cell(10, 7, "Obs: "); pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{obs}")
        pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "2. CONDICOES", ln=True)
        pdf.set_font("Arial", '', 11); pdf.cell(0, 8, f"- Prazo: {prazo} | Revisões: {rev}", ln=True)
        pdf.cell(0, 8, f"- Forma de Pagamento: {pgto}", ln=True)
        pdf.set_y(-40); pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

def gerar_pdf_recibo(cliente, servico, valor):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_draw_color(212, 175, 55); pdf.rect(5, 5, 200, 120)
        pdf.set_font("Arial", 'B', 18); pdf.set_y(15); pdf.cell(0, 15, "RECIBO DE PAGAMENTO", ln=True, align='C')
        pdf.ln(10); pdf.set_font("Arial", '', 12)
        texto = f"Recebemos de {str(cliente).upper()}, a importância de R$ {valor:,.2f} referente ao serviço de: {servico}."
        pdf.multi_cell(0, 10, texto, align='L')
        pdf.ln(10); pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
        pdf.ln(15); pdf.cell(0, 10, "__________________________________________________", ln=True, align='C')
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, "PJ Gold", ln=True, align='C')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

# 5. Interface Principal
def main():
    aplicar_estilo()
    
    st.sidebar.title("⚜️ PJ Gold Studio")
    menu = ["Painel", "Novo Job", "Gestão de Projetos"]
    escolha = st.sidebar.radio("Navegar:", menu)

    # Carregar dados da planilha
    df = buscar_dados()

    if escolha == "Painel":
        st.title("⚜️ Painel PJ Gold")
        total_rec = 0.0
        if not df.empty:
            total_rec = df[df['status_integral'] == 'Recebido']['valor'].sum()
            total_pend = df['valor'].sum() - total_rec
        else:
            total_pend = 0.0
            
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
                    novo_job = pd.DataFrame([{
                        "cliente": n, "servico": ser, "valor": v, "status": "Em Produção",
                        "data_inicio": datetime.now().strftime("%d/%m/%Y"), "telefone": tel,
                        "status_entrada": "Pendente", "status_final": "Pendente", "status_integral": "Pendente",
                        "prazo_salvo": prz, "pagamento_salvo": pag, "revisao_salva": rev, "obs_salva": obs_in
                    }])
                    updated_df = pd.concat([df, novo_job], ignore_index=True)
                    conn.update(spreadsheet="https://docs.google.com/spreadsheets/d/1Zt6iC9D9fC9W3Ea_Z0I6_kI1R4u_F9mS3A0Q7K9R8E0", data=updated_df)
                    st.success("Orçamento Salvo na Planilha Google!")
                    st.rerun()

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Gestão e Financeiro")
        if df.empty:
            st.info("Nenhum projeto encontrado.")
        else:
            for index, r in df.iterrows():
                with st.expander(f"📌 {r['cliente']} | R$ {r['valor']:.2f}"):
                    st.write(f"**Serviço:** {r['servico']}")
                    col1, col2, col3 = st.columns(3)
                    s_int = col1.selectbox("Integral", ["Pendente", "Recebido"], index=0 if r['status_integral'] == "Pendente" else 1, key=f"i{index}")
                    
                    c_at, c_orc, c_rec, c_del = st.columns(4)
                    if c_at.button("Atualizar Status", key=f"at{index}"):
                        df.at[index, 'status_integral'] = s_int
                        conn.update(spreadsheet="https://docs.google.com/spreadsheets/d/1Zt6iC9D9fC9W3Ea_Z0I6_kI1R4u_F9mS3A0Q7K9R8E0", data=df)
                        st.rerun()
                    
                    if c_orc.button("Gerar PDF", key=f"pdf{index}"):
                        pdf_o = gerar_pdf_orcamento(r['cliente'], r['servico'], r['valor'], r['pagamento_salvo'], r['prazo_salvo'], r['revisao_salva'], r['obs_salva'])
                        st.download_button("Baixar", pdf_o, f"Orcamento_{r['cliente']}.pdf", key=f"dl{index}")

if __name__ == "__main__":
    main()
