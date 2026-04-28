import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
from datetime import datetime
import time

# --- 1. CONFIGURAÇÃO E BLINDAGEM VISUAL (LACRADO) ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- 2. CONEXÃO SUPABASE (MOTOR ORIGINAL INTEGRAL) ---
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "sb_publishable_qisG5bDBD-AxpBKW9LmBnA_p-_M671n"

try:
    supabase: Client = create_client(URL, KEY)
except Exception:
    st.error("ERRO: Conexão com o banco de dados não estabelecida.")
    st.stop()

# --- 3. CSS PRETO E OURO (VISUAL ORIGINAL SEM CORTES) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #121212 !important; border-right: 2px solid #D4AF37 !important; }
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800 !important; }
    label { color: #D4AF37 !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.8rem !important; font-weight: bold; }
    .stButton>button { 
        background-color: #D4AF37 !important; 
        color: black !important; 
        font-weight: bold !important; 
        border-radius: 10px !important;
        width: 100% !important;
    }
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

# --- 5. GERAÇÃO DE PDF (ESPECIFICAÇÕES DE PAGAMENTO DETALHADAS) ---
def gerar_pdf(tipo, p, c):
    pdf = FPDF()
    pdf.add_page()
    def t(texto): return str(texto).encode('latin-1', 'replace').decode('latin-1')

    # Cabeçalho Original
    pdf.set_fill_color(212, 175, 55) 
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_font("Arial", 'B', 16); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, t(c.get('nome_empresa', 'PJ STUDIO DESIGN')), ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, t(f"WhatsApp: {c.get('whatsapp', '')} | E-mail: {c.get('email', '')}"), ln=True, align='C')
    pdf.ln(10)

    if tipo == "REC":
        pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "RECIBO DE PAGAMENTO", ln=True, align='C'); pdf.ln(5)
        v_total = float(p.get('valor_total', 0))
        
        # Lógica de Recibo Específico
        if p.get('status_total') == 'Recebido':
            txt_pg = f"QUITAÇÃO INTEGRAL (100%) no valor de R$ {v_total:,.2f}"
        elif p.get('status_entrada') == 'Recebido' and p.get('status_final') == 'Pendente':
            txt_pg = f"PAGAMENTO DE ENTRADA (50%) no valor de R$ {v_total/2:,.2f}"
        elif p.get('status_final') == 'Recebido':
            txt_pg = f"PAGAMENTO FINAL (50%) no valor de R$ {v_total/2:,.2f}"
        else:
            txt_pg = "NENHUM PAGAMENTO IDENTIFICADO"

        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 8, t(f"Recebemos de {p.get('cliente')}, referente ao projeto {p.get('nome_projeto')}, a seguinte modalidade: {txt_pg}."))
        pdf.ln(20); pdf.cell(0, 10, "__________________________", ln=True, align='C')
        pdf.cell(0, 5, t(c.get('nome_empresa', 'PJ STUDIO DESIGN')), ln=True, align='C')

    elif tipo == "ORC":
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, t(f"ORÇAMENTO: {p.get('nome_projeto')}"), ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 6, t(f"Cliente: {p.get('cliente')}\nValor: R$ {float(p.get('valor_total', 0)):,.2f}"))

    elif tipo == "CONTRATO":
        pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "CONTRATO DE PRESTACAO DE SERVICOS", ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        clausulas = [
            f"Objeto: {p.get('nome_projeto')}",
            f"Valor: R$ {float(p.get('valor_total', 0)):,.2f} (50% Entrada / 50% Entrega)",
            "Direitos: O PJ Studio Design podera utilizar o material em portfolio."
        ]
        for item in clausulas: pdf.multi_cell(0, 6, t(item))

    return pdf.output(dest='S').encode('latin-1')

# --- 6. NAVEGAÇÃO E TELAS (RESTURADO E LACRADO) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>⚜️ PJ STUDIO</h1>", unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO", ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"], label_visibility="collapsed")

