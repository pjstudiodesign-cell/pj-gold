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
    st.error("ERRO DE CONEXÃO: O sistema não detectou as chaves. Verifique o Render.")
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

# --- 5. GERAÇÃO DE PDF (CONTRATO IDENTICO AO MODELO ENVIADO) ---
def gerar_pdf(tipo, p, c):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Ouro do Studio
    pdf.set_fill_color(212, 175, 55) 
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 20, "PJ STUDIO DESIGN", ln=True, align='C')
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)

    if tipo == "CONTRATO":
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS", ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 11)
        # Preenchimento Automático do Contratante
        pdf.multi_cell(0, 7, f"CONTRATANTE: {p.get('cliente')} | CPF/CNPJ: {p.get('cpf_cnpj', 'N/I')}")
        pdf.multi_cell(0, 7, f"CONTRATADO: {c.get('nome_empresa', 'PJ Studio Design')} | {c.get('email', '')} | WhatsApp: {c.get('whatsapp', '')}")
        pdf.ln(5)
        
        # Cláusulas idênticas ao modelo enviado
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, "1. OBJETO:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, f"Prestação de serviços de design gráfico ({p.get('nome_projeto', '')}).")
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, "2. PRAZO:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, f"O prazo será combinado entre as partes, iniciando após confirmação do pagamento da entrada. Prazo estimado: {p.get('prazo', 'A combinar')}.")
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, "3. VALOR E PAGAMENTO:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, f"Valor total: R$ {float(p.get('valor_total', 0)):,.2f}", ln=True)
        pdf.multi_cell(0, 6, "Pagamento em duas etapas:\n• 50% na contratação (entrada para início do serviço).\n• 50% restantes na entrega final do material aprovado.")
        pdf.multi_cell(0, 6, "Os arquivos finais sem marca d'água serão entregues após a quitação total.")
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, "4. ALTERAÇÕES:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, "Inclui até 2 revisões simples. Alterações adicionais poderão ser cobradas.")
        
        # Cláusula de Portfólio Preservada
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, "5. DIREITOS DE USO:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, f"Após pagamento integral, o cliente terá direito de uso do material. O {c.get('nome_empresa', 'PJ Studio Design')} poderá utilizar o material em portfólio.")
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, "6. CANCELAMENTO:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, "Cancelamento após início do serviço não gera reembolso da entrada.")
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, "7. VALIDADE:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, "Este contrato passa a valer após assinatura das partes.")
        
        pdf.ln(10)
        pdf.cell(0, 10, f"Local/Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(15)
        pdf.cell(95, 10, "__________________________", 0, 0, 'C')
        pdf.cell(95, 10, "__________________________", 0, 1, 'C')
        pdf.cell(95, 5, "Assinatura do Contratante", 0, 0, 'C')
        pdf.cell(95, 5, f"Assinatura {c.get('nome_empresa')}", 0, 1, 'C')
    
    elif tipo == "ORC":
        # (Lógica do Orçamento - LACRADA)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"ORÇAMENTO PROFISSIONAL: {p.get('nome_projeto')}", ln=True)
        pdf.line(10, 55, 200, 55); pdf.ln(5)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, f"Cliente: {p.get('cliente')}", ln=True)
        pdf.cell(0, 6, f"Doc: {p.get('cpf_cnpj', 'N/I')} | Zap: {p.get('whatsapp_cliente', 'N/I')}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, f"INVESTIMENTO TOTAL: R$ {float(p.get('valor_total', 0)):,.2f}", ln=True, align='R')

    elif tipo == "REC":
        # (Lógica do Recibo - LACRADA E PROFISSIONALIZADA)
        pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "RECIBO DE PAGAMENTO", ln=True)
        pdf.set_font("Arial", 'I', 11); pdf.cell(0, 8, f"Referente ao Projeto: {p.get('nome_projeto')}", ln=True)
        pdf.line(10, 65, 200, 65); pdf.ln(10)
        pdf.set_font("Arial", '', 12)
        v = float(p.get('valor_total', 0))
        if p.get('status_total') == 'Recebido': txt = f"recebemos a QUITAÇÃO INTEGRAL de R$ {v:,.2f}"
        else: txt = f"recebemos a importância de R$ {v/2:,.2f}"
        pdf.multi_cell(0, 8, f"Recebemos de {p.get('cliente')} ({p.get('cpf_cnpj', 'N/I')}), {txt}."); pdf.ln(20)
        pdf.cell(0, 5, c.get('nome_empresa'), ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')

# --- 6. NAVEGAÇÃO E TELAS (LACRADAS) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚜️ PJ STUDIO</h2>", unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO", ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"], label_visibility="collapsed")

if menu == "PAINEL":
    st.title("⚜️ PAINEL DE CONTROLE")
    # (Restante do motor - LACRADO)
    projetos, _ = carregar_dados()
    st.metric("💰 DINHEIRO NO BOLSO", f"R$ {sum([float(p.get('valor_total', 0)) for p in projetos if p.get('status_total') == 'Recebido']):,.2f}")

elif menu == "NOVO ORÇAMENTO":
    st.title("➕ NOVO ORÇAMENTO")
    with st.form("orc_form"):
        # (Formulário - LACRADO)
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
            st.write(f"Valor: R$ {float(p.get('valor_total', 0)):,.2f}")
            b1, b2, b3 = st.columns(3)
            b1.download_button("📄 ORÇAMENTO", gerar_pdf("ORC", p, config), f"Orc_{p['id']}.pdf")
            b2.download_button("🧾 RECIBO", gerar_pdf("REC", p, config), f"Rec_{p['id']}.pdf")
            b3.download_button("📜 CONTRATO", gerar_pdf("CONTRATO", p, config), f"Con_{p['id']}.pdf")

elif menu == "CONFIGURAÇOES":
    st.title("⚙️ CONFIGURAÇÕES")
    # (Configurações - LACRADAS)
    _, config = carregar_dados()
    with st.form("cfg"):
        n_e = st.text_input("Nome da Empresa", config.get('nome_empresa', ''))
        if st.form_submit_button("SALVAR"):
            supabase.table("configuracoes").update({"nome_empresa":n_e}).eq("id", 1).execute(); st.rerun()
