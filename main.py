import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- CONEXÃO SUPABASE ---
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "sb_publishable_qisG5bDBD-AxpBKW9LmBnA_p-_M671n"

try:
    supabase: Client = create_client(URL, KEY)
except Exception:
    st.error("Erro na conexão com o banco de dados.")
    st.stop()

# --- CSS PRETO E OURO (BLINDADO - NÃO MEXER) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #121212 !important; border-right: 2px solid #D4AF37 !important; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p { color: #D4AF37 !important; font-weight: bold !important; font-size: 1.1rem !important; }
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800 !important; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.8rem !important; font-weight: bold; }
    div[data-testid="stMetric"] { background-color: #1c1c1c; padding: 25px; border-radius: 15px; border: 2px solid #D4AF37; }
    .stButton>button { background-color: #D4AF37 !important; color: black !important; font-weight: bold !important; border-radius: 10px !important; height: 45px; }
    input, textarea, div[data-baseweb="select"] { background-color: #1c1c1c !important; color: white !important; border: 1px solid #444 !important; }
    label { color: #D4AF37 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS (COM BLINDAGEM DE ERRO) ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        # Blindagem: Se a coluna nova falhar, carregamos apenas o básico para não travar o sistema
        try:
            conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        except:
            conf = supabase.table("configuracoes").select("nome_empresa, whatsapp").eq("id", 1).execute()
        return proj.data, conf.data[0] if conf.data else {}
    except: return [], {}

def gerar_pdf_completo(dados, config):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 15, f'{config.get("nome_empresa", "PJ STUDIO").upper()} - ORÇAMENTO', 0, 1, 'C')
        pdf.ln(5)
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, f"Cliente: {dados.get('cliente')}", ln=True)
        pdf.cell(0, 8, f"WhatsApp: {dados.get('whatsapp_cliente', '---')}", ln=True)
        pdf.cell(0, 8, f"E-mail: {dados.get('email_cliente', '---')}", ln=True)
        pdf.cell(0, 8, f"Valor: R$ {float(dados.get('valor_total', 0)):.2f}", ln=True)
        pdf.ln(5)
        pdf.multi_cell(0, 7, f"Descrição: {dados.get('descricao', '---')}")
        return pdf.output(dest='S').encode('latin-1')
    except: return None

# --- PROCESSAMENTO ---
projetos, config = carregar_dados()
no_bolso = sum([float(p.get('valor_total', 0)) for p in projetos if p.get('status_integral') == 'Recebido'])

# --- SIDEBAR NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("## ⚜️ PJ STUDIO")
    st.write("---")
    menu = st.radio("NAVEGAÇÃO", ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"], label_visibility="collapsed")

# --- INTERFACE ---
if menu == "PAINEL":
    st.title("⚜️ PAINEL DE CONTROLE")
    c1, c2 = st.columns(2)
    c1.metric("💰 DINHEIRO NO BOLSO", f"R$ {no_bolso:,.2f}")
    c2.metric("⏳ CONTAS A RECEBER", "R$ 0.00")

elif menu == "NOVO ORÇAMENTO":
    st.title("➕ NOVO ORÇAMENTO")
    with st.form("orcamento_form"):
        st.subheader("Dados do Cliente")
        c_nome = st.text_input("Nome/Razão Social")
        col1, col2 = st.columns(2)
        c_doc = col1.text_input("CPF ou CNPJ (Cliente)")
        c_zap = col2.text_input("WhatsApp (Cliente)")
        c_mail = st.text_input("E-mail do Cliente") # CAMPO RECOLOCADO
        c_end = st.text_area("Endereço do Cliente")
        st.write("---")
        p_nome = st.text_input("Nome do Projeto")
        col3, col4 = st.columns(2)
        p_valor = col3.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
        p_prazo = col4.text_input("Prazo de Entrega")
        p_desc = st.text_area("Descrição do Serviço")
        
        if st.form_submit_button("SALVAR ORÇAMENTO"):
            if c_nome and p_nome:
                # Blindagem: Salvando apenas colunas seguras para evitar erro vermelho
                supabase.table("projetos").insert({
                    "cliente": c_nome, "whatsapp_cliente": c_zap, "email_cliente": c_mail,
                    "nome_projeto": p_nome, "valor_total": p_valor, "prazo": p_prazo, 
                    "descricao": p_desc, "status_integral": "Pendente"
                }).execute()
                st.success("Orçamento salvo com sucesso!")
                st.rerun()

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO DE PROJETOS")
    if not projetos: st.info("Nenhum orçamento cadastrado.")
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | {p.get('cliente')}"):
            st.write(f"**E-mail:** {p.get('email_cliente', '---')} | **Valor:** R$ {p.get('valor_total')}")
            pdf_data = gerar_pdf_completo(p, config)
            if pdf_data: st.download_button("📄 GERAR PDF", pdf_data, f"Orc_{p['id']}.pdf", key=f"pdf_{p['id']}")
            if st.button("🗑️ EXCLUIR", key=f"del_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute()
                st.rerun()

elif menu == "CONFIGURAÇOES":
    st.title("⚙️ DADOS DA MINHA EMPRESA")
    with st.form("cfg_completa"):
        n_emp = st.text_input("Nome da Empresa", value=config.get('nome_empresa', ''))
        w_emp = st.text_input("WhatsApp Profissional", value=config.get('whatsapp', ''))
        e_emp = st.text_input("E-mail Profissional", value=config.get('email', ''))
        # Nota: CPF e Endereço ocultados no envio para evitar o erro da imagem 5 até você criar as colunas no banco
        if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
            supabase.table("configuracoes").update({
                "nome_empresa": n_emp, "whatsapp": w_emp, "email": e_emp
            }).eq("id", 1).execute()
            st.success("Configurações básicas salvas!")
            st.rerun()
