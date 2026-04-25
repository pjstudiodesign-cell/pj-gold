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
    st.error("Erro de conexão com o banco de dados.")
    st.stop()

# --- CSS PRETO E OURO (IDENTIDADE PJ STUDIO - BLOQUEADO PARA ALTERAÇÕES) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #121212 !important; border-right: 2px solid #D4AF37 !important; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p { color: #D4AF37 !important; font-weight: bold !important; font-size: 1.1rem !important; }
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800 !important; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.8rem !important; font-weight: bold; }
    div[data-testid="stMetric"] { background-color: #1c1c1c; padding: 25px; border-radius: 15px; border: 2px solid #D4AF37; }
    .stButton>button { background-color: #D4AF37 !important; color: black !important; font-weight: bold !important; border-radius: 10px !important; height: 45px; width: 100%; }
    input, textarea, div[data-baseweb="select"] { background-color: #1c1c1c !important; color: white !important; border: 1px solid #444 !important; }
    label { color: #D4AF37 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data, conf.data[0] if conf.data else {}
    except Exception: return [], {}

# --- NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("## ⚜️ PJ STUDIO")
    st.write("---")
    menu = st.radio("NAVEGAÇÃO", ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"], label_visibility="collapsed")

# --- TELAS ---
if menu == "PAINEL":
    st.title("⚜️ PAINEL DE CONTROLE")
    projetos, _ = carregar_dados()
    no_bolso = sum([float(p.get('valor_total', 0)) for p in projetos if p.get('status_integral') == 'Recebido'])
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
        c_mail = st.text_input("E-mail do Cliente")
        c_end = st.text_area("Endereço do Cliente")
        st.write("---")
        st.subheader("Detalhes do Serviço")
        p_nome = st.text_input("Nome do Projeto")
        col3, col4 = st.columns(2)
        p_valor = col3.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
        p_prazo = col4.text_input("Prazo de Entrega")
        p_desc = st.text_area("Descrição do Serviço")
        p_exig = st.text_area("Exigências Específicas") # CAMPO RECUPERADO
        
        if st.form_submit_button("SALVAR ORÇAMENTO"):
            if c_nome and p_nome:
                dados = {
                    "cliente": c_nome, "cpf_cnpj": c_doc, "whatsapp_cliente": c_zap,
                    "email_cliente": c_mail, "endereco": c_end, "nome_projeto": p_nome,
                    "valor_total": p_valor, "prazo": p_prazo, "descricao": p_desc, "exigencias": p_exig
                }
                try:
                    supabase.table("projetos").insert(dados).execute()
                    st.success("✅ Orçamento salvo na nuvem!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.warning("Preencha Nome do Cliente e do Projeto.")

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO DE PROJETOS")
    projetos, _ = carregar_dados()
    if not projetos: st.info("Nenhum projeto registrado.")
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | {p.get('cliente')}"):
            st.write(f"**WhatsApp:** {p.get('whatsapp_cliente')} | **Valor:** R$ {p.get('valor_total')}")
            if st.button("🗑️ EXCLUIR", key=f"del_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute()
                st.rerun()

elif menu == "CONFIGURAÇOES":
    st.title("⚙️ DADOS DA MINHA EMPRESA")
    _, config = carregar_dados()
    with st.form("cfg_completa"):
        n_emp = st.text_input("Nome da Empresa", value=config.get('nome_empresa', ''))
        c_emp = st.text_input("CPF ou CNPJ da Empresa", value=config.get('cpf_cnpj', ''))
        col5, col6 = st.columns(2)
        w_emp = col5.text_input("WhatsApp Profissional", value=config.get('whatsapp', ''))
        e_emp = col6.text_input("E-mail Profissional", value=config.get('email', ''))
        end_emp = st.text_area("Endereço Completo", value=config.get('endereco', ''))
        
        if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
            try:
                supabase.table("configuracoes").update({
                    "nome_empresa": n_emp, "cpf_cnpj": c_emp, "whatsapp": w_emp, "email": e_emp, "endereco": end_emp
                }).eq("id", 1).execute()
                st.success("✅ Configurações atualizadas!")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
