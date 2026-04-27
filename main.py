import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO E BLINDAGEM VISUAL (LACRADO) ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- 2. CONEXÃO SUPABASE (LACRADA) ---
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "sb_publishable_qisG5bDBD-AxpBKW9LmBnA_p-_M671n"

try:
    supabase: Client = create_client(URL, KEY)
except Exception:
    st.error("Erro crítico de conexão.")
    st.stop()

# --- 3. CSS PRETO E OURO (SISTEMA DE CORES BLINDADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #121212 !important; border-right: 2px solid #D4AF37 !important; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p { color: #D4AF37 !important; font-weight: bold !important; font-size: 1.1rem !important; }
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800 !important; }
    label { color: #D4AF37 !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.8rem !important; font-weight: bold; }
    .stButton>button { background-color: #D4AF37 !important; color: black !important; font-weight: bold !important; border-radius: 10px !important; }
    input, textarea, div[data-baseweb="select"] { background-color: #1c1c1c !important; color: white !important; border: 1px solid #444 !important; }
    .stExpander { border: 1px solid #D4AF37 !important; background-color: #121212 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÕES DE DADOS ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data if proj.data else [], conf.data[0] if conf.data else {}
    except Exception: return [], {}

# --- 5. GERAÇÃO DE PDF (SISTEMA DE DOCUMENTOS INTEGRADO) ---
def gerar_pdf(tipo, p, c):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(212, 175, 55) 
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"{c.get('nome_empresa', 'PJ STUDIO DESIGN')}", ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"CNPJ/CPF: {c.get('cpf_cnpj', '')} | WhatsApp: {c.get('whatsapp', '')}", ln=True, align='C')
    pdf.cell(0, 5, f"E-mail: {c.get('email', '')}", ln=True, align='C')
    pdf.multi_cell(0, 5, f"Endereço: {c.get('endereco', '')}", align='C')
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)

    if tipo == "CONTRATO":
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS", ln=True, align='C')
        pdf.ln(5)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 6, f"CONTRATANTE: {p.get('cliente')} | CPF/CNPJ: {p.get('cpf_cnpj', 'N/I')}")
        pdf.ln(4)
        clausulas = [
            f"1. OBJETO: Prestação de serviços de design gráfico ({p.get('descricao')}).",
            f"2. PRAZO: {p.get('prazo', 'A combinar')}, após pagamento da entrada.",
            f"3. VALOR: R$ {float(p.get('valor_total', 0)):,.2f} (50% entrada / 50% entrega).",
            "4. ALTERAÇÕES: Inclui até 2 revisões simples.",
            "5. DIREITOS: Uso liberado após quitação total.",
            "6. CANCELAMENTO: Início do serviço não gera reembolso da entrada.",
            "7. VALIDADE: Ativo após assinatura das partes."
        ]
        for item in clausulas: pdf.multi_cell(0, 6, item); pdf.ln(1)
        pdf.ln(10)
        pdf.cell(0, 10, f"Local/Data: Barra Mansa - RJ, {datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(15)
        pdf.cell(95, 10, "__________________________", 0, 0, 'C'); pdf.cell(95, 10, "__________________________", 0, 1, 'C')
        pdf.cell(95, 5, "Contratante", 0, 0, 'C'); pdf.cell(95, 5, c.get('nome_empresa'), 0, 1, 'C')
    
    elif tipo == "ORC":
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"ORÇAMENTO PROFISSIONAL: {p.get('nome_projeto')}", ln=True)
        pdf.line(10, 55, 200, 55); pdf.ln(5)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, f"Cliente: {p.get('cliente')}", ln=True)
        pdf.cell(0, 6, f"Exigências: {p.get('exigencias', 'Nenhuma')}", ln=True)
        pdf.multi_cell(0, 6, f"Descrição: {p.get('descricao')}")
        pdf.cell(0, 10, f"VALOR TOTAL: R$ {float(p.get('valor_total', 0)):,.2f}", ln=True, align='R')

    elif tipo == "REC":
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"RECIBO DE PAGAMENTO: {p.get('nome_projeto')}", ln=True)
        pdf.ln(5)
        valor = float(p.get('valor_total', 0))
        if p.get('status_total') == 'Recebido': txt = f"QUITAÇÃO INTEGRAL de R$ {valor:,.2f}"
        elif p.get('status_entrada') == 'Recebido': txt = f"ENTRADA (50%) de R$ {valor/2:,.2f}"
        else: txt = f"PAGAMENTO FINAL (50%) de R$ {valor/2:,.2f}"
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, f"Recebemos de {p.get('cliente')} o valor referente à {txt}.")

    return pdf.output(dest='S').encode('latin-1')

# --- 6. NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚜️ PJ STUDIO</h2>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("NAVEGAÇÃO", ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"], label_visibility="collapsed")

