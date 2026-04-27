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
# 2. ESTILO VISUAL PREMIUM (BLINDAGEM TOTAL)
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
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. GERAÇÃO DE DOCUMENTOS (LAYOUT PJ STUDIO)
# ==========================================
def gerar_pdf(p, dados_empresa, tipo="Orcamento", sub_tipo="Integral"):
    pdf = FPDF()
    pdf.add_page()
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
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS", 0, 1, 'C'); pdf.ln(5)
        pdf.set_font("Arial", '', 10)
        texto = f"CONTRATANTE: {p['cliente']} | OBJETO: {p['nome_projeto']}\nDESCRIÇÃO: {p['descricao']}\nVALOR: R$ {p['valor_total']:.2f} | PRAZO: {p['prazo']}"
        pdf.multi_cell(0, 7, texto)
    elif tipo == "Recibo":
        valor_r = p['valor_total'] if sub_tipo == "Integral" else p['valor_total'] / 2
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, f"RECIBO ({sub_tipo})", 0, 1, 'C'); pdf.ln(10)
        pdf.set_font("Arial", '', 12); pdf.multi_cell(0, 10, f"Recebemos de {p['cliente']} a importância de R$ {valor_r:.2f} referente ao projeto {p['nome_projeto']}.")
    else:
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, f"ORÇAMENTO: {p['nome_projeto']}".upper(), "B", 1, 'L'); pdf.ln(5)
        pdf.set_font("Arial", '', 11); pdf.cell(0, 8, f"Cliente: {p['cliente']}", 0, 1); pdf.cell(0, 8, f"Prazo: {p['prazo']}", 0, 1); pdf.multi_cell(0, 8, f"Descrição: {p['descricao']}")
        pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, f"VALOR TOTAL: R$ {p['valor_total']:.2f}", 0, 1, 'R')
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

