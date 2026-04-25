import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- CONEXÃO SUPABASE (ESTRUTURA BLINDADA) ---
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "sb_publishable_qisG5bDBD-AxpBKW9LmBnA_p-_M671n"

try:
    supabase: Client = create_client(URL, KEY)
except Exception:
    st.error("Erro crítico na conexão. Verifique o banco de dados.")
    st.stop()

# --- CSS PRETO E OURO PREMIUM (ESTRUTURA PROTEGIDA) ---
st.markdown("""
    <style>
    /* Fundo Total */
    .stApp { 
        background-color: #0e1117; 
        color: #FFFFFF; 
    }
    
    /* Títulos em Ouro */
    h1, h2, h3, span { color: #D4AF37 !important; }
    
    /* Caixas de Métricas Ouro */
    div[data-testid="stMetricValue"] { 
        color: #D4AF37 !important; 
        font-size: 2.5rem !important; 
        font-weight: bold !important;
    }
    div[data-testid="stMetricLabel"] { 
        color: #FFFFFF !important; 
        font-size: 1.1rem !important;
    }
    div[data-testid="stMetric"] { 
        background-color: #1c1c1c; 
        padding: 25px; 
        border-radius: 15px; 
        border: 2px solid #D4AF37; 
        box-shadow: 0px 4px 20px rgba(212, 175, 55, 0.15);
    }
    
    /* Botões Ouro Profissional */
    .stButton>button { 
        background-color: #D4AF37 !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        border-radius: 10px !important; 
        border: none !important;
        height: 45px !important;
        transition: 0.3s all ease;
    }
    .stButton>button:hover { 
        background-color: #F5D76E !important; 
        box-shadow: 0px 0px 15px rgba(212, 175, 55, 0.4);
    }
    
    /* Abas do Menu */
    button[data-baseweb="tab"] { 
        color: #FFFFFF !important; 
        font-size: 1.1rem !important;
    }
    button[aria-selected="true"] { 
        color: #D4AF37 !important; 
        border-bottom-color: #D4AF37 !important; 
    }
    
    /* Expanders de Projetos */
    div[data-testid="stExpander"] { 
        border: 1px solid #D4AF37 !important; 
        background-color: #121212 !important; 
        border-radius: 10px !important;
        margin-bottom: 15px !important;
    }

    /* Estilização de Inputs */
    input, textarea, div[data-baseweb="select"] { 
        background-color: #1c1c1c !important; 
        color: white !important; 
        border: 1px solid #444 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DOCUMENTOS (PDF/RECIBO) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(212, 175, 55) # Ouro
        self.cell(0, 15, 'PJ STUDIO GOLD PRO - ORÇAMENTO', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_projeto(dados, config, tipo="ORÇAMENTO"):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Cabeçalho da Empresa
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, f"EMPRESA: {config.get('nome_empresa', 'PJ STUDIO')}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"CNPJ: {config.get('cnpj', '---')}", ln=True)
        pdf.cell(0, 8, f"WHATSAPP: {config.get('whatsapp', '---')}", ln=True)
        pdf.cell(0, 8, f"E-MAIL: {config.get('email', '---')}", ln=True)
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
        
        # Detalhes do Job
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"DOCUMENTO: {tipo}", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"CLIENTE: {dados.get('cliente', '---')}", ln=True)
        pdf.cell(0, 10, f"PROJETO: {dados.get('nome_projeto', '---')}", ln=True)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"VALOR TOTAL: R$ {float(dados.get('valor_total', 0)):.2f}", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'I', 11)
        pdf.multi_cell(0, 8, f"DESCRIÇÃO DO SERVIÇO: {dados.get('descricao', '---')}")
        
        return pdf.output(dest='S').encode('latin-1')
    except:
        return None

# --- LÓGICA DE DADOS (SUPABASE) ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data, conf.data[0] if conf.data else {}
    except:
        return [], {}

projetos, config = carregar_dados()

# Métricas Financeiras Blindadas
no_bolso = 0
a_receber = 0
for p in projetos:
    try:
        v = float(p.get('valor_total', 0))
        if p.get('status_integral') == 'Recebido': 
            no_bolso += v
        else:
            # Lógica 50% Entrada
            if p.get('status_entrada') == 'Recebido': no_bolso += (v * 0.5)
            else: a_receber += (v * 0.5)
            # Lógica 50% Final
            if p.get('status_final') == 'Recebido': no_bolso += (v * 0.5)
            else: a_receber += (v * 0.5)
    except:
        continue

# --- INTERFACE PRINCIPAL ---
st.title("⚜️ PJ STUDIO GOLD PRO")

col_m1, col_m2 = st.columns(2)
with col_m1:
    st.metric("💰 DINHEIRO NO BOLSO", f"R$ {no_bolso:,.2f}")
with col_m2:
    st.metric("⏳ CONTAS A RECEBER", f"R$ {a_receber:,.2f}")

st.write("---")

tabs = st.tabs(["📋 GESTÃO DE PROJETOS", "➕ NOVO JOB", "⚙️ CONFIGURAÇÕES"])

# TABELA DE PROJETOS
with tabs[0]:
    if not projetos:
        st.info("Nenhum projeto registrado.")
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | CLIENTE: {p.get('cliente')}"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st_int = st.selectbox("Status Integral", ["Pendente", "Recebido"], index=0 if p.get('status_integral') == 'Pendente' else 1, key=f"int_{p['id']}")
            with c2:
                st_ent = st.selectbox("Entrada (50%)", ["Pendente", "Recebido"], index=0 if p.get('status_entrada') == 'Pendente' else 1, key=f"ent_{p['id']}")
            with c3:
                st_fin = st.selectbox("Final (50%)", ["Pendente", "Recebido"], index=0 if p.get('status_final') == 'Pendente' else 1, key=f"fin_{p['id']}")
            
            st.write("")
            b1, b2, b3, b4 = st.columns(4)
            
            if b1.button("🔄 ATUALIZAR", key=f"btn_upd_{p['id']}"):
                supabase.table("projetos").update({"status_integral": st_int, "status_entrada": st_ent, "status_final": st_fin}).eq("id", p['id']).execute()
                st.rerun()
            
            pdf_orc = gerar_pdf_projeto(p, config, "ORÇAMENTO")
            if pdf_orc:
                b2.download_button("📄 GERAR PDF", pdf_orc, f"Orcamento_{p['id']}.pdf", "application/pdf", key=f"btn_pdf_{p['id']}")
            
            pdf_rec = gerar_pdf_projeto(p, config, "RECIBO")
            if pdf_rec:
                b3.download_button("🧾 GERAR RECIBO", pdf_rec, f"Recibo_{p['id']}.pdf", "application/pdf", key=f"btn_rec_{p['id']}")
            
            if b4.button("🗑️ EXCLUIR", key=f"btn_del_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute()
                st.rerun()

# FORMULÁRIO DE NOVO JOB
with tabs[1]:
    with st.form("form_novo_job", clear_on_submit=True):
        st.subheader("Cadastrar Novo Serviço")
        col_f1, col_f2 = st.columns(2)
        n_p = col_f1.text_input("Nome do Projeto")
        c_p = col_f2.text_input("Nome do Cliente")
        d_p = st.text_area("Descrição Detalhada do Serviço")
        v_p = st.number_input("Valor Total do Orçamento (R$)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("SALVAR PROJETO NO SISTEMA"):
            if n_p and c_p:
                supabase.table("projetos").insert({
                    "nome_projeto": n_p, 
                    "cliente": c_p, 
                    "descricao": d_p, 
                    "valor_total": v_p,
                    "status_integral": "Pendente",
                    "status_entrada": "Pendente",
                    "status_final": "Pendente"
                }).execute()
                st.success("Projeto salvo com sucesso!")
                st.rerun()
            else:
                st.warning("Preencha o Nome do Projeto e do Cliente.")

# CONFIGURAÇÕES DA EMPRESA
with tabs[2]:
    with st.form("form_config"):
        st.subheader("Configurações de Identidade da Empresa")
        n_e = st.text_input("Nome da Empresa", value=config.get('nome_empresa', ''))
        cj_e = st.text_input("CNPJ", value=config.get('cnpj', ''))
        zp_e = st.text_input("WhatsApp para Contato", value=config.get('whatsapp', ''))
        ml_e = st.text_input("E-mail Profissional", value=config.get('email', ''))
        ed_e = st.text_input("Endereço Físico/Comercial", value=config.get('endereco', ''))
        
        if st.form_submit_button("SALVAR E BLINDAR CONFIGURAÇÕES"):
            supabase.table("configuracoes").update({
                "nome_empresa": n_e, 
                "cnpj": cj_e, 
                "whatsapp": zp_e, 
                "email": ml_e, 
                "endereco": ed_e
            }).eq("id", 1).execute()
            st.success("Configurações atualizadas no banco de dados!")
            st.rerun()