# --- 7. TELAS RESTAURADAS E BLINDADAS ---
if menu == "PAINEL":
    st.title("⚜️ PAINEL DE CONTROLE")
    projetos, _ = carregar_dados()
    no_bolso = 0
    total_geral = sum([float(p.get('valor_total', 0)) for p in projetos])
    for p in projetos:
        v = float(p.get('valor_total', 0))
        if p.get('status_total') == 'Recebido': no_bolso += v
        else:
            if p.get('status_entrada') == 'Recebido': no_bolso += (v/2)
            if p.get('status_final') == 'Recebido': no_bolso += (v/2)
    
    c1, c2 = st.columns(2)
    c1.metric("💰 DINHEIRO NO BOLSO", f"R$ {no_bolso:,.2f}")
    c2.metric("⏳ CONTAS A RECEBER", f"R$ {(total_geral - no_bolso):,.2f}")

elif menu == "NOVO ORÇAMENTO":
    st.title("➕ NOVO ORÇAMENTO")
    with st.form("orc_form"):
        c_nome = st.text_input("Nome do Cliente")
        col1, col2 = st.columns(2)
        c_doc = col1.text_input("CPF/CNPJ")
        c_zap = col2.text_input("WhatsApp")
        c_end = st.text_input("Endereço do Cliente Completo")
        p_nome = st.text_input("Nome do Projeto")
        p_exig = st.text_input("Exigências do Cliente")
        col3, col4 = st.columns(2)
        p_valor = col3.number_input("Valor Total", step=0.01)
        p_prazo = col4.text_input("Prazo de Entrega")
        p_desc = st.text_area("Descrição do Serviço")
        if st.form_submit_button("SALVAR ORÇAMENTO"):
            supabase.table("projetos").insert({
                "cliente":c_nome, "cpf_cnpj":c_doc, "whatsapp_cliente":c_zap, 
                "endereco_cliente":c_end, "nome_projeto":p_nome, "exigencias":p_exig, 
                "valor_total":p_valor, "prazo":p_prazo, "descricao":p_desc, 
                "status_total":"Pendente", "status_entrada":"Pendente", "status_final":"Pendente"
            }).execute()
            st.rerun()

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO E EDIÇÃO")
    projetos, config = carregar_dados()
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | {p.get('cliente')}"):
            col_ed1, col_ed2 = st.columns(2)
            n_p = col_ed1.text_input("Editar Projeto", p.get('nome_projeto'), key=f"np_{p['id']}")
            n_c = col_ed2.text_input("Editar Cliente", p.get('cliente'), key=f"nc_{p['id']}")
            
            st.write("---")
            st.write("**Controle de Pagamentos (50/50)**")
            f1, f2, f3 = st.columns(3)
            v_t = f1.selectbox("VALOR TOTAL", ["Pendente", "Recebido"], index=0 if p.get('status_total')=="Pendente" else 1, key=f"vt_{p['id']}")
            v_e = f2.selectbox("ENTRADA (50%)", ["Pendente", "Recebido"], index=0 if p.get('status_entrada')=="Pendente" else 1, key=f"ve_{p['id']}")
            v_f = f3.selectbox("FINAL (50%)", ["Pendente", "Recebido"], index=0 if p.get('status_final')=="Pendente" else 1, key=f"vf_{p['id']}")
            
            st.write("---")
            b1, b2, b3, b4, b5 = st.columns(5)
            if b1.button("💾 ATUALIZAR", key=f"up_{p['id']}"):
                supabase.table("projetos").update({"nome_projeto":n_p, "cliente":n_c, "status_total":v_t, "status_entrada":v_e, "status_final":v_f}).eq("id", p['id']).execute(); st.rerun()
            b2.download_button("📄 ORÇAMENTO", gerar_pdf("ORC", p, config), f"Orc_{p['id']}.pdf", key=f"bo_{p['id']}")
            b3.download_button("🧾 RECIBO", gerar_pdf("REC", p, config), f"Rec_{p['id']}.pdf", key=f"br_{p['id']}")
            b4.download_button("📜 CONTRATO", gerar_pdf("CONTRATO", p, config), f"Con_{p['id']}.pdf", key=f"bc_{p['id']}")
            if b5.button("🗑️ EXCLUIR", key=f"del_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute(); st.rerun()

elif menu == "CONFIGURAÇOES":
    st.title("⚙️ CONFIGURAÇÕES")
    _, config = carregar_dados()
    with st.form("cfg"):
        n_e = st.text_input("Nome da Empresa", config.get('nome_empresa', ''))
        c_e = st.text_input("CNPJ/CPF", config.get('cpf_cnpj', ''))
        w_e = st.text_input("WhatsApp Profissional", config.get('whatsapp', ''))
        e_e = st.text_input("E-mail de Contato", config.get('email', ''))
        end_e = st.text_area("Endereço Completo", config.get('endereco', ''))
        if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
            supabase.table("configuracoes").update({"nome_empresa":n_e, "cpf_cnpj":c_e, "whatsapp":w_e, "email":e_e, "endereco":end_e}).eq("id", 1).execute(); st.rerun()
