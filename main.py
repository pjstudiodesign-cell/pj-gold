import streamlit as st
from supabase import create_client
import pandas as pd

# --- CONFIGURAÇÃO DE PÁGINA (ESTILO PREMIUM) ---
st.set_page_config(page_title="PJ STUDIO DESIGN | PRO", layout="wide", page_icon="⚜️")

# --- O DESIGN DO CHEFE (PRETO E DOURADO) ---
st.markdown("""
    <style>
    /* Fundo principal */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Menu Lateral */
    section[data-testid="stSidebar"] { background-color: #1a1c23 !important; border-right: 2px solid #d4af37; }
    
    /* Títulos e Textos Dourados */
    h1, h2, h3, p, label { color: #d4af37 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Botões Dourados com texto preto */
    .stButton>button { 
        background-color: #d4af37 !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        border-radius: 8px !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #f1c40f !important; transform: scale(1.02); }
    
    /* Inputs (Caixas de texto) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
        background-color: #1a1c23 !important;
        color: white !important;
        border: 1px solid #d4af37 !important;
    }
    
    /* Cards de Informação */
    div[data-testid="stMetricValue"] { color: #d4af37 !important; }
    .stAlert { background-color: #1a1c23 !important; border: 1px solid #d4af37 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO DIRETA (MANTENDO O QUE FUNCIONOU) ---
URL_SUPA = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY_SUPA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtcmpnZXVrcXVleXl4emhicHJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODEzODAsImV4cCI6MjA5MjA1NzM4MH0.zEk_qYIvErts5aO9fJ6EL6ZU--Pm7woqugCfW3i0yyY"

try:
    supabase = create_client(URL_SUPA, KEY_SUPA)
except:
    st.error("Erro na conexão.")

# --- MENU LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1063/1063231.png", width=80) # Ícone de Coroa/Flor de Lis
    st.markdown("## ⚜️ PJ STUDIO")
    pagina = st.radio("Navegação:", ["🏛️ Painel Geral", "📝 Novo Job / Orçamento", "⚙️ Gestão & Edição"])

# --- PÁGINA: PAINEL ---
if pagina == "🏛️ Painel Geral":
    st.title("⚜️ Painel de Controle | PJ Studio")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    try:
        res_proj = supabase.table("projetos").select("valor, financeiro").execute()
        if res_proj.data:
            df_proj = pd.DataFrame(res_proj.data)
            total_bolso = df_proj[df_proj['financeiro'] == 'Pago']['valor'].sum()
            total_receber = df_proj[df_proj['financeiro'] == 'Pendente']['valor'].sum()
            with col1:
                st.metric("DINHEIRO NO BOLSO", f"R$ {total_bolso:,.2f}")
            with col2:
                st.metric("CONTAS A RECEBER", f"R$ {total_receber:,.2f}")
    except:
        st.info("Aguardando lançamentos para calcular o financeiro.")

# --- PÁGINA: NOVO JOB ---
elif pagina == "📝 Novo Job / Orçamento":
    st.title("📝 Novo Registro")
    with st.form("form_job"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Cliente / Empresa")
            doc = st.text_input("CPF ou CNPJ")
        with c2:
            contato = st.text_input("WhatsApp / E-mail")
            valor = st.number_input("Valor do Serviço (R$)", min_value=0.0)
        
        servico = st.text_area("Descrição dos Serviços")
        status = st.selectbox("Status de Pagamento", ["Pendente", "Pago"])
        
        if st.form_submit_button("CADASTRAR PROJETO ⚜️"):
            supabase.table("clientes").insert({"nome": nome, "contato": contato, "documento": doc}).execute()
            supabase.table("projetos").insert({"nome": nome, "valor": valor, "financeiro": status}).execute()
            st.success(f"✅ {nome} adicionado com sucesso!")

# --- PÁGINA: GESTÃO ---
elif pagina == "⚙️ Gestão & Edição":
    st.title("⚙️ Gestão de Projetos")
    res = supabase.table("projetos").select("*").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        for _, row in df.iterrows():
            with st.expander(f"📦 ID: {row['id']} | {row['nome']} | R$ {row['valor']}"):
                u_nome = st.text_input("Editar Cliente", row['nome'], key=f"n_{row['id']}")
                u_valor = st.number_input("Editar Valor", float(row['valor']), key=f"v_{row['id']}")
                u_status = st.selectbox("Mudar Status", ["Pendente", "Pago"], 
                                     index=0 if row['financeiro']=='Pendente' else 1, 
                                     key=f"s_{row['id']}")
                
                if st.button("SALVAR ALTERAÇÕES", key=f"btn_{row['id']}"):
                    supabase.table("projetos").update({"nome": u_nome, "valor": u_valor, "financeiro": u_status}).eq("id", row['id']).execute()
                    st.success("Atualizado!")
                    st.rerun()
    else:
        st.write("Nenhum projeto cadastrado.")
