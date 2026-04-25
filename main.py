import streamlit as st
from supabase import create_client
import pandas as pd

# Configurações de Página
st.set_page_config(page_title="PJ STUDIO DESIGN | PRO", layout="wide", page_icon="⚜️")

# Estilo CSS Personalizado (Preto e Dourado)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #d4af37; color: black; font-weight: bold; border-radius: 5px; }
    .stTextInput>div>div>input { background-color: #1a1c23; color: white; border: 1px solid #d4af37; }
    .css-1d391kg { background-color: #0e1117; border-right: 1px solid #d4af37; }
    h1, h2, h3 { color: #d4af37; }
    </style>
""", unsafe_allow_html=True)

# Conexão Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown("## ⚜️ MENU REAL")
    pagina = st.radio("Ir para:", ["Painel", "Novo Job / Orçamento", "Gestão de Projetos", "Configurações"])

# --- PÁGINA: PAINEL ---
if pagina == "Painel":
    st.title("⚜️ PJ STUDIO DESIGN | Painel")
    
    col1, col2 = st.columns(2)
    
    # Busca dados para o painel
    res_proj = supabase.table("projetos").select("valor, financeiro").execute()
    df_proj = pd.DataFrame(res_proj.data)
    
    total_bolso = 0
    total_receber = 0
    
    if not df_proj.empty:
        total_bolso = df_proj[df_proj['financeiro'] == 'Pago']['valor'].sum()
        total_receber = df_proj[df_proj['financeiro'] == 'Pendente']['valor'].sum()

    with col1:
        st.info("Dinheiro no Bolso")
        st.subheader(f"R$ {total_bolso:,.2f}")
    with col2:
        st.warning("Contas a Receber")
        st.subheader(f"R$ {total_receber:,.2f}")

# --- PÁGINA: NOVO JOB / ORÇAMENTO ---
elif pagina == "Novo Job / Orçamento":
    st.title("📝 Novo Orçamento")
    
    with st.form("form_cliente"):
        nome = st.text_input("Nome do Cliente / Empresa")
        doc = st.text_input("CPF ou CNPJ")
        contato = st.text_input("WhatsApp / E-mail")
        servico = st.text_area("Descrição do Serviço")
        valor = st.number_input("Valor do Serviço (R$)", min_value=0.0)
        status = st.selectbox("Status Inicial", ["Pendente", "Pago"])
        
        btn_salvar = st.form_submit_button("SALVAR NO SISTEMA")
        
        if btn_salvar:
            # Salva Cliente
            res_c = supabase.table("clientes").insert({"nome": nome, "contato": contato, "documento": doc}).execute()
            # Salva Projeto/Orçamento
            res_p = supabase.table("projetos").insert({"nome": nome, "valor": valor, "financeiro": status}).execute()
            st.success(f"Orçamento de {nome} salvo com sucesso!")

# --- PÁGINA: GESTÃO DE PROJETOS (A MÁGICA DA EDIÇÃO) ---
elif pagina == "Gestão de Projetos":
    st.title("⚙️ Gestão e Edição")
    
    res = supabase.table("projetos").select("*").execute()
    df = pd.DataFrame(res.data)
    
    if df.empty:
        st.write("Nenhum projeto encontrado.")
    else:
        st.write("### Lista de Serviços Ativos")
        for index, row in df.iterrows():
            with st.expander(f"ID: {row['id']} | Cliente: {row['nome']} | R$ {row['valor']}"):
                new_nome = st.text_input("Editar Nome", row['nome'], key=f"n_{row['id']}")
                new_valor = st.number_input("Editar Valor", float(row['valor']), key=f"v_{row['id']}")
                new_status = st.selectbox("Status", ["Pendente", "Pago"], index=0 if row['financeiro']=='Pendente' else 1, key=f"s_{row['id']}")
                
                if st.button("Atualizar Dados", key=f"btn_{row['id']}"):
                    supabase.table("projetos").update({"nome": new_nome, "valor": new_valor, "financeiro": new_status}).eq("id", row['id']).execute()
                    st.success("Atualizado com sucesso! Atualize a página.")
                    st.rerun()

# --- PÁGINA: CONFIGURAÇÕES ---
elif pagina == "Configurações":
    st.title("🛠️ Configurações")
    st.write("Sistema PJ Gold Pro v2.0 - Banco de Dados Conectado.")