if menu == "PAINEL":
    st.title("⚜️ PAINEL DE CONTROLE")
    projetos, _ = carregar_dados()
    no_bolso = 0
    for p in projetos:
        v = float(p.get('valor_total', 0))
        if p.get('status_total') == 'Recebido': no_bolso += v
        else:
            if p.get('status_entrada') == 'Recebido': no_bolso += (v/2)
            if p.get('status_final') == 'Recebido': no_bolso += (v/2)
    st.metric("💰 DINHEIRO NO BOLSO", f"R$ {no_bolso:,.2f}")

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO E EDIÇÃO")
    projetos, config = carregar_dados()
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | {p.get('cliente')}"):
            # RESTAURAÇÃO INTEGRAL DE TODOS OS CAMPOS ORIGINAIS
            ed_nome_p = st.text_input("Nome do Projeto", p.get('nome_projeto'), key=f"p_{p['id']}")
            ed_cliente = st.text_input("Nome do Cliente", p.get('cliente'), key=f"c_{p['id']}")
            col_a, col_b = st.columns(2)
            ed_doc = col_a.text_input("CPF/CNPJ", p.get('cpf_cnpj', ''), key=f"d_{p['id']}")
            ed_zap = col_b.text_input("WhatsApp", p.get('whatsapp_cliente', ''), key=f"z_{p['id']}")
            ed_end = st.text_input("Endereço Completo", p.get('endereco_cliente', ''), key=f"e_{p['id']}")
            ed_exig = st.text_input("Exigências", p.get('exigencias', ''), key=f"x_{p['id']}")
            col_c, col_d = st.columns(2)
            ed_valor = col_c.number_input("Valor Total", value=float(p.get('valor_total', 0)), key=f"v_{p['id']}")
            ed_prazo = col_d.text_input("Prazo de Entrega", p.get('prazo', ''), key=f"pr_{p['id']}")
            ed_desc = st.text_area("Descrição do Serviço", p.get('descricao', ''), key=f"ds_{p['id']}")
            
            st.write("---")
            # LÓGICA DE 50% RESTAURADA COM PRECISÃO
            f1, f2, f3 = st.columns(3)
            v_t = f1.selectbox("TOTAL (100%)", ["Pendente", "Recebido"], index=0 if p.get('status_total')=="Pendente" else 1, key=f"vt_{p['id']}")
            v_e = f2.selectbox("ENTRADA (50%)", ["Pendente", "Recebido"], index=0 if p.get('status_entrada')=="Pendente" else 1, key=f"ve_{p['id']}")
            v_f = f3.selectbox("FINAL (50%)", ["Pendente", "Recebido"], index=0 if p.get('status_final')=="Pendente" else 1, key=f"vf_{p['id']}")
            
            st.write("---")
            # BOTÕES COM TEXTO COMPLETO E FUNCIONALIDADE INTEGRAL
            b1, b2, b3, b4 = st.columns(4)
            if b1.button("💾 ATUALIZAR TUDO", key=f"up_{p['id']}"):
                supabase.table("projetos").update({"nome_projeto":ed_nome_p, "cliente":ed_cliente, "cpf_cnpj":ed_doc, "whatsapp_cliente":ed_zap, "endereco_cliente":ed_end, "exigencias":ed_exig, "valor_total":ed_valor, "prazo":ed_prazo, "descricao":ed_desc, "status_total":v_t, "status_entrada":v_e, "status_final":v_f}).eq("id", p['id']).execute(); st.rerun()
            b2.download_button("📄 GERAR ORÇAMENTO", gerar_pdf("ORC", p, config), f"Orc_{p['id']}.pdf", key=f"bo_{p['id']}")
            b3.download_button("🧾 GERAR RECIBO", gerar_pdf("REC", p, config), f"Rec_{p['id']}.pdf", key=f"br_{p['id']}")
            b4.download_button("📜 GERAR CONTRATO", gerar_pdf("CONTRATO", p, config), f"Con_{p['id']}.pdf", key=f"bc_{p['id']}")

elif menu == "NOVO ORÇAMENTO":
    st.title("➕ NOVO ORÇAMENTO")
    with st.form("orc_form"):
        c_nome = st.text_input("Nome do Cliente")
        p_nome = st.text_input("Nome do Projeto")
        p_valor = st.number_input("Valor Total", step=0.01)
        if st.form_submit_button("SALVAR"):
            if c_nome and p_nome:
                supabase.table("projetos").insert({"cliente":c_nome, "nome_projeto":p_nome, "valor_total":p_valor, "status_total":"Pendente", "status_entrada":"Pendente", "status_final":"Pendente"}).execute()
                st.success("Salvo com sucesso!"); st.rerun()

elif menu == "CONFIGURAÇOES":
    st.title("⚙️ CONFIGURAÇÕES")
    _, config = carregar_dados()
    with st.form("cfg"):
        n_e = st.text_input("Empresa", config.get('nome_empresa', ''))
        w_e = st.text_input("WhatsApp", config.get('whatsapp', ''))
        e_e = st.text_input("E-mail", config.get('email', ''))
        if st.form_submit_button("SALVAR"):
            supabase.table("configuracoes").update({"nome_empresa":n_e, "whatsapp":w_e, "email":e_e}).eq("id", 1).execute(); st.rerun()
