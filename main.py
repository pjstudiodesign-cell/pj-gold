import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
from datetime import datetime

# ==========================================
# 1. CONEXÃO BLINDADA (CREDENCIAIS DO PAULO)
# ==========================================
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtcmpnZXVrcXVleXl4emhicHJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODEzODAsImV4cCI6MjA5MjA1NzM4MH0.zEk_qYIvErts5aO9fJ6EL6ZU--Pm7woqugCfW3i0yyY"

@st.cache_resource
def get_supabase() -> Client:
    return create_client(URL, KEY)

supabase = get_supabase()

# ==========================================
# 2. ESTILO VISUAL PREMIUM (INTOCÁVEL)
# ==========================================
st.set_page_config(page_title="PJ GOLD PRO", layout="wide", page_icon="💰")

st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #001f3f;
        color: #d4af37;
        font-weight: bold;
        border: 1px solid #d4af37;
    }
    .stButton>button:hover {
        background-color: #d4af37;
        color: #001f3f;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. FUNÇÃO DE PDF (LAYOUT PJ STUDIO DESIGN)
# ==========================================
def gerar_pdf(p, dados_empresa, tipo="Orcamento"):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Dourado Premium
    pdf.set_fill_color(212, 175, 55)
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_y(10)
    pdf.cell(0, 10, f"{dados_empresa.get('nome_empresa', 'PJ Studio Design')}", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 8)
    info = f"CNPJ/CPF: {dados_empresa.get('cpf_cnpj', '')} | WhatsApp: {dados_empresa.get('whatsapp', '')} | E-mail: {dados_empresa.get('email', '')}"
    pdf.cell(0, 5, info, 0, 1, 'C')
    pdf.cell(0, 5, f"Endereço: {dados_empresa.get('endereco', '')}", 0, 1, 'C')
    
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 12)
    titulo = f"{tipo.upper()}: {p['nome_projeto']}".upper()
    pdf.cell(0, 10, titulo, "B", 1, 'L')
    
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"Cliente: {p['cliente']}", 0, 1)
    pdf.cell(0, 8, f"Prazo: {p['prazo']}", 0, 1)
    pdf.multi_cell(0, 8, f"Descrição: {p['descricao']}")
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"VALOR TOTAL: R$ {p['valor_total']:.2f}", 0, 1, 'R')
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 4. CARREGAMENTO DE CONFIGURAÇÕES
# ==========================================
try:
    conf = supabase.table("configuracoes").select("*").limit(1).execute()
    dados_empresa = conf.data[0] if conf.data else {"nome_empresa": "PJ Studio Design", "cpf_cnpj": "", "whatsapp": "", "email": "", "endereco": ""}
except:
    dados_empresa = {"nome_empresa": "PJ Studio Design", "cpf_cnpj": "", "whatsapp": "", "email": "", "endereco": ""}

# ==========================================
# 5. NAVEGAÇÃO E REGRAS DE NEGÓCIO
# ==========================================
menu = st.sidebar.selectbox("MENU PRINCIPAL", ["Painel de Controle", "Novo Orçamento", "Gestão de Projetos", "Configurações"])

