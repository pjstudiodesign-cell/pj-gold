import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- CONEXÃO SUPABASE (CONFIGURADA) ---
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "sb_publishable_qisG5bDBD-AxpBKW9LmBnA_p-_M671n"

try:
    supabase: Client = create_client(URL, KEY)
except Exception:
    st.error("Erro na conexão com o banco de dados.")
    st.stop()

# --- CSS CUSTOMIZADO (PRETO E DOURADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; width: 100%; border-radius: 5px; border: none; }
    .stButton>button:hover { background-color: #F5D76E; color: black; }
    .stMetric { background-color: #1c1c1c; padding: 15px; border-radius: 10px; border: 1px solid #D4AF37; }
    div[data-testid="stExpander"] { border: 1px solid #D4AF37; background-color: #121212; border-radius: 8px; margin-bottom: 10px; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #1c1c1c; color: white; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(212, 175, 55) # Dourado
        self.cell(0, 10, 'PJ STUDIO GOLD PRO - DOCUMENTO OFICIAL', 0, 1, 'C')
        self.ln(10)

def gerar_pdf_projeto(dados, config, tipo="ORÇAMENTO"):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        
        pdf.cell(0, 10, f"Empresa: {config.get('nome_empresa', 'PJ Studio')}", ln=True)
        pdf.cell(0, 10, f"CNPJ: {config.get('cnpj', '---')} | WhatsApp: {config.get('whatsapp', '---')}", ln=True)
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
        
        pdf.cell(0, 10, f"Tipo: {tipo}", ln=True)
        pdf.cell(0, 10, f"Cliente: {dados.get('cliente', 'Não informado')}", ln=True)
        pdf.cell(0, 10, f"Serviço: {dados.get('nome_projeto', 'Não informado')}", ln=True)
        valor = float(dados.get('valor_total', 0))
        pdf.cell(0, 10, f"Valor Total: R$ {valor:.2f}", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Descrição: {dados.get('descricao', 'Sem descrição detalhada.')}")
        
        return pdf.output(dest='S').encode('latin-1')
    except:
        return None

# --- LÓGICA DE DADOS ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data, conf.data[0] if conf.data else {}
    except:
        return [], {}

projetos, config = carregar_dados()

# Métricas 50/50
no_bolso = 0
a_receber = 0
for p in projetos:
    try:
        v = float(p.get('valor_total', 0))
        if p.get('status_integral') == 'Recebido': 
            no_bolso += v
        else:
            if p.get('status_entrada') == 'Recebido': no_bolso += (v * 0.5)
            else: a_receber += (v * 0.5)
            if p.get('status_final') == 'Recebido': no_bolso += (v * 0.5)
            else: a_receber += (v * 0.5)
    except:
        continue

# --- INTERFACE ---
st.title("⚜️ PJ STUDIO GOLD PRO")

col1, col2 = st.columns(2)
col1.metric("💰 DINHEIRO NO BOLSO", f"R$ {no_bolso:,.2f}")
col2.metric("⏳ CONTAS A RECEBER", f"R$ {a_receber:,.2f}")

tabs = st.tabs(["📋 Gestão de Projetos", "➕ Novo Job", "⚙️ Configurações"])

with tabs[0]:
    if not projetos:
        st.info("Nenhum projeto cadastrado.")
    for p in projetos:
        with st.expander(f"Projeto: {p.get('nome_projeto')} - Cliente: {p.get('cliente')}"):
            c1, c2, c3 = st.columns(3)
            st_int = c1.selectbox("Integral", ["Pendente", "Recebido"], index=0 if p.get('status_integral') == 'Pendente' else 1, key=f"int_{p['id']}")
            st_ent = c2.selectbox("Entrada 50%", ["Pendente", "Recebido"], index=0 if p.get('status_entrada') == 'Pendente' else 1, key=f"ent_{p['id']}")
            st_fin = c3.selectbox("Final 50%", ["Pendente", "Recebido"], index=0 if p.get('status_final') == 'Pendente' else 1, key=f"fin_{p['id']}")
            
            b1, b2, b3, b4 = st.columns(4)
            if b1.button("🔄 ATUALIZAR", key=f"upd_{p['id']}"):
                supabase.table("projetos").update({"status_integral": st_int, "status_entrada": st_ent, "status_final": st_fin}).eq("id", p['id']).execute()
                st.rerun()
            
            pdf_orc = gerar_pdf_projeto(p, config, "ORÇAMENTO")
            if pdf_orc: b2.download_button("📄 PDF", pdf_orc, f"Orcamento_{p['id']}.pdf", "application/pdf", key=f"pdf_{p['id']}")
            
            pdf_rec = gerar_pdf_projeto(p, config, "RECIBO")
            if pdf_rec: b3.download_button("🧾 RECIBO", pdf_rec, f"Recibo_{p['id']}.pdf", "application/pdf", key=f"rec_{p['id']}")
            
            if b4.button("🗑️ EXCLUIR", key=f"del_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute()
                st.rerun()

with tabs[1]:
    with st.form("novo_job"):
        n_p = st.text_input("Nome do Projeto")
        c_p = st.text_input("Nome do Cliente")
        d_p = st.text_area("Descrição")
        v_p = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        if st.form_submit_button("SALVAR"):
            if n_p and c_p:
                supabase.table("projetos").insert({"nome_projeto": n_p, "cliente": c_p, "descricao": d_p, "valor_total": v_p, "status_integral": "Pendente", "status_entrada": "Pendente", "status_final": "Pendente"}).execute()
                st.success("Salvo!")
                st.rerun()

with tabs[2]:
    with st.form("conf"):
        n_e = st.text_input("Empresa", value=config.get('nome_empresa', ''))
        cj_e = st.text_input("CNPJ", value=config.get('cnpj', ''))
        zp_e = st.text_input("WhatsApp", value=config.get('whatsapp', ''))
        ml_e = st.text_input("E-mail", value=config.get('email', ''))
        ed_e = st.text_input("Endereço", value=config.get('endereco', ''))
        if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
            supabase.table("configuracoes").update({"nome_empresa": n_e, "cnpj": cj_e, "whatsapp": zp_e, "email": ml_e, "endereco": ed_e}).eq("id", 1).execute()
            st.success("Configurações Blindadas!")
            st.rerun()
