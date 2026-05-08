import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
from datetime import datetime
import time

# --- 1. CONFIGURAÇÃO E BLINDAGEM VISUAL (LACRADO) ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- 2. CONEXÃO SUPABASE (LACRADA - SEUS DADOS ORIGINAIS) ---
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

# --- 4. FUNÇÕES DE DADOS (LACRADAS) ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data if proj.data else [], conf.data[0] if conf.data else {}
    except Exception: return [], {}

# --- 5. GERAÇÃO DE PDF (REFINAMENTO MINUCIOSO DOS DOCUMENTOS) ---
def gerar_pdf(tipo, p, c):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Ouro
    pdf.set_fill_color(212, 175, 55) 
    pdf.rect(0, 0, 210, 45, 'F')
    
    # Dados da Empresa (Configurações)
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
        pdf.multi_cell(0, 6, f"ENDEREÇO: {p.get('endereco_cliente', 'N/I')}")
        pdf.ln(4)

        valor_total = float(p.get('valor_total', 0))
        valor_entrada = valor_total / 2
        clausulas = [
            f"1. OBJETO: Prestação de serviços de design gráfico ({p.get('nome_projeto', '')}).",
            f"2. DESCRIÇÃO: {p.get('descricao', 'Conforme acordado')}.",
            f"3. PRAZO: {p.get('prazo', 'A combinar')}, contados após o pagamento da entrada.",
            f"4. VALOR E PAGAMENTO: Valor total: R$ {valor_total:,.2f}. Pagamento em duas etapas: 50% na contratação (R$ {valor_entrada:,.2f} - entrada para início do serviço) e 50% restantes (R$ {valor_entrada:,.2f}) na entrega final do material aprovado. Os arquivos finais sem marca d'água serão entregues somente após a quitação total.",
            f"5. EXIGÊNCIAS ESPECÍFICAS: {p.get('exigencias', 'Nenhuma')}.",
            "6. ALTERAÇÕES: O projeto inclui até 2 (duas) revisões simples sem custo adicional. Alterações adicionais poderão ser cobradas.",
            "7. DIREITOS DE USO: Após pagamento integral, o cliente terá direito de uso do material. O PJ Studio Design poderá utilizar o material em portfólio.",
            "8. CANCELAMENTO: Em caso de desistência após início do serviço, o valor da entrada não será devolvido.",
            "9. VALIDADE: Este contrato passa a valer após assinatura das partes."
        ]
        for item in clausulas: 
            pdf.multi_cell(0, 6, item)
            pdf.ln(1)
            
        pdf.ln(10)
        pdf.cell(0, 10, f"Local/Data: Barra Mansa - RJ, {datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(15)
        pdf.cell(95, 10, "__________________________", 0, 0, 'C')
        pdf.cell(95, 10, "__________________________", 0, 1, 'C')
        pdf.cell(95, 5, "Contratante", 0, 0, 'C')
        pdf.cell(95, 5, c.get('nome_empresa'), 0, 1, 'C')
    
    elif tipo == "ORC":
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"ORÇAMENTO PROFISSIONAL: {p.get('nome_projeto')}", ln=True)
        pdf.line(10, 55, 200, 55)
        pdf.ln(5)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, f"Cliente: {p.get('cliente')}", ln=True)
        pdf.cell(0, 6, f"Doc: {p.get('cpf_cnpj', 'N/I')} | Zap: {p.get('whatsapp_cliente', 'N/I')}", ln=True)
        pdf.cell(0, 6, f"Prazo: {p.get('prazo', 'A combinar')}", ln=True)
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 6, "Detalhamento:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, f"Exigências: {p.get('exigencias', 'Nenhuma')}")
        pdf.multi_cell(0, 6, f"Descrição do Serviço: {p.get('descricao', '')}")
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 13)
        pdf.cell(0, 10, f"INVESTIMENTO TOTAL: R$ {float(p.get('valor_total', 0)):,.2f}", ln=True, align='R')

    elif tipo == "REC":
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "RECIBO DE PAGAMENTO", ln=True, align='L')
        pdf.set_font("Arial", 'I', 11)
        pdf.cell(0, 8, f"Referente ao Projeto: {p.get('nome_projeto')}", ln=True, align='L')
        pdf.line(10, 65, 200, 65)
        pdf.ln(10)
        
        valor = float(p.get('valor_total', 0))
        
        pdf.set_font("Arial", '', 12)
        if p.get('status_total') == 'Recebido':
            txt_principal = f"Recebemos de {p.get('cliente')} ({p.get('cpf_cnpj', 'N/I')})"
            txt_valor = f"a importância total de R$ {valor:,.2f}"
            txt_detalhe = "referente à QUITAÇÃO INTEGRAL dos serviços de design gráfico prestados."
        elif p.get('status_entrada') == 'Recebido' and p.get('status_final') == 'Pendente':
            txt_principal = f"Recebemos de {p.get('cliente')} ({p.get('cpf_cnpj', 'N/I')})"
            txt_valor = f"a importância de R$ {valor/2:,.2f}"
            txt_detalhe = "referente ao pagamento de ENTRADA (50%) para início da execução do projeto."
        else:
            txt_principal = f"Recebemos de {p.get('cliente')} ({p.get('cpf_cnpj', 'N/I')})"
            txt_valor = f"a importância de R$ {valor/2:,.2f}"
            txt_detalhe = "referente ao pagamento FINAL (50%) e entrega definitiva dos arquivos do projeto."
            
        pdf.multi_cell(0, 8, txt_principal)
        pdf.set_font("Arial", 'B', 12)
        pdf.multi_cell(0, 8, txt_valor)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 8, txt_detalhe)
        
        pdf.ln(15)
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f"Documento emitido em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", ln=True, align='R')
        pdf.ln(20)
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, "________________________________________________", ln=True, align='C')
        pdf.cell(0, 5, c.get('nome_empresa'), ln=True, align='C')
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 5, "Representante Legal", ln=True, align='C')

    elif tipo == "MANUTENCAO":
        # ======================================================
        # RECIBO DE MANUTENÇÃO / SERVIÇO EXTRA — NOVO
        # ======================================================
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "RECIBO DE SERVIÇO EXTRA / MANUTENÇÃO", ln=True, align='L')
        pdf.set_font("Arial", 'I', 11)
        pdf.cell(0, 8, f"Referente ao Projeto: {p.get('nome_projeto')}", ln=True, align='L')
        pdf.line(10, 65, 200, 65)
        pdf.ln(10)

        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 8, f"Recebemos de {p.get('cliente')} ({p.get('cpf_cnpj', 'N/I')})")
        pdf.set_font("Arial", 'B', 12)
        pdf.multi_cell(0, 8, f"a importância de R$ {float(p.get('valor_manutencao', 0)):,.2f}")
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 8, "referente ao pagamento INTEGRAL pelo serviço extra / manutenção descrito abaixo:")
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "Descrição do Serviço:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 7, f"{p.get('desc_manutencao', 'Serviço extra conforme acordado.')}")
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 13)
        pdf.cell(0, 10, f"VALOR PAGO: R$ {float(p.get('valor_manutencao', 0)):,.2f}", ln=True, align='R')
        pdf.ln(3)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, "Pagamento efetuado à vista — quitado integralmente.", ln=True, align='R')

        pdf.ln(15)
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f"Documento emitido em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", ln=True, align='R')
        pdf.ln(20)

        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, "________________________________________________", ln=True, align='C')
        pdf.cell(0, 5, c.get('nome_empresa'), ln=True, align='C')
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 5, "Representante Legal", ln=True, align='C')
        # ======================================================

    return pdf.output(dest='S').encode('latin-1')

