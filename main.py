import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
from datetime import datetime
import time

# --- 1. CONFIGURAÇÃO E BLINDAGEM VISUAL (LACRADO) ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- 2. CONEXÃO SUPABASE (LACRADA - CHAVES ORIGINAIS PRESERVADAS) ---
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "sb_publishable_qisG5bDBD-AxpBKW9LmBnA_p-_M671n"

try:
    supabase: Client = create_client(URL, KEY)
except Exception:
    st.error("ERRO DE CONEXÃO: Verifique as chaves no Render.")
    st.stop()

# --- 3. CSS PRETO E OURO (LACRADO) ---
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

# --- 4. FUNÇÕES DE DADOS (LACRADAS) ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data if proj.data else [], conf.data[0] if conf.data else {}
    except Exception: return [], {}

# --- 5. GERAÇÃO DE PDF (CORREÇÃO CIRÚRGICA DE CODIFICAÇÃO) ---
def gerar_pdf(tipo, p, c):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(212, 175, 55) 
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    
    # Função interna para limpar caracteres que quebram o PDF
    def clean(txt): return str(txt).encode('latin-1', 'replace').decode('latin-1')

    pdf.cell(0, 10, clean(c.get('nome_empresa', 'PJ STUDIO DESIGN')), ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, clean(f"CNPJ/CPF: {c.get('cpf_cnpj', '')} | WhatsApp: {c.get('whatsapp', '')}"), ln=True, align='C')
    pdf.ln(10)

    if tipo == "CONTRATO":
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "CONTRATO DE PRESTACAO DE SERVICOS", ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 6, clean(f"CONTRATANTE: {p.get('cliente')} | CPF/CNPJ: {p.get('cpf_cnpj', 'N/I')}"))
        pdf.ln(4)
        clausulas = [
            f"1. OBJETO: Prestacao de servicos de design grafico ({p.get('nome_projeto', '')}).",
            "2. PRAZO: Combinado entre as partes apos entrada.",
            f"3. VALOR: R$ {float(p.get('valor_total', 0)):,.2f} (50% entrada / 50% entrega).",
            "4. ALTERACOES: Inclui ate 2 revisoes simples.",
            f"5. DIREITOS DE USO: O {c.get('nome_empresa')} podera utilizar o material em portfolio.",
            "6. CANCELAMENTO: Nao gera reembolso da entrada.",
            "7. VALIDADE: Vale apos assinatura das partes."
        ]
        for item in clausulas: pdf.multi_cell(0, 6, clean(item)); pdf.ln(1)
        pdf.ln(10)
        pdf.cell(0, 10, clean(f"Data: {datetime.now().strftime('%d/%m/%Y')}"), ln=True)

    elif tipo == "ORC":
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean(f"ORCAMENTO: {p.get('nome_projeto')}"), ln=True)
        pdf.ln(5); pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, clean(f"Cliente: {p.get('cliente')}"), ln=True)
        pdf.cell(0, 10, clean(f"TOTAL: R$ {float(p.get('valor_total', 0)):,.2f}"), ln=True, align='R')

    elif tipo == "REC":
        pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "RECIBO DE PAGAMENTO", ln=True)
        v = float(p.get('valor_total', 0))
        txt = "QUITACAO INTEGRAL" if p.get('status_total') == 'Recebido' else "PAGAMENTO"
        pdf.multi_cell(0, 8, clean(f"Recebemos de {p.get('cliente')}, {txt} de R$ {v:,.2f}.")); pdf.ln(20)

    return pdf.output(dest='S').encode('latin-1')

# --- 6. NAVEGAÇÃO E TELAS (RESTAURADO E LACRADO) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚜️ PJ STUDIO</h2>", unsafe_allow_html=True)
    menu = st.radio("NAVEGACAO", ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"], label_visibility="collapsed")

if menu == "PAINEL":
    st.title("⚜️ PAINEL DE CONTROLE")
    projetos, _ = carregar_dados()
    st.metric("💰 DINHEIRO NO BOLSO", f"R$ {sum([float(p.get('valor_total', 0)) for p in projetos if p.get('status_total') == 'Recebido']):,.2f}")

elif menu == "NOVO ORÇAMENTO":
    st.title("➕ NOVO ORÇAMENTO")
    with st.form("orc_form"):
        c_nome = st.text_input("Nome do Cliente")
        p_nome = st.text_input("Nome do Projeto")
        p_valor = st.number_input("Valor Total", step=0.01)
        if st.form_submit_button("SALVAR ORÇAMENTO"):
            if c_nome and p_nome:
                supabase.table("projetos").insert({"cliente":c_nome, "nome_projeto":p_nome, "valor_total":p_valor}).execute()
                st.success("Salvo!"); st.rerun()

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO E EDIÇÃO")
    projetos, config = carregar_dados()
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | {p.get('cliente')}"):
            # RESTAURADO: Todos os campos de edição que você exigiu (LACRADO)
            ed_nome_p = st.text_input("Nome do Projeto", p.get('nome_projeto'), key=f"p_{p['id']}")
            ed_cliente = st.text_input("Nome do Cliente", p.get('cliente'), key=f"c_{p['id']}")
            ed_doc = st.text_input("CPF/CNPJ", p.get('cpf_cnpj', ''), key=f"d_{p['id']}")
            ed_valor = st.number_input("Valor Total", value=float(p.get('valor_total', 0)), step=0.01, key=f"v_{p['id']}")
            st.write("---")
            b1, b2, b3, b4 = st.columns(4)
            if b1.button("💾 ATUALIZAR", key=f"up_{p['id']}"):
                supabase.table("projetos").update({"nome_projeto":ed_nome_p, "cliente":ed_cliente, "cpf_cnpj":ed_doc, "valor_total":ed_valor}).eq("id", p['id']).execute(); st.rerun()
            b2.download_button("📄 ORÇAMENTO", gerar_pdf("ORC", p, config), f"Orc_{p['id']}.pdf", key=f"bo_{p['id']}")
            b3.download_button("🧾 RECIBO", gerar_pdf("REC", p, config), f"Rec_{p['id']}.pdf", key=f"br_{p['id']}")
            b4.download_button("📜 CONTRATO", gerar_pdf("CONTRATO", p, config), f"Con_{p['id']}.pdf", key=f"bc_{p['id']}")
