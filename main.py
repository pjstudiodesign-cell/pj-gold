import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
from datetime import datetime

# ==========================================
# 1. CONEXÃO (DADOS ORIGINAIS SUPABASE)
# ==========================================
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtcmpnZXVrcXVleXl4emhicHJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODEzODAsImV4cCI6MjA5MjA1NzM4MH0.zEk_qYIvErts5aO9fJ6EL6ZU--Pm7woqugCfW3i0yyY"

@st.cache_resource
def get_supabase() -> Client:
    return create_client(URL, KEY)

supabase = get_supabase()

# ==========================================
# 2. ESTILO VISUAL PREMIUM (BLINDADO)
# ==========================================
st.set_page_config(page_title="PJ GOLD PRO", layout="wide", page_icon="💰")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #001f3f;
        color: #d4af37;
        font-weight: bold;
        border: 2px solid #d4af37;
    }
    .stButton>button:hover {
        background-color: #d4af37;
        color: #001f3f;
    }
    .stExpander { border: 1px solid #d4af37; border-radius: 5px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. GERAÇÃO DE DOCUMENTOS (LAYOUT PJ STUDIO)
# ==========================================
def gerar_pdf(p, dados_empresa, tipo="Orcamento", sub_tipo="Integral"):
    pdf = FPDF()
    pdf.add_page()
    
    # Faixa Ouro Superior
    pdf.set_fill_color(212, 175, 55)
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_font("Arial", 'B', 18)
    pdf.set_y(10)
    pdf.cell(0, 10, f"{dados_empresa.get('nome_empresa', 'PJ Studio Design')}", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 8)
    info = f"CNPJ/CPF: {dados_empresa.get('cpf_cnpj', '')} | WhatsApp: {dados_empresa.get('whatsapp', '')} | E-mail: {dados_empresa.get('email', '')}"
    pdf.cell(0, 5, info, 0, 1, 'C')
    pdf.cell(0, 5, f"Endereço: {dados_empresa.get('endereco', '')}", 0, 1, 'C')
    
    pdf.ln(25)
    
    if tipo == "Contrato":
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS", 0, 1, 'C')
        pdf.ln(5)
        pdf.set_font("Arial", '', 10)
        texto = f"""CONTRATANTE: {p['cliente']} | CPF/CNPJ: {p['cpf_cnpj']}
OBJETO: {p['nome_projeto']}
DESCRIÇÃO: {p['descricao']}
VALOR TOTAL: R$ {p['valor_total']:.2f} | PRAZO: {p['prazo']}

O contratante aceita os termos e condições de serviço da PJ Studio Design."""
        pdf.multi_cell(0, 7, texto)
    
    elif tipo == "Recibo":
        valor_r = p['valor_total']
        obs_r = "QUITAÇÃO INTEGRAL"
        if sub_tipo == "Entrada": 
            valor_r = p['valor_total'] / 2
            obs_r = "PAGAMENTO DE ENTRADA (50%)"
        elif sub_tipo == "Final":
            valor_r = p['valor_total'] / 2
            obs_r = "PAGAMENTO FINAL (50%)"
            
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"RECIBO DE PAGAMENTO: {p['nome_projeto']}".upper(), 0, 1, 'C')
        pdf.ln(10)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, f"Recebemos de {p['cliente']} a importância de R$ {valor_r:.2f} referente à {obs_r} do projeto acima descrito.")
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"VALOR TOTAL DO PROJETO: R$ {p['valor_total']:.2f}", 0, 1, 'R')
    
    else: # Orçamento
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"ORÇAMENTO: {p['nome_projeto']}".upper(), "B", 1, 'L')
        pdf.ln(5)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"Cliente: {p['cliente']}", 0, 1)
        pdf.cell(0, 8, f"Prazo: {p['prazo']}", 0, 1)
        pdf.multi_cell(0, 8, f"Descrição/Exigências: {p['descricao']}")
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"VALOR TOTAL: R$ {p['valor_total']:.2f}", 0, 1, 'R')

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 4. CONFIGURAÇÕES E MENU
# ==========================================
try:
    conf_res = supabase.table("configuracoes").select("*").limit(1).execute()
    dados_empresa = conf_res.data[0] if conf_res.data else {"nome_empresa": "PJ Studio Design", "cpf_cnpj": "", "whatsapp": "", "email": "", "endereco": ""}
except:
    dados_empresa = {"nome_empresa": "PJ Studio Design", "cpf_cnpj": "", "whatsapp": "", "email": "", "endereco": ""}

menu = st.sidebar.selectbox("MENU PRINCIPAL", ["Painel de Controle", "Novo Orçamento", "Gestão de Projetos", "Configurações"])

# --- ABA: PAINEL DE CONTROLE ---
if menu == "Painel de Controle":
    st.title("🚀 Dashboard PJ GOLD PRO")
    res = supabase.table("projetos").select("valor_total").execute()
    total = sum([x['valor_total'] for x in res.data]) if res.data else 0.0
    st.metric("Faturamento Acumulado", f"R$ {total:,.2f}")

