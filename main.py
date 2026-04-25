import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- CONEXÃO SUPABASE ---
URL = "SUA_URL_AQUI"
KEY = "SUA_KEY_AQUI"
supabase: Client = create_client(URL, KEY)

# --- CSS CUSTOMIZADO (PRETO E DOURADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; width: 100%; border-radius: 5px; }
    .stMetric { background-color: #1c1c1c; padding: 15px; border-radius: 10px; border: 1px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(212, 175, 55) # Dourado
        self.cell(0, 10, 'PJ STUDIO GOLD PRO - ORÇAMENTO', 0, 1, 'C')
        self.ln(10)

def gerar_pdf_projeto(dados, config, tipo="ORÇAMENTO"):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    
    # Dados da Empresa (Vindos das Configurações)
    pdf.cell(0, 10, f"Empresa: {config['nome_empresa']}", ln=True)
    pdf.cell(0, 10, f"CNPJ: {config['cnpj']} | WhatsApp: {config['whatsapp']}", ln=True)
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Dados do Projeto
    pdf.cell(0, 10, f"Documento: {tipo}", ln=True)
    pdf.cell(0, 10, f"Cliente: {dados['cliente']}", ln=True)
    pdf.cell(0, 10, f"Serviço: {dados['nome_projeto']}", ln=True)
    pdf.cell(0, 10, f"Valor Total: R$ {dados['valor_total']:.2f}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Descrição: {dados['descricao']}")
    
    return pdf.output(dest='S').encode('latin-1')

# --- LÓGICA DE NEGÓCIO / PAINEL ---
def carregar_dados():
    proj = supabase.table("projetos").select("*").execute()
    conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
    return proj.data, conf.data[0] if conf.data else {}

projetos, config = carregar_dados()

# Cálculo das Métricas
no_bolso = 0
a_receber = 0
for p in projetos:
    v = float(p['valor_total'])
    # Lógica 50/50
    if p['status_integral'] == 'Recebido': no_bolso += v
    else:
        if p['status_entrada'] == 'Recebido': no_bolso += (v * 0.5)
        else: a_receber += (v * 0.5)
        
        if p['status_final'] == 'Recebido': no_bolso += (v * 0.5)
        else: a_receber += (v * 0.5)

# --- INTERFACE ---
st.title("⚜️ PJ STUDIO GOLD PRO")

col1, col2 = st.columns(2)
col1.metric("💰 DINHEIRO NO BOLSO", f"R$ {no_bolso:,.2f}")
col2.metric("⏳ CONTAS A RECEBER", f"R$ {a_receber:,.2f}")

tabs = st.tabs(["📋 Gestão de Projetos", "➕ Novo Job", "⚙️ Configurações"])

with tabs[0]:
    for p in projetos:
        with st.expander(f"Projeto: {p['nome_projeto']} - Cliente: {p['cliente']}"):
            c1, c2, c3 = st.columns(3)
            st_int = c1.selectbox("Integral", ["Pendente", "Recebido"], index=0 if p['status_integral'] == 'Pendente' else 1, key=f"int_{p['id']}")
            st_ent = c2.selectbox("Entrada 50%", ["Pendente", "Recebido"], index=0 if p['status_entrada'] == 'Pendente' else 1, key=f"ent_{p['id']}")
            st_fin = c3.selectbox("Final 50%", ["Pendente", "Recebido"], index=0 if p['status_final'] == 'Pendente' else 1, key=f"fin_{p['id']}")
            
            b1, b2, b3, b4 = st.columns(4)
            if b1.button("🔄 ATUALIZAR", key=f"upd_{p['id']}"):
                supabase.table("projetos").update({
                    "status_integral": st_int, "status_entrada": st_ent, "status_final": st_fin
                }).eq("id", p['id']).execute()
                st.rerun()
            
            # Botão PDF Orçamento
            pdf_orc = gerar_pdf_projeto(p, config, "ORÇAMENTO")
            b2.download_button("📄 PDF ORÇAMENTO", pdf_orc, f"Orcamento_{p['id']}.pdf", "application/pdf", key=f"pdf_{p['id']}")
            
            # Botão Recibo
            pdf_rec = gerar_pdf_projeto(p, config, "RECIBO")
            b3.download_button("🧾 GERAR RECIBO", pdf_rec, f"Recibo_{p['id']}.pdf", "application/pdf", key=f"rec_{p['id']}")
            
            if b4.button("🗑️ EXCLUIR", key=f"del_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute()
                st.rerun()

with tabs[1]:
    with st.form("novo_job"):
        nome_p = st.text_input("Nome do Projeto")
        cliente_p = st.text_input("Nome do Cliente")
        desc_p = st.text_area("Descrição do Serviço")
        valor_p = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
        if st.form_submit_button("SALVAR PROJETO"):
            supabase.table("projetos").insert({
                "nome_projeto": nome_p, "cliente": cliente_p, 
                "descricao": desc_p, "valor_total": valor_p
            }).execute()
            st.success("Projeto salvo com sucesso!")
            st.rerun()

with tabs[2]:
    st.subheader("Configurações da Empresa")
    with st.form("conf_empresa"):
        n_emp = st.text_input("Nome da Empresa", value=config.get('nome_empresa', ''))
        cnpj_emp = st.text_input("CNPJ", value=config.get('cnpj', ''))
        zap_emp = st.text_input("WhatsApp", value=config.get('whatsapp', ''))
        mail_emp = st.text_input("E-mail", value=config.get('email', ''))
        end_emp = st.text_input("Endereço", value=config.get('endereco', ''))
        
        if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
            supabase.table("configuracoes").update({
                "nome_empresa": n_emp, "cnpj": cnpj_emp, 
                "whatsapp": zap_emp, "email": mail_emp, "endereco": end_emp
            }).eq("id", 1).execute()
            st.success("Configurações atualizadas!")
            st.rerun()
