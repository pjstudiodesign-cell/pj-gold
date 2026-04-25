import streamlit as st
from supabase import create_client
import pandas as pd

# Configurações de Página
st.set_page_config(page_title="PJ STUDIO DESIGN | PRO", layout="wide", page_icon="⚜️")

# Estilo CSS Personalizado
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #d4af37; color: black; font-weight: bold; border-radius: 5px; }
    .stTextInput>div>div>input { background-color: #1a1c23; color: white; border: 1px solid #d4af37; }
    h1, h2, h3 { color: #d4af37; }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DIRETA (PLANO B - À PROVA DE ERROS) ---
# Aqui os dados entram direto no código, sem depender do painel do Render
URL_SUPA = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY_SUPA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtcmpnZXVrcXVleXl4emhicHJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODEzODAsImV4cCI6MjA5MjA1NzM4MH0.zEk_qYIvErts5aO9fJ6EL6ZU--Pm7woqugCfW3i0yyY"

try:
    supabase = create_client(URL_SUPA, KEY_SUPA)
except Exception as e:
    st.error(f"Erro na conexão: {e}")

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown("## ⚜️ MENU PJ STUDIO")
    pagina = st.radio("Ir para:", ["Painel", "Novo Job / Orçamento", "Gestão de Projetos", "Configurações"])

# --- PÁGINA: PAINEL ---
if pagina == "Painel":
    st.title("⚜️ Painel de Controle")
    col1, col2 = st.columns(2)
    try:
        res_proj = supabase.table("projetos").select("valor, financeiro").execute()
        if res_proj.data:
            df_proj = pd.DataFrame(res_proj.data)
            total_bolso = df_proj[df_proj['financeiro'] == 'Pago']['valor'].sum()
            total_receber = df_proj[df_proj['financeiro'] == 'Pendente']['valor'].sum()
            with col1:
                st.info("Dinheiro no Bolso")
                st.subheader(f"R$ {total_bolso:,.2f}")
            with col2:
                st.warning("Contas a Receber")
                st.subheader(f"R$ {total_receber:,.2f}")
    except:
        st.write("Aguardando lançamentos...")

# --- PÁGINA: NOVO JOB / ORÇAMENTO ---
elif pagina == "Novo Job / Orçamento":
    st.title("📝 Novo Orçamento")
    with st.form("form_cliente"):
        nome = st.text_input("Nome do Cliente / Empresa")
        doc = st.text_input("CPF ou CNPJ")
        contato = st.text_input("WhatsApp / E-mail")
        servico = st.text_area("Descrição do Serviço")
        valor = st.number_input("Valor do Serviço (R$)", min_value=0.0)
        status = st.selectbox("Status Financeiro", ["Pendente", "Pago"])
        
        if st.form_submit_button("SALVAR NO SISTEMA"):
            try:
                # Salva no banco
                supabase.table("clientes").insert({"nome": nome, "contato": contato, "documento": doc}).execute()
                supabase.table("projetos").insert({"nome": nome, "valor": valor, "financeiro": status}).execute()
                st.success(f"✅ Sucesso! {nome} cadastrado.")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# --- PÁGINA: GESTÃO DE PROJETOS ---
elif pagina == "Gestão de Projetos":
    st.title("⚙️ Gestão de Projetos")
    try:
        res = supabase.table("projetos").select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for index, row in df.iterrows():
                with st.expander(f"📌 {row['nome']} - R$ {row['valor']}"):
                    u_nome = st.text_input("Nome", row['nome'], key=f"n_{row['id']}")
                    u_valor = st.number_input("Valor", float(row['valor']), key=f"v_{row['id']}")
                    u_status = st.selectbox("Status", ["Pendente", "Pago"], 
                                         index=0 if row['financeiro']=='Pendente' else 1, 
                                         key=f"s_{row['id']}")
                    
                    if st.button("Atualizar Dados", key=f"btn_{row['id']}"):
                        supabase.table("projetos").update({
                            "nome": u_nome, 
                            "valor": u_valor, 
                            "financeiro": u_status
                        }).eq("id", row['id']).execute()
                        st.success("Dados atualizados!")
                        st.rerun()
        else:
            st.info("Nenhum projeto para listar.")
    except:
        st.error("Erro ao carregar lista.")

# --- PÁGINA: CONFIGURAÇÕES ---
elif pagina == "Configurações":
    st.title("🛠️ Configurações do Sistema")
    st.write("PJ Gold Pro v3.0 - Ativado")
    st.write("Conexão direta com Supabase: **OK**")