# --- ABA: NOVO ORÇAMENTO (CORRIGIDA E BLINDADA) ---
if menu == "Novo Orçamento":
    st.header("📝 Criar Novo Orçamento")
    with st.form("form_orcamento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cliente = st.text_input("Nome do Cliente")
            cpf_cnpj = st.text_input("CPF/CNPJ Cliente")
            whatsapp = st.text_input("WhatsApp Cliente")
        with col2:
            email = st.text_input("E-mail Cliente")
            endereco = st.text_input("Endereço Cliente")
            nome_projeto = st.text_input("Nome do Projeto")
            
        descricao = st.text_area("Descrição do Serviço")
        col3, col4 = st.columns(2)
        with col3:
            prazo = st.text_input("Prazo de Entrega (ex: 7 dias úteis)")
        with col4:
            valor_total = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
            
        if st.form_submit_button("GERAR E SALVAR ORÇAMENTO"):
            if cliente and nome_projeto:
                try:
                    res = supabase.table("projetos").insert({
                        "cliente": cliente, "cpf_cnpj": cpf_cnpj, "whatsapp_cliente": whatsapp,
                        "email_cliente": email, "endereco_cliente": endereco, "nome_projeto": nome_projeto,
                        "descricao": descricao, "prazo": prazo, "valor_total": valor_total,
                        "status_total": "Pendente", "status_entrada": "Pendente", "status_final": "Pendente"
                    }).execute()
                    
                    if res.data:
                        st.success("✅ Orçamento salvo com sucesso!")
                        st.cache_data.clear() # Limpa memória para o próximo
                        st.rerun()            # TRAVA ANTI-DUPLICAÇÃO SOLICITADA
                except Exception as e:
                    st.error(f"Erro no banco: {e}")
            else:
                st.warning("Preencha o nome do cliente e do projeto.")

# --- ABA: GESTÃO DE PROJETOS ---
elif menu == "Gestão de Projetos":
    st.header("📋 Gestão de Projetos")
    projs = supabase.table("projetos").select("*").order("created_at", desc=True).execute()
    
    if projs.data:
        for p in projs.data:
            with st.expander(f"📌 {p['cliente']} - {p['nome_projeto']} (R$ {p['valor_total']:.2f})"):
                c_e1, c_e2 = st.columns(2)
                with c_e1:
                    st.write(f"**WhatsApp:** {p['whatsapp_cliente']}")
                    st.write(f"**CPF/CNPJ:** {p['cpf_cnpj']}")
                    n_ent = st.selectbox("Status Entrada", ["Pendente", "Pago"], index=0 if p['status_entrada'] == "Pendente" else 1, key=f"e_{p['id']}")
                    n_fin = st.selectbox("Status Final", ["Pendente", "Pago"], index=0 if p['status_final'] == "Pendente" else 1, key=f"f_{p['id']}")
                with c_e2:
                    pdf_data = gerar_pdf(p, dados_empresa, "Orcamento")
                    st.download_button("📥 Baixar PDF", pdf_data, f"Orcamento_{p['id']}.pdf", key=f"d_{p['id']}")
                    if st.button("Atualizar Projeto", key=f"u_{p['id']}"):
                        supabase.table("projetos").update({
                            "status_entrada": n_ent, "status_final": n_fin,
                            "status_total": "Concluído" if n_fin == "Pago" else "Em Andamento"
                        }).eq("id", p['id']).execute()
                        st.success("Atualizado!")
                        st.cache_data.clear()
                        st.rerun()
    else:
        st.info("Nenhum registro encontrado.")

# --- ABA: PAINEL DE CONTROLE ---
elif menu == "Painel de Controle":
    st.title("🚀 Dashboard PJ GOLD PRO")
    res = supabase.table("projetos").select("valor_total").execute()
    total = sum([x['valor_total'] for x in res.data]) if res.data else 0.0
    st.metric("Faturamento Acumulado", f"R$ {total:,.2f}")

# --- ABA: CONFIGURAÇÕES ---
elif menu == "Configurações":
    st.header("⚙️ Configurações do Estúdio")
    with st.form("f_conf"):
        n = st.text_input("Nome da Empresa", value=dados_empresa['nome_empresa'])
        d = st.text_input("CPF/CNPJ", value=dados_empresa['cpf_cnpj'])
        w = st.text_input("WhatsApp", value=dados_empresa['whatsapp'])
        e = st.text_input("E-mail", value=dados_empresa['email'])
        a = st.text_input("Endereço", value=dados_empresa['endereco'])
        if st.form_submit_button("SALVAR DADOS"):
            d_save = {"nome_empresa": n, "cpf_cnpj": d, "whatsapp": w, "email": e, "endereco": a}
            if "id" in dados_empresa:
                supabase.table("configuracoes").update(d_save).eq("id", dados_empresa['id']).execute()
            else:
                supabase.table("configuracoes").insert(d_save).execute()
            st.success("Dados salvos!")
            st.rerun()