# --- ABA: NOVO ORÇAMENTO ---
elif menu == "Novo Orçamento":
    st.header("📝 Criar Novo Orçamento")
    with st.form("form_orc", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            cli = st.text_input("Nome do Cliente")
            cnpj = st.text_input("CPF/CNPJ Cliente")
            zap = st.text_input("WhatsApp Cliente")
        with c2:
            ema = st.text_input("E-mail Cliente")
            end = st.text_input("Endereço Cliente")
            proj = st.text_input("Nome do Projeto")
        desc = st.text_area("Descrição do Serviço / Exigências")
        c3, c4 = st.columns(2)
        with c3: prz = st.text_input("Prazo de Entrega")
        with c4: val = st.number_input("Valor Total (R$)", min_value=0.0)
        if st.form_submit_button("GERAR E SALVAR ORÇAMENTO"):
            if cli and proj:
                supabase.table("projetos").insert({"cliente": cli, "cpf_cnpj": cnpj, "whatsapp_cliente": zap, "email_cliente": ema, "endereco_cliente": end, "nome_projeto": proj, "descricao": desc, "prazo": prz, "valor_total": val, "status_entrada": "Pendente", "status_final": "Pendente"}).execute()
                st.success("Salvo!"); st.rerun()

# --- ABA: GESTÃO DE PROJETOS (RESTAURAÇÃO TOTAL DE CAMPOS E BOTOES) ---
elif menu == "Gestão de Projetos":
    st.header("📋 Gestão de Projetos")
    projs = supabase.table("projetos").select("*").execute()
    if projs.data:
        for p in projs.data:
            with st.expander(f"📌 {p['cliente']} - {p['nome_projeto']}"):
                # CAMPOS DE EDIÇÃO INTEGRADOS (IGUAL AO ORÇAMENTO)
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    edit_cli = st.text_input("Cliente", value=p['cliente'], key=f"cli_{p['id']}")
                    edit_cnpj = st.text_input("CPF/CNPJ", value=p['cpf_cnpj'], key=f"cnpj_{p['id']}")
                    edit_zap = st.text_input("WhatsApp", value=p['whatsapp_cliente'], key=f"zap_{p['id']}")
                    edit_ent = st.selectbox("Status Entrada", ["Pendente", "Pago"], index=0 if p['status_entrada']=="Pendente" else 1, key=f"en_{p['id']}")
                with col_e2:
                    edit_ema = st.text_input("E-mail", value=p['email_cliente'], key=f"ema_{p['id']}")
                    edit_end = st.text_input("Endereço", value=p['endereco_cliente'], key=f"end_{p['id']}")
                    edit_prz = st.text_input("Prazo", value=p['prazo'], key=f"prz_{p['id']}")
                    edit_fin = st.selectbox("Status Final", ["Pendente", "Pago"], index=0 if p['status_final']=="Pendente" else 1, key=f"fi_{p['id']}")
                
                edit_desc = st.text_area("Descrição / Exigências", value=p['descricao'], key=f"desc_{p['id']}")
                edit_val = st.number_input("Valor (R$)", value=float(p['valor_total']), key=f"val_{p['id']}")

                # BOTÕES DE DOCUMENTOS E AÇÃO
                st.write("---")
                b1, b2, b3, b4 = st.columns(4); b5, b6, b7, b8 = st.columns(4)
                with b1: st.download_button("Orçamento", gerar_pdf(p, dados_empresa, "Orcamento"), f"Orc_{p['id']}.pdf", key=f"d1_{p['id']}")
                with b2: st.download_button("Recibo Integral", gerar_pdf(p, dados_empresa, "Recibo", "Integral"), f"RecI_{p['id']}.pdf", key=f"d2_{p['id']}")
                with b3: st.download_button("Recibo Entrada", gerar_pdf(p, dados_empresa, "Recibo", "Entrada"), f"RecE_{p['id']}.pdf", key=f"d3_{p['id']}")
                with b4: st.download_button("Recibo Final", gerar_pdf(p, dados_empresa, "Recibo", "Final"), f"RecF_{p['id']}.pdf", key=f"d4_{p['id']}")
                with b5: st.download_button("Contrato", gerar_pdf(p, dados_empresa, "Contrato"), f"Cont_{p['id']}.pdf", key=f"d5_{p['id']}")
                
                with b6:
                    if st.button("ATUALIZAR", key=f"btn_up_{p['id']}"):
                        supabase.table("projetos").update({"cliente": edit_cli, "cpf_cnpj": edit_cnpj, "whatsapp_cliente": edit_zap, "email_cliente": edit_ema, "endereco_cliente": edit_end, "prazo": edit_prz, "descricao": edit_desc, "valor_total": edit_val, "status_entrada": edit_ent, "status_final": edit_fin}).eq("id", p['id']).execute()
                        st.success("Atualizado!"); st.rerun()
                with b7:
                    if st.button("EXCLUIR", key=f"btn_del_{p['id']}"):
                        supabase.table("projetos").delete().eq("id", p['id']).execute()
                        st.rerun()

# --- ABA: CONFIGURAÇÕES ---
elif menu == "Configurações":
    st.header("⚙️ Configurações do Estúdio")
    with st.form("f_conf"):
        n = st.text_input("Empresa", value=dados_empresa['nome_empresa'])
        c = st.text_input("CPF/CNPJ", value=dados_empresa['cpf_cnpj'])
        w = st.text_input("WhatsApp", value=dados_empresa['whatsapp'])
        e = st.text_input("Email", value=dados_empresa['email'])
        a = st.text_input("Endereço", value=dados_empresa['endereco'])
        if st.form_submit_button("SALVAR"):
            d = {"nome_empresa": n, "cpf_cnpj": c, "whatsapp": w, "email": e, "endereco": a}
            if "id" in dados_empresa: supabase.table("configuracoes").update(d).eq("id", dados_empresa['id']).execute()
            else: supabase.table("configuracoes").insert(d).execute()
            st.success("Salvo!"); st.rerun()
