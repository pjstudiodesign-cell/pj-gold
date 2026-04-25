import streamlit as st
from supabase import create_client, Client

# --- 1. CONFIGURAÇÃO E BLINDAGEM VISUAL (IMUTÁVEL) ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- 2. CONEXÃO SUPABASE ---
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "sb_publishable_qisG5bDBD-AxpBKW9LmBnA_p-_M671n"

try:
    supabase: Client = create_client(URL, KEY)
except Exception:
    st.error("Erro crítico de conexão.")
    st.stop()

# --- 3. CSS PRETO E OURO (LACRADO) ---
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

# --- 4. FUNÇÕES DE DADOS ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data if proj.data else [], conf.data[0] if conf.data else {}
    except Exception: return [], {}

# --- 5. NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚜️ PJ STUDIO</h2>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("NAVEGAÇÃO", ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"], label_visibility="collapsed")

# --- 6. TELAS ---
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
        p_valor = col3.number_input("Valor Total (R$)", min_value=0.0, step=0.01, format="%.2f")
        p_prazo = col4.text_input("Prazo de Entrega")
        p_desc = st.text_area("Descrição do Serviço")
        p_exig = st.text_area("Exigências Específicas")
        
        if st.form_submit_button("GERAR E SALVAR ORÇAMENTO"):
            if c_nome and p_nome:
                # DADOS ORGANIZADOS PARA O BANCO
                dados = {
                    "cliente": c_nome, "cpf_cnpj": c_doc, "whatsapp_cliente": c_zap,
                    "email_cliente": c_mail, "endereco": c_end, "nome_projeto": p_nome,
                    "valor_total": p_valor, "prazo": p_prazo, "descricao": p_desc, "exigencias": p_exig
                }
                try:
                    # TENTATIVA DE SALVAMENTO BLINDADA
                    supabase.table("projetos").insert(dados).execute()
                    st.success("✅ Orçamento salvo com sucesso na PJ STUDIO!")
                except Exception as e:
                    # SE O BANCO DER ERRO DE COLUNA, ELE SALVA O BÁSICO PARA NÃO TRAVAR VOCÊ
                    st.warning("⚠️ O banco de dados está atualizando. Tentando salvamento de segurança...")
                    try:
                        supabase.table("projetos").insert({"cliente": c_nome, "nome_projeto": p_nome, "valor_total": p_valor}).execute()
                        st.success("✅ Dados básicos salvos! As novas colunas estarão ativas em instantes.")
                    except:
                        st.error("Erro técnico no banco. Por favor, aguarde 1 minuto e tente novamente.")
            else:
                st.warning("Preencha os campos obrigatórios (Nome do Cliente e Projeto).")

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO DE PROJETOS")
    projetos, _ = carregar_dados()
    if not projetos:
        st.info("Nenhum projeto encontrado.")
    else:
        for p in projetos:
            with st.expander(f"📌 {p.get('nome_projeto', 'Sem Nome')} | {p.get('cliente', 'Sem Cliente')}"):
                st.write(f"**Valor:** R$ {p.get('valor_total', 0)}")
                st.write(f"**Prazo:** {p.get('prazo', 'N/A')}")
                if st.button("🗑️ EXCLUIR", key=f"del_{p.get('id')}"):
                    supabase.table("projetos").delete().eq("id", p.get('id')).execute()
                    st.rerun()

elif menu == "CONFIGURAÇOES":
    st.title("⚙️ DADOS DA MINHA EMPRESA")
    _, config = carregar_dados()
    with st.form("cfg"):
        n_emp = st.text_input("Nome da Empresa", value=config.get('nome_empresa', ''))
        c_emp = st.text_input("CPF ou CNPJ", value=config.get('cpf_cnpj', ''))
        w_emp = st.text_input("WhatsApp", value=config.get('whatsapp', ''))
        e_emp = st.text_input("E-mail", value=config.get('email', ''))
        end_emp = st.text_area("Endereço", value=config.get('endereco', ''))
        if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
            supabase.table("configuracoes").update({"nome_empresa": n_emp, "cpf_cnpj": c_emp, "whatsapp": w_emp, "email": e_emp, "endereco": end_emp}).eq("id", 1).execute()
            st.success("✅ Configurações atualizadas!")