# --- ABA: NOVO ORÇAMENTO (CAMPOS RESTAURADOS) ---
elif menu == "Novo Orçamento":
    st.header("📝 Criar Novo Orçamento")
    with st.form("form_orc", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            cliente = st.text_input("Nome do Cliente")
            cpf_cnpj = st.text_input("CPF/CNPJ Cliente")
            whatsapp = st.text_input("WhatsApp Cliente")
        with c2:
            email = st.text_input("E-mail Cliente")
            endereco = st.text_input("Endereço Cliente")
            nome_projeto = st.text_input("Nome do Projeto")
            
        descricao = st.text_area("Descrição do Serviço / Exigências do Cliente")
        
        c3, c4 = st.columns(2)
        with c3: prazo = st.text_input("Prazo de Entrega")
        with c4: valor = st.number_input("Valor Total (R$)", min_value=0.0, step=10.0)
        
        if st.form_submit_button("GERAR E SALVAR ORÇAMENTO"):
            if cliente and nome_projeto:
                supabase.table("projetos").insert({
                    "cliente": cliente, "cpf_cnpj": cpf_cnpj, "whatsapp_cliente": whatsapp,
                    "email_cliente": email, "endereco_cliente": endereco, "nome_projeto": nome_projeto,
                    "descricao": descricao, "prazo": prazo, "valor_total": valor,
                    "status_entrada": "Pendente", "status_final": "Pendente"
                }).execute()
                st.success("Orçamento salvo com sucesso!")
                st.rerun()

# --- ABA: GESTÃO DE PROJETOS (BOTOES E CAMPOS RESTAURADOS) ---
elif menu == "Gestão de Projetos":
    st.header("📋 Gestão de Projetos")
    projs = supabase.table("projetos").select("*").execute()
    
    if projs.data:
        for p in projs.data:
            with st.expander(f"📌 {p['cliente']} - {p['nome_projeto']}"):
                col_i, col_b1, col_b2 = st.columns([2, 1, 1])
                
                with col_i:
                    st.write(f"**Valor:** R$ {p['valor_total']:.2f}")
                    st.write(f"**WhatsApp:** {p['whatsapp_cliente']}")
                    s_ent = st.selectbox("Status Entrada", ["Pendente", "Pago"], index=0 if p['status_entrada']=="Pendente" else 1, key=f"ent_{p['id']}")
                    s_fin = st.selectbox("Status Final", ["Pendente", "Pago"], index=0 if p['status_final']=="Pendente" else 1, key=f"fin_{p['id']}")
                
                with col_b1:
                    st.download_button("Orçamento", gerar_pdf(p, dados_empresa, "Orcamento"), f"Orc_{p['id']}.pdf", key=f"d_o_{p['id']}")
                    st.download_button("Recibo Integral", gerar_pdf(p, dados_empresa, "Recibo", "Integral"), f"Rec_I_{p['id']}.pdf", key=f"d_ri_{p['id']}")
                    st.download_button("Recibo Entrada", gerar_pdf(p, dados_empresa, "Recibo", "Entrada"), f"Rec_E_{p['id']}.pdf", key=f"d_re_{p['id']}")
                    st.download_button("Recibo Final", gerar_pdf(p, dados_empresa, "Recibo", "Final"), f"Rec_F_{p['id']}.pdf", key=f"d_rf_{p['id']}")

                with col_b2:
                    st.download_button("Contrato", gerar_pdf(p, dados_empresa, "Contrato"), f"Cont_{p['id']}.pdf", key=f"d_c_{p['id']}")
                    if st.button("Atualizar", key=f"up_{p['id']}"):
                        supabase.table("projetos").update({"status_entrada": s_ent, "status_final": s_fin}).eq("id", p['id']).execute()
                        st.success("Atualizado!")
                        st.rerun()
                    if st.button("EXCLUIR", key=f"del_{p['id']}"):
                        supabase.table("projetos").delete().eq("id", p['id']).execute()
                        st.rerun()

# --- ABA: CONFIGURAÇÕES (MANUTENÇÃO DO QUE ESTÁ INTACTO) ---
elif menu == "Configurações":
    st.header("⚙️ Configurações do Estúdio")
    with st.form("form_config"):
        n = st.text_input("Empresa", value=dados_empresa['nome_empresa'])
        c = st.text_input("CPF/CNPJ", value=dados_empresa['cpf_cnpj'])
        w = st.text_input("WhatsApp", value=dados_empresa['whatsapp'])
        e = st.text_input("E-mail", value=dados_empresa['email'])
        a = st.text_input("Endereço", value=dados_empresa['endereco'])
        
        if st.form_submit_button("SALVAR"):
            d = {"nome_empresa": n, "cpf_cnpj": c, "whatsapp": w, "email": e, "endereco": a}
            if "id" in dados_empresa:
                supabase.table("configuracoes").update(d).eq("id", dados_empresa['id']).execute()
            else:
                supabase.table("configuracoes").insert(d).execute()
            st.success("Configurações salvas!")
            st.rerun()