# --- 6. NAVEGAÇÃO (LACRADO) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚜️ PJ STUDIO</h2>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("NAVEGAÇÃO", ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"], label_visibility="collapsed")

# --- 7. TELAS (LACRADAS) ---
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
    if 'last_submit_time' not in st.session_state: st.session_state.last_submit_time = 0

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
        btn_salvar = st.form_submit_button("SALVAR ORÇAMENTO")
        
        if btn_salvar:
            current_time = time.time()
            if current_time - st.session_state.last_submit_time > 2:
                if c_nome and p_nome:
                    try:
                        st.session_state.last_submit_time = current_time
                        supabase.table("projetos").insert({
                            "cliente":c_nome, "cpf_cnpj":c_doc, "whatsapp_cliente":c_zap, 
                            "endereco_cliente":c_end, "nome_projeto":p_nome, "exigencias":p_exig, 
                            "valor_total":p_valor, "prazo":p_prazo, "descricao":p_desc, 
                            "status_total":"Pendente", "status_entrada":"Pendente", "status_final":"Pendente"
                        }).execute()
                        st.success("Orçamento salvo com sucesso!")
                        st.rerun()
                    except Exception as e: st.error(f"Erro ao salvar: {e}")
                else: st.warning("Preencha cliente e projeto.")
            else: st.info("Processando...")

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO E EDIÇÃO")
    projetos, config = carregar_dados()
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | {p.get('cliente')}"):
            ed_nome_p = st.text_input("Nome do Projeto", p.get('nome_projeto'), key=f"p_{p['id']}")
            ed_cliente = st.text_input("Nome do Cliente", p.get('cliente'), key=f"c_{p['id']}")
            
            c_ed1, c_ed2 = st.columns(2)
            ed_doc = c_ed1.text_input("CPF/CNPJ", p.get('cpf_cnpj', ''), key=f"d_{p['id']}")
            ed_zap = c_ed2.text_input("WhatsApp", p.get('whatsapp_cliente', ''), key=f"z_{p['id']}")
            
            ed_end = st.text_input("Endereço do Cliente Completo", p.get('endereco_cliente', ''), key=f"e_{p['id']}")
            ed_exig = st.text_input("Exigências do Cliente", p.get('exigencias', ''), key=f"x_{p['id']}")
            
            c_ed3, c_ed4 = st.columns(2)
            ed_valor = c_ed3.number_input("Valor Total", value=float(p.get('valor_total', 0)), step=0.01, key=f"v_{p['id']}")
            ed_prazo = c_ed4.text_input("Prazo de Entrega", p.get('prazo', ''), key=f"pr_{p['id']}")
            
            ed_desc = st.text_area("Descrição do Serviço", p.get('descricao', ''), key=f"ds_{p['id']}")
            
            st.write("---")
            st.write("**Controle de Pagamentos (50/50)**")
            f1, f2, f3 = st.columns(3)
            v_t = f1.selectbox("VALOR TOTAL", ["Pendente", "Recebido"], index=0 if p.get('status_total')=="Pendente" else 1, key=f"vt_{p['id']}")
            v_e = f2.selectbox("ENTRADA (50%)", ["Pendente", "Recebido"], index=0 if p.get('status_entrada')=="Pendente" else 1, key=f"ve_{p['id']}")
            v_f = f3.selectbox("FINAL (50%)", ["Pendente", "Recebido"], index=0 if p.get('status_final')=="Pendente" else 1, key=f"vf_{p['id']}")
            
            st.write("---")
            b1, b2, b3, b4, b5 = st.columns(5)
            if b1.button("💾 ATUALIZAR", key=f"up_{p['id']}"):
                supabase.table("projetos").update({
                    "nome_projeto":ed_nome_p, "cliente":ed_cliente, "cpf_cnpj":ed_doc, 
                    "whatsapp_cliente":ed_zap, "endereco_cliente":ed_end, "exigencias":ed_exig, 
                    "valor_total":ed_valor, "prazo":ed_prazo, "descricao":ed_desc,
                    "status_total":v_t, "status_entrada":v_e, "status_final":v_f
                }).eq("id", p['id']).execute(); st.rerun()
            
            b2.download_button("📄 ORÇAMENTO", gerar_pdf("ORC", p, config), f"Orc_{p['id']}.pdf", key=f"bo_{p['id']}")
            b3.download_button("🧾 RECIBO", gerar_pdf("REC", p, config), f"Rec_{p['id']}.pdf", key=f"br_{p['id']}")
            b4.download_button("📜 CONTRATO", gerar_pdf("CONTRATO", p, config), f"Con_{p['id']}.pdf", key=f"bc_{p['id']}")
            if b5.button("🗑️ EXCLUIR", key=f"del_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute(); st.rerun()

            # ======================================================
            # SEÇÃO MANUTENÇÃO / SERVIÇO EXTRA — ÚNICO ACRÉSCIMO
            # ======================================================
            st.write("---")
            st.write("**🔧 Serviço Extra / Manutenção**")
            man_col1, man_col2 = st.columns([3, 1])
            man_desc = man_col1.text_input(
                "Descrição do Serviço Extra",
                placeholder="Ex: Atualização de cardápio, ajuste de arte...",
                key=f"mdesc_{p['id']}"
            )
            man_valor = man_col2.number_input("Valor (R$)", min_value=0.0, step=0.01, key=f"mval_{p['id']}")

            if man_desc and man_valor > 0:
                dados_manutencao = {**p, "desc_manutencao": man_desc, "valor_manutencao": man_valor}
                st.download_button(
                    "🔧 GERAR RECIBO DE MANUTENÇÃO",
                    gerar_pdf("MANUTENCAO", dados_manutencao, config),
                    f"Manutencao_{p['id']}.pdf",
                    key=f"bm_{p['id']}"
                )
            # ======================================================

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
