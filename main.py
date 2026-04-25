import streamlit as st
from supabase import create_client
import pandas as pd

# --- CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="PJ STUDIO DESIGN | PRO", layout="wide", page_icon="⚜️")

# --- DESIGN PREMIUM PJ GOLD (ESTRUTURA BLINDADA) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #1a1c23 !important; border-right: 2px solid #d4af37; }
    h1, h2, h3, p, label { color: #d4af37 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { 
        background-color: #d4af37 !important; color: #000000 !important; 
        font-weight: bold !important; border-radius: 8px !important; width: 100%;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
        background-color: #1a1c23 !important; color: white !important; border: 1px solid #d4af37 !important;
    }
    div[data-testid="metric-container"] {
        background-color: #1a1c23; border: 1px solid #d4af37; padding: 20px; border-radius: 10px;
    }
    div[data-testid="stMetricValue"] { color: #d4af37 !important; }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO DIRETA E SEGURA ---
URL_SUPA = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY_SUPA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtcmpnZXVrcXVleXl4emhicHJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODEzODAsImV4cCI6MjA5MjA1NzM4MH0.zEk_qYIvErts5aO9fJ6EL6ZU--Pm7woqugCfW3i0yyY"

try:
    supabase = create_client(URL_SUPA, KEY_SUPA)
except:
    st.error("Erro na comunicação com o banco de dados.")

# --- MENU LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1063/1063231.png", width=80)
    st.markdown("## ⚜️ MENU PJ STUDIO")
    pagina = st.radio("Ir para:", ["Painel", "Novo Job / Orçamento", "Gestão de Projetos", "Configurações"])

# --- PÁGINA: PAINEL (EXIBINDO 0,00 POR PADRÃO) ---
if pagina == "Painel":
    st.title("⚜️ Painel de Controle | PJ Studio")
    st.markdown("---")
    
    pago = 0.0
    pendente = 0.0
    
    try:
        res = supabase.table("projetos").select("valor, financeiro").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
            pago = df[df['financeiro'] == 'Pago']['valor'].sum()
            pendente = df[df['financeiro'] == 'Pendente']['valor'].sum()
    except:
        pass # Mantém 0,00 se houver erro ou banco vazio

    c1, c2 = st.columns(2)
    with c1:
        st.metric("💰 DINHEIRO NO BOLSO", f"R$ {pago:,.2f}")
    with c2:
        st.metric("⏳ CONTAS A RECEBER", f"R$ {pendente:,.2f}")

# --- PÁGINA: NOVO JOB (WHATSAPP E E-MAIL SEPARADOS) ---
elif pagina == "Novo Job / Orçamento":
    st.title("📝 Novo Registro Completo")
    with st.form("form_final_ajustado"):
        col_left, col_right = st.columns(2)
        with col_left:
            nome = st.text_input("Nome do Cliente / Empresa")
            doc = st.text_input("CPF ou CNPJ")
            whatsapp = st.text_input("WhatsApp")
            email = st.text_input("E-mail")
        with col_right:
            valor = st.number_input("Valor do Serviço (R$)", min_value=0.0)
            prazo = st.text_input("Prazo de Entrega (Ex: 10 dias)")
            status = st.selectbox("Status de Pagamento", ["Pendente", "Pago"])
            servico = st.text_input("Descrição Curta do Serviço")
        
        exigencias = st.text_area("Exigências Detalhadas")
        
        if st.form_submit_button("CADASTRAR E SALVAR ⚜️"):
            try:
                # Salva Cliente (WhatsApp e Email juntos no campo contato para compatibilidade)
                contato_full = f"WA: {whatsapp} | Email: {email}"
                supabase.table("clientes").insert({"nome": nome, "contato": contato_full, "documento": doc}).execute()
                # Salva Projeto
                supabase.table("projetos").insert({
                    "nome": nome, "valor": valor, "financeiro": status,
                    "descricao": f"{servico} | {exigencias}", "prazo": prazo
                }).execute()
                st.success(f"✅ Projeto de {nome} salvo com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# --- PÁGINA: GESTÃO ---
elif pagina == "Gestão de Projetos":
    st.title("⚙️ Gestão & Edição")
    try:
        res = supabase.table("projetos").select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"📌 {row['nome']} - R$ {row['valor']}"):
                    st.write(f"**Prazo:** {row.get('prazo', 'N/A')}")
                    st.write(f"**Descrição:** {row.get('descricao', 'N/A')}")
                    new_status = st.selectbox("Mudar Status", ["Pendente", "Pago"], 
                                           index=0 if row['financeiro']=='Pendente' else 1, key=f"ed_{row['id']}")
                    if st.button("Atualizar", key=f"bt_{row['id']}"):
                        supabase.table("projetos").update({"financeiro": new_status}).eq("id", row['id']).execute()
                        st.rerun()
    except:
        st.write("Nenhum projeto encontrado.")

# --- PÁGINA: CONFIGURAÇÕES ---
elif pagina == "Configurações":
    st.title("🛠️ Configurações PJ GOLD")
    st.write("Sistema Blindado v3.3")
    st.write("Banco de Dados: **Conectado**")
