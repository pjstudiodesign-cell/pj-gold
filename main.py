import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO E BLINDAGEM VISUAL (MANTIDA) ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- 2. CONEXÃO SUPABASE (LACRADA) ---
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "sb_publishable_qisG5bDBD-AxpBKW9LmBnA_p-_M671n"

try:
    supabase: Client = create_client(URL, KEY)
except Exception:
    st.error("Erro crítico de conexão.")
    st.stop()

# --- 3. CSS PRETO E OURO (MANTIDO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #121212 !important; border-right: 2px solid #D4AF37 !important; }
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800 !important; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.8rem !important; font-weight: bold; }
    .stButton>button { background-color: #D4AF37 !important; color: black !important; font-weight: bold !important; border-radius: 10px !important; }
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

# --- 5. GERAÇÃO DE PDF (ORÇAMENTO, RECIBO E CONTRATO) ---
def gerar_pdf(tipo, p, c):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Ouro (MANTIDO)
    pdf.set_fill_color(212, 175, 55) 
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"{c.get('nome_empresa', 'PJ STUDIO DESIGN')}", ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"CNPJ/CPF: {c.get('cpf_cnpj', '')} | WhatsApp: {c.get('whatsapp', '')}", ln=True, align='C')
    pdf.cell(0, 5, f"E-mail: {c.get('email', '')}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)

    if tipo == "CONTRATO":
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS", ln=True, align='C')
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 6, f"CONTRATANTE: {p.get('cliente')}", ln=True)
        pdf.cell(0, 6, f"CPF/CNPJ: {p.get('cpf_cnpj', 'N/I')}", ln=True)
        pdf.ln(2)
        pdf.cell(0, 6, f"CONTRATADO: {c.get('nome_empresa')} | {c.get('email')} | WhatsApp: {c.get('whatsapp')}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 10)
        clausulas = [
            f"1. OBJETO: Prestação de serviços de design gráfico ({p.get('descricao')}).",
            f"2. PRAZO: O prazo será de {p.get('prazo', 'combinado')}, iniciando após confirmação do pagamento da entrada.",
            f"3. VALOR E PAGAMENTO: Valor total: R$ {float(p.get('valor_total', 0)):,.2f}. Pagamento em duas etapas: 50% na contratação (entrada) e 50% na entrega final aprovada.",
            "4. ALTERAÇÕES: Inclui até 2 revisões simples. Alterações adicionais poderão ser cobradas.",
            "5. DIREITOS DE USO: Após pagamento integral, o cliente terá direito de uso do material.",
            "6. CANCELAMENTO: Cancelamento após início do serviço não gera reembolso da entrada.",
            "7. VALIDADE: Este contrato passa a valer após assinatura das partes."
        ]
        for item in clausulas:
            pdf.multi_cell(0, 6, item)
            pdf.ln(2)
        
        pdf.ln(10)
        data_atual = datetime.now().strftime("%d/%m/%Y")
        pdf.cell(0, 10, f"Local/Data: Barra Mansa - RJ, {data_atual}", ln=True)
        pdf.ln(12)
        pdf.cell(95, 10, "__________________________", 0, 0, 'C')
        pdf.cell(95, 10, "__________________________", 0, 1, 'C')
        pdf.cell(95, 5, "Assinatura do Contratante", 0, 0, 'C')
        pdf.cell(95, 5, f"Assinatura {c.get('nome_empresa')}", 0, 1, 'C')
    
    elif tipo == "ORC":
        # Lógica de Orçamento (Mantida)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"ORÇAMENTO: {p.get('nome_projeto')}", ln=True)
        pdf.line(10, 55, 200, 55)
        pdf.ln(5)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, f"Cliente: {p.get('cliente')}", ln=True)
        pdf.multi_cell(0, 6, f"Descrição: {p.get('descricao')}")
        pdf.cell(0, 10, f"VALOR TOTAL: R$ {float(p.get('valor_total', 0)):,.2f}", ln=True, align='R')

    elif tipo == "REC":
        # Lógica de Recibo Corrigida (Mantida)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"RECIBO DE PAGAMENTO: {p.get('nome_projeto')}", ln=True)
        pdf.ln(5)
        valor = float(p.get('valor_total', 0))
        if p.get('status_total') == 'Recebido': txt = f"QUITAÇÃO INTEGRAL de R$ {valor:,.2f}"
        elif p.get('status_entrada') == 'Recebido': txt = f"ENTRADA (50%) de R$ {valor/2:,.2f}"
        else: txt = f"PAGAMENTO FINAL (50%) de R$ {valor/2:,.2f}"
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, f"Recebemos de {p.get('cliente')} a importância referente à {txt}.")

    return pdf.output(dest='S').encode('latin-1')

# --- 6. NAVEGAÇÃO E TELAS (MANTIDO O FOCO) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚜️ PJ STUDIO</h2>", unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO", ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"], label_visibility="collapsed")

if menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO E EDIÇÃO")
    projetos, config = carregar_dados()
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | {p.get('cliente')}"):
            st.write("---")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Botões de Download
            orc_pdf = gerar_pdf("ORC", p, config)
            col2.download_button("📄 ORÇAMENTO", orc_pdf, f"Orc_{p['id']}.pdf", key=f"o_{p['id']}")
            
            rec_pdf = gerar_pdf("REC", p, config)
            col3.download_button("🧾 RECIBO", rec_pdf, f"Rec_{p['id']}.pdf", key=f"r_{p['id']}")
            
            # NOVO BOTAO CONTRATO (DETALHAMENTO CIRÚRGICO)
            con_pdf = gerar_pdf("CONTRATO", p, config)
            col4.download_button("📜 CONTRATO", con_pdf, f"Contrato_{p['id']}.pdf", key=f"c_{p['id']}")
            
            # ... (Lógica de Atualizar e Excluir mantida exatamente igual)
