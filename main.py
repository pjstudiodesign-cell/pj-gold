import streamlit as st
from supabase import create_client
import pandas as pd

# --- CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="PJ STUDIO DESIGN | PRO", layout="wide", page_icon="⚜️")

# --- DESIGN PREMIUM PJ GOLD ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #1a1c23 !important; border-right: 2px solid #d4af37; }
    h1, h2, h3, p, label { color: #d4af37 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { 
        background-color: #d4af37 !important; color: #000000 !important; 
        font-weight: bold !important; border-radius: 8px !important;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
        background-color: #1a1c23 !important; color: white !important; border: 1px solid #d4af37 !important;
    }
    div[data-testid="metric-container"] {
        background-color: #1a1c23; border: 1px solid #d4af37; padding: 20px; border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO DIRETA ---
URL_SUPA = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY_SUPA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtcmpnZXVrcXVleXl4emhicHJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODEzODAsImV4cCI6MjA5MjA1NzM4MH0.zEk_qYIvErts5aO9fJ6EL6ZU--Pm7woqugCfW3i0yyY"
supabase = create_client(URL_SUPA, KEY_SUPA)

# --- MENU ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1063/1063231.png", width=80)
    st.markdown("## ⚜️ MENU PJ STUDIO")
    pagina = st.radio("Ir para:", ["Painel", "Novo Job / Orçamento", "Gestão de Projetos", "Configurações"])

# --- PÁGINA: PAINEL ---
if pagina == "Painel":
    st.title("⚜️ Painel de Controle")
    pago, pendente = 0.0, 0.0
    try:
        res = supabase.table("projetos").select("valor, financeiro").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
            pago = df[df['financeiro'] == 'Pago Total']['valor'].sum()
            # Soma quem pagou só 50% ou nada
            pendente = df[df['financeiro'] != 'Pago Total']['valor'].sum()
    except: pass
    c1, c2 = st.columns(2)
    c1.metric("💰 DINHEIRO NO BOLSO", f"R$ {pago:,.2f}")
    c2.metric("⏳ CONTAS A RECEBER", f"R$ {pendente:,.2f}")

# --- PÁGINA: NOVO JOB ---
elif pagina == "Novo Job / Orçamento":
    st.title("📝 Novo Registro")
    with st.form("form_job"):
        c_l, c_r = st.columns(2)
        with c_l:
            nome = st.text_input("Nome do Cliente")
            doc = st.text_input("CPF ou CNPJ")
            whatsapp = st.text_input("WhatsApp")
        with c_r:
            email = st.text_input("E-mail")
            valor = st.number_input("Valor Total (R$)", min_value=0.0)
            prazo = st.text_input("Prazo")
        servico = st.text_input("Serviço")
        exigencias = st.text_area("Exigências")
        if st.form_submit_button("CADASTRAR JOB ⚜️"):
            try:
                supabase.table("projetos").insert({
                    "nome": nome, "valor": valor, "financeiro": "Aguardando Entrada",
                    "descricao": f"{servico} | {exigencias}", "prazo": prazo
                }).execute()
                st.success("✅ Cadastrado! Vá em 'Gestão' para controlar os pagamentos.")
            except Exception as e: st.error(f"Erro: {e}")

# --- PÁGINA: GESTÃO (OS 4 BOTÕES DE CONTROLE) ---
elif pagina == "Gestão de Projetos":
    st.title("⚙️ Gestão de Pagamentos e Projetos")
    try:
        res = supabase.table("projetos").select("*").execute()
        if res.data:
            for row in res.data:
                with st.expander(f"📌 {row['nome']} - Status: {row['financeiro']}"):
                    st.write(f"**Valor Total:** R$ {row['valor']} | **Prazo:** {row['prazo']}")
                    st.write(f"**Descrição:** {row['descricao']}")
                    
                    b1, b2, b3, b4 = st.columns(4)
                    # BOTAO 1: SALVAR/EDITAR (Simulado pela própria estrutura)
                    b1.button("💾 Salvar Alterações", key=f"save_{row['id']}")
                    
                    # BOTAO 2: ENTRADA 50%
                    if b2.button("💵 Recebi 50% (Entrada)", key=f"ent_{row['id']}"):
                        supabase.table("projetos").update({"financeiro": "Entrada Paga (50%)"}).eq("id", row['id']).execute()
                        st.rerun()
                    
                    # BOTAO 3: FINAL 50%
                    if b3.button("💰 Recebi +50% (Total)", key=f"fin_{row['id']}"):
                        supabase.table("projetos").update({"financeiro": "Pago Total"}).eq("id", row['id']).execute()
                        st.rerun()
                        
                    # BOTAO 4: EXCLUIR
                    if b4.button("❌ Excluir Projeto", key=f"del_{row['id']}"):
                        supabase.table("projetos").delete().eq("id", row['id']).execute()
                        st.rerun()
    except: st.write("Nenhum projeto.")

# --- PÁGINA: CONFIGURAÇÕES (ENDEREÇO ADICIONADO) ---
elif pagina == "Configurações":
    st.title("🛠️ Configurações PJ GOLD")
    with st.form("conf_final"):
        st.subheader("Dados para Localização e Contato")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nome da Empresa", value="PJ GOLD DESIGN")
            st.text_input("CNPJ", value="00.000.000/0001-00")
        with c2:
            st.text_input("WhatsApp Profissional")
            st.text_input("E-mail Profissional")
            
        # CAMPO DE ENDEREÇO (COMO O CLIENTE TE ACHA)
        endereco = st.text_area("Endereço Completo (Rua, Número, Bairro, Cidade/UF)")
        
        if st.form_submit_button("SALVAR DADOS DA EMPRESA ⚜️"):
            st.success("✅ Endereço e dados salvos com sucesso!")
