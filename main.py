import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURAÇÃO E BLINDAGEM VISUAL (PJ GOLD) ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- 2. CONEXÃO SUPABASE (LOGICA INTACTA) ---
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "sb_publishable_qisG5bDBD-AxpBKW9LmBnA_p-_M671n"

try:
    supabase: Client = create_client(URL, KEY)
except Exception:
    st.error("Erro crítico de conexão.")
    st.stop()

# --- 3. CSS PRETO E OURO (INTERFACE LACRADA) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #121212 !important; border-right: 2px solid #D4AF37 !important; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p { color: #D4AF37 !important; font-weight: bold !important; font-size: 1.1rem !important; }
    h1, h2, h3, label { color: #D4AF37 !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.8rem !important; font-weight: bold; }
    .stButton>button { background-color: #D4AF37 !important; color: black !important; font-weight: bold !important; border-radius: 10px !important; }
    .stExpander { border: 1px solid #D4AF37 !important; background-color: #121212 !important; }
    </style>
    """, unsafe_allow_html=True)

def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data if proj.data else [], conf.data[0] if conf.data else {}
    except Exception: return [], {}

# --- 4. GERAÇÃO DE DOCUMENTOS (IDENTIDADE TOTAL) ---
def gerar_pdf(tipo, p, c):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Ouro PJ Studio (Padronizado)
    pdf.set_fill_color(212, 175, 55) 
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 12, f"{c.get('nome_empresa', 'PJ Studio Design')}", ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"CNPJ/CPF: {c.get('cpf_cnpj', '')} | WhatsApp: {c.get('whatsapp', '')} | E-mail: {c.get('email', '')}", ln=True, align='C')
    pdf.cell(0, 5, f"Endereço: {c.get('endereco', '')}", ln=True, align='C')
    pdf.ln(12)
    pdf.set_text_color(0, 0, 0)

    if tipo == "CONTRATO":
        # CONTRATO IDÊNTICO AO MODELO DE UMA PÁGINA
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS", ln=True, align='C')
        pdf.ln(5)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, f"CONTRATANTE: {p.get('cliente')}", ln=True)
        pdf.cell(0, 6, f"CPF/CNPJ: {p.get('cpf_cnpj', 'N/I')}", ln=True)
        pdf.cell(0, 6, f"CONTRATADO: {c.get('nome_empresa')} | {c.get('email')} | WhatsApp: {c.get('whatsapp')} | {c.get('endereco', '').split('-')[-1].strip()}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 11); pdf.write(6, "1. OBJETO: "); pdf.set_font("Arial", '', 11)
        pdf.write(6, f"Prestação de serviços de design gráfico ({p.get('descricao', 'logos, artes digitais e materiais gráficos')}).\n")
        
        pdf.set_font("Arial", 'B', 11); pdf.write(6, "2. PRAZO: "); pdf.set_font("Arial", '', 11)
        pdf.write(6, f"O prazo será de {p.get('prazo', 'combinar')}, iniciando após confirmação do pagamento da entrada.\n")
        
        pdf.set_font("Arial", 'B', 11); pdf.write(6, "3. VALOR E PAGAMENTO: \n"); pdf.set_font("Arial", '', 11)
        pdf.write(6, f"Valor total: R$ {float(p.get('valor_total', 0)):,.2f}\n")
        pdf.write(6, "Pagamento em duas etapas:\n• 50% na contratação (entrada para início do serviço).\n• 50% restantes na entrega final do material aprovado.\nOs arquivos finais sem marca d'água serão entregues após a quitação total.\n")
        
        pdf.set_font("Arial", 'B', 11); pdf.write(6, "4. ALTERAÇÕES: "); pdf.set_font("Arial", '', 11)
        pdf.write(6, "Inclui até 2 revisões simples. Alterações adicionais poderão ser cobradas.\n")
        
        pdf.set_font("Arial", 'B', 11); pdf.write(6, "5. DIREITOS DE USO: "); pdf.set_font("Arial", '', 11)
        pdf.write(6, f"Após pagamento integral, o cliente {p.get('cliente')} terá direito de uso do material. O PJ Studio Design poderá utilizar o material em portfólio.\n")
        
        pdf.set_font("Arial", 'B', 11); pdf.write(6, "6. CANCELAMENTO: "); pdf.set_font("Arial", '', 11)
        pdf.write(6, "Cancelamento após início do serviço não gera reembolso da entrada.\n")
        
        pdf.set_font("Arial", 'B', 11); pdf.write(6, "7. VALIDADE: "); pdf.set_font("Arial", '', 11)
        pdf.write(6, "Este contrato passa a valer após assinatura das partes.\n")
        
        pdf.ln(10)
        pdf.cell(0, 10, f"Local/Data: Barra Mansa - RJ, {datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(15)
        pdf.cell(95, 10, "__________________________", 0, 0, 'C'); pdf.cell(95, 10, "__________________________", 0, 1, 'C')
        pdf.cell(95, 5, "Contratante", 0, 0, 'C'); pdf.cell(95, 5, c.get('nome_empresa'), 0, 1, 'C')

    elif tipo == "ORC":
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"ORÇAMENTO PROFISSIONAL: {p.get('nome_projeto')}", ln=True)
        pdf.line(10, 56, 200, 56); pdf.ln(8)
        pdf.set_font("Arial", 'B', 11); pdf.cell(0, 6, "DADOS DO CLIENTE:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, f"Cliente: {p.get('cliente')}", ln=True)
        pdf.cell(0, 6, f"Endereço: {p.get('endereco_cliente', 'N/A')}", ln=True)
        pdf.cell(0, 6, f"Prazo: {p.get('prazo', 'A combinar')}", ln=True)
        pdf.cell(0, 6, f"Exigências: {p.get('exigencias', 'N/A')}", ln=True)
        pdf.multi_cell(0, 6, f"Descrição: {p.get('descricao')}")
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, f"VALOR TOTAL: R$ {float(p.get('valor_total', 0)):,.2f}", align='R')

    elif tipo == "REC":
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"RECIBO DE PAGAMENTO: {p.get('nome_projeto')}", ln=True)
        pdf.line(10, 56, 200, 56); pdf.ln(8)
        pdf.set_font("Arial", 'B', 11); pdf.cell(0, 6, "DADOS DO CLIENTE:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, f"Cliente: {p.get('cliente')}", ln=True)
        pdf.cell(0, 6, f"Documento: {p.get('cpf_cnpj', 'N/I')}", ln=True)
        pdf.cell(0, 6, f"WhatsApp: {p.get('whatsapp_cliente', 'N/I')}", ln=True)
        pdf.ln(5); pdf.set_font("Arial", 'B', 11); pdf.cell(0, 6, "DECLARAÇÃO DE RECEBIMENTO:", ln=True)
        pdf.set_font("Arial", '', 11)
        
        valor_base = float(p.get('valor_total', 0))
        if p.get('status_total') == 'Recebido':
            txt = f"QUITAÇÃO INTEGRAL do projeto {p.get('nome_projeto')}."
            v_doc = valor_base
        elif p.get('status_final') == 'Recebido':
            txt = f"PAGAMENTO FINAL (50%) do projeto {p.get('nome_projeto')}."
            v_doc = valor_base / 2
        else:
            txt = f"ENTRADA (50%) do projeto {p.get('nome_projeto')}."
            v_doc = valor_base / 2
            
        pdf.multi_cell(0, 7, f"Recebemos a importância de R$ {v_doc:,.2f} referente à {txt}")
        pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, f"VALOR TOTAL: R$ {valor_base:,.2f}", align='R')

    return pdf.output(dest='S').encode('latin-1')

# --- 5. INTERFACE ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚜️ PJ STUDIO</h2>", unsafe_allow_html=True)
    menu = st.radio("MENU", ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"], label_visibility="collapsed")

if menu == "PAINEL":
    st.title("⚜️ PAINEL DE CONTROLE")
    projs, _ = carregar_dados()
    no_bolso = sum([float(p['valor_total']) if p['status_total']=='Recebido' else (float(p['valor_total'])/2 if p['status_entrada']=='Recebido' else 0) + (float(p['valor_total'])/2 if p['status_final']=='Recebido' else 0) for p in projs])
    total = sum([float(p['valor_total']) for p in projs])
    c1, c2 = st.columns(2)
    c1.metric("💰 NO BOLSO", f"R$ {no_bolso:,.2f}")
    c2.metric("⏳ A RECEBER", f"R$ {total-no_bolso:,.2f}")

elif menu == "NOVO ORÇAMENTO":
    st.title("➕ NOVO ORÇAMENTO")
    with st.form("f_orc"):
        nome = st.text_input("Cliente")
        col1, col2 = st.columns(2)
        doc = col1.text_input("CPF/CNPJ")
        zap = col2.text_input("WhatsApp")
        end_cli = st.text_input("Endereço do Cliente")
        proj = st.text_input("Projeto")
        exig = st.text_input("Exigências")
        prazo = st.text_input("Prazo (ex: 20 dias úteis)") # RESTAURAÇÃO DO PRAZO
        val = st.number_input("Valor Total", step=0.01)
        if st.form_submit_button("SALVAR"):
            supabase.table("projetos").insert({"cliente":nome, "cpf_cnpj":doc, "whatsapp_cliente":zap, "endereco_cliente":end_cli, "nome_projeto":proj, "exigencias":exig, "prazo":prazo, "valor_total":val, "status_total":"Pendente", "status_entrada":"Pendente", "status_final":"Pendente"}).execute()
            st.rerun()

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO DE PROJETOS")
    projs, config = carregar_dados()
    for p in projs:
        with st.expander(f"📌 {p['nome_projeto']} - {p['cliente']}"):
            # RESTAURAÇÃO COMPLETA DA EDIÇÃO
            with st.form(f"edit_{p['id']}"):
                col_a, col_b = st.columns(2)
                e_nome = col_a.text_input("Cliente", p['cliente'])
                e_doc = col_b.text_input("CPF/CNPJ", p['cpf_cnpj'])
                e_end = st.text_input("Endereço", p.get('endereco_cliente', ''))
                e_proj = st.text_input("Nome do Projeto", p['nome_projeto'])
                col_c, col_d = st.columns(2)
                e_v = col_c.number_input("Valor Total", value=float(p['valor_total']))
                e_p = col_d.text_input("Prazo", p.get('prazo', ''))
                
                f1, f2, f3 = st.columns(3)
                v_t = f1.selectbox("TOTAL", ["Pendente", "Recebido"], index=0 if p['status_total']=="Pendente" else 1)
                v_e = f2.selectbox("ENTRADA (50%)", ["Pendente", "Recebido"], index=0 if p['status_entrada']=="Pendente" else 1)
                v_f = f3.selectbox("FINAL (50%)", ["Pendente", "Recebido"], index=0 if p['status_final']=="Pendente" else 1)
                
                if st.form_submit_button("💾 SALVAR ALTERAÇÕES"):
                    supabase.table("projetos").update({"cliente":e_nome, "cpf_cnpj":e_doc, "endereco_cliente":e_end, "nome_projeto":e_proj, "valor_total":e_v, "prazo":e_p, "status_total":v_t, "status_entrada":v_e, "status_final":v_f}).eq("id", p['id']).execute()
                    st.rerun()
            
            st.markdown("---")
            b1, b2, b3, b4 = st.columns(4)
            b1.download_button("📄 ORÇAMENTO", gerar_pdf("ORC", p, config), f"Orc_{p['id']}.pdf")
            b2.download_button("🧾 RECIBO", gerar_pdf("REC", p, config), f"Rec_{p['id']}.pdf")
            b3.download_button("📜 CONTRATO", gerar_pdf("CONTRATO", p, config), f"Con_{p['id']}.pdf")
            if b4.button("🗑️ EXCLUIR", key=f"d_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute(); st.rerun()

elif menu == "CONFIGURAÇOES":
    st.title("⚙️ CONFIGURAÇÕES")
    _, config = carregar_dados()
    with st.form("f_cfg"):
        n = st.text_input("Empresa", config.get('nome_empresa', ''))
        c = st.text_input("CNPJ", config.get('cpf_cnpj', ''))
        w = st.text_input("WhatsApp", config.get('whatsapp', ''))
        e = st.text_input("E-mail", config.get('email', ''))
        ed = st.text_area("Endereço", config.get('endereco', ''))
        if st.form_submit_button("SALVAR"):
            supabase.table("configuracoes").update({"nome_empresa":n, "cpf_cnpj":c, "whatsapp":w, "email":e, "endereco":ed}).eq("id", 1).execute(); st.rerun()
