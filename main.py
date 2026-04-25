import streamlit as st
from supabase import create_client
import pandas as pd

# --- CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="PJ STUDIO DESIGN | PRO", layout="wide", page_icon="⚜️")

# --- DESIGN PREMIUM PJ GOLD (BLINDADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #1a1c23 !important; border-right: 2px solid #d4af37; }
    h1, h2, h3, p, label { color: #d4af37 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { 
        background-color: #d4af37 !important; color: #000000 !important; 
        font-weight: bold !important; border-radius: 8px !important; width: 100%;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input, .stDateInput>div>div>input {
        background-color: #1a1c23 !important; color: white !important; border: 1px solid #d4af37 !important;
    }
    div[data-testid="stMetricValue"] { color: #d4af37 !important; }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO DIRETA (ESTRUTURA DE SEGURANÇA) ---
URL_SUPA = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY_SUPA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtcmpnZXVrcXVleXl4emhicHJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODEzODAsImV4cCI6MjA5MjA1NzM4MH0.zEk_qYIvErts5aO9fJ6EL6ZU--Pm7woqugCfW3i0yyY"

try:
    supabase = create_client(URL_SUPA, KEY_SUPA)
except Exception as e:
    st.error(f"Erro Crítico de Conexão: {e}")

# --- MENU LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1063/1063231.png", width=80)
    st.markdown("## ⚜️ MENU PJ STUDIO")
    pagina = st.radio("Ir para:", ["Painel", "Novo Job / Orçamento", "Gestão de Projetos", "Configurações"])

# --- PÁGINA: PAINEL ---
if pagina == "Painel":
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
        st.info("Aguardando dados para análise financeira.")

# --- PÁGINA: NOVO JOB (CAMPOS CORRIGIDOS) ---
elif pagina == "Novo Job / Orçamento":
    st.title("📝 Novo Orçamento / Job")
    with st.form("form_job_completo"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Cliente / Empresa")
            doc = st.text_input("CPF ou CNPJ")
            contato = st.text_input("WhatsApp / E-mail")
        with c2:
            valor = st.number_input("Valor do Serviço (R$)", min_value=0.0)
            prazo = st.text_input("Prazo de Entrega (Ex: 5 dias úteis)")
            status = st.selectbox("Status de Pagamento", ["Pendente", "Pago"])
        
        # CAMPO DE EXIGÊNCIAS (O QUE O CLIENTE QUER)
        exigencias = st.text_area("Exigências do Cliente (Descrição Detalhada do Projeto)")
        
        if st.form_submit_button("CADASTRAR E BLINDAR JOB ⚜️"):
            try:
                # Salva dados do cliente
                supabase.table("clientes").insert({
                    "nome": nome, 
                    "contato": contato, 
                    "documento": doc
                }).execute()
                
                # Salva dados do projeto incluindo exigências e prazo
                supabase.table("projetos").insert({
                    "nome": nome, 
                    "valor": valor, 
                    "financeiro": status,
                    "descricao": exigencias,
                    "prazo": prazo
                }).execute()
                st.success(f"✅ Sucesso! Job para {nome} registrado com todos os detalhes.")
            except Exception as e:
                st.error(f"Erro ao salvar: Verifique se as colunas 'descricao' e 'prazo' existem no seu Supabase.")

# --- PÁGINA: GESTÃO ---
elif pagina == "Gestão de Projetos":
    st.title("⚙️ Gestão & Edição")
    try:
        res = supabase.table("projetos").select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"📌 {row['nome']} | Prazo: {row.get('prazo', 'N/A')}"):
                    u_valor = st.number_input("Editar Valor", float(row['valor']), key=f"v_{row['id']}")
                    u_status = st.selectbox("Status", ["Pendente", "Pago"], index=0 if row['financeiro']=='Pendente' else 1, key=f"s_{row['id']}")
                    if st.button("ATUALIZAR", key=f"btn_{row['id']}"):
                        supabase.table("projetos").update({"valor": u_valor, "financeiro": u_status}).eq("id", row['id']).execute()
                        st.rerun()
    except:
        st.error("Erro ao carregar lista de projetos.")

# --- PÁGINA: CONFIGURAÇÕES ---
elif pagina == "Configurações":
    st.title("🛠️ Configurações PJ GOLD")
    st.markdown("---")
    st.subheader("Informações do Sistema")
    st.write("Versão: 3.1 (Edição Cirúrgica)")
    st.write("Conexão Supabase: **ESTÁVEL**")
    st.write("Render Deployment: **ATIVO**")
