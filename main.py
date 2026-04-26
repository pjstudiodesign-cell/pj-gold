import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import io

# --- 1. CONFIGURAÇÃO E BLINDAGEM VISUAL ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- 2. CONEXÃO SUPABASE ---
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "sb_publishable_qisG5bDBD-AxpBKW9LmBnA_p-_M671n"

try:
    supabase: Client = create_client(URL, KEY)
except Exception:
    st.error("Erro crítico de conexão.")
    st.stop()

# --- 3. CSS PRETO E OURO (LACRADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #121212 !important; border-right: 2px solid #D4AF37 !important; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p { color: #D4AF37 !important; font-weight: bold !important; font-size: 1.1rem !important; }
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800 !important; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.8rem !important; font-weight: bold; }
    div[data-testid="stMetric"] { background-color: #1c1c1c; padding: 25px; border-radius: 15px; border: 2px solid #D4AF37; }
    .stButton>button { background-color: #D4AF37 !important; color: black !important; font-weight: bold !important; border-radius: 10px !important; }
    input, textarea, div[data-baseweb="select"] { background-color: #1c1c1c !important; color: white !important; border: 1px solid #444 !important; }
    label { color: #D4AF37 !important; font-weight: bold !important; }
    .stExpander { border: 1px solid #D4AF37 !important; background-color: #121212 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÕES DE DADOS E GERAÇÃO DE DOCUMENTOS ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data if proj.data else [], conf.data[0] if conf.data else {}
    except Exception: return [], {}

def criar_pdf_orcamento(p, c):
    pdf = FPDF()
    pdf.add_page()
    
    # --- CABEÇALHO DA EMPRESA (DADOS COMPLETOS DAS CONFIGURAÇÕES) ---
    pdf.set_fill_color(212, 175, 55) # Cor Ouro Profissional
    pdf.rect(0, 0, 210, 45, 'F')
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"{c.get('nome_empresa', 'PJ STUDIO')}", ln=True, align='C')
    
    pdf.set_font("Arial", '', 9)
    # Linha de Documento e Contato
    pdf.cell(0, 5, f"CNPJ/CPF: {c.get('cpf_cnpj', '')} | WhatsApp: {c.get('whatsapp', '')} | E-mail: {c.get('email', '')}", ln=True, align='C')
    # Linha de Endereço Completo
    pdf.multi_cell(0, 5, f"Endereço: {c.get('endereco', '')}", align='C')
    
    pdf.ln(15)
    
    # Título do Orçamento
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"ORÇAMENTO PROFISSIONAL: {p.get('nome_projeto')}", ln=True, align='L')
    pdf.line(10, 60, 200, 60)
    
    # Dados do Cliente
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "DADOS DO CLIENTE:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 6, f"Cliente: {p.get('cliente')}", ln=True)
    pdf.cell(0, 6, f"Documento: {p.get('cpf_cnpj', 'N/I')}", ln=True)
    pdf.cell(0, 6, f"WhatsApp: {p.get('whatsapp_cliente', 'N/I')}", ln=True)
    pdf.cell(0, 6, f"Endereço: {p.get('endereco', 'N/I')}", ln=True)
    
    # Detalhes do Serviço
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "DETALHES DO SERVIÇO:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 6, f"Descrição: {p.get('descricao', 'N/I')}")
    pdf.multi_cell(0, 6, f"Exigências: {p.get('exigencias', 'N/I')}")
    pdf.cell(0, 6, f"Prazo de Entrega: {p.get('prazo', 'A combinar')}", ln=True)
    
    # Rodapé Financeiro
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"VALOR TOTAL: R$ {float(p.get('valor_total', 0)):,.2f}", ln=True, align='R')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, "Condição: 50% de entrada e 50% na entrega final.", ln=True, align='R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. NAVEGAÇÃO (BLINDADA) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚜️ PJ STUDIO</h2>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("NAVEGAÇÃO", ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"], label_visibility="collapsed")

# --- 6. TELAS ---
if menu == "PAINEL":
    st.title("⚜️ PAINEL DE CONTROLE")
    projetos, _ = carregar_dados()
    no_bolso = sum([float(p.get('valor_total',0))/2 for p in projetos if p.get('status_entrada') == 'Recebido']) + \
               sum([float(p.get('valor_total',0))/2 for p in projetos if p.get('status_final') == 'Recebido'])
    a_receber = sum([float(p.get('valor_total',0)) for p in projetos]) - no_bolso
    c1, c2 = st.columns(2)
    c1.metric("💰 DINHEIRO NO BOLSO", f"R$ {no_bolso:,.2f}")
    c2.metric("⏳ CONTAS A RECEBER", f"R$ {a_receber:,.2f}")

elif menu == "NOVO ORÇAMENTO":
    st.title("➕ NOVO ORÇAMENTO")
    with st.form("orcamento_form"):
        st.subheader("Dados do Cliente")
        c_nome = st.text_input("Nome/Razão Social")
        col1, col2 = st.columns(2)
        c_doc = col1.text_input("CPF ou CNPJ (Cliente)")
        c_zap = col2.text_input("WhatsApp (Cliente)")
        c_mail = st.text_input("E-mail do Cliente")
        c_end = st.text_area("Endereço do Cliente")
        st.write("---")
        st.subheader("Detalhes do Serviço")
        p_nome = st.text_input("Nome do Projeto")
        col3, col4 = st.columns(2)
        p_valor = col3.number_input("Valor Total (R$)", min_value=0.0, step=0.01)
        p_prazo = col4.text_input("Prazo de Entrega")
        p_desc = st.text_area("Descrição do Serviço")
        p_exig = st.text_area("Exigências Específicas")
        if st.form_submit_button("GERAR E SALVAR ORÇAMENTO"):
            if c_nome and p_nome:
                supabase.table("projetos").insert({
                    "cliente": c_nome, "cpf_cnpj": c_doc, "whatsapp_cliente": c_zap,
                    "email_cliente": c_mail, "endereco": c_end, "nome_projeto": p_nome,
                    "valor_total": p_valor, "prazo": p_prazo, "descricao": p_desc, 
                    "exigencias": p_exig, "status_total": "Pendente", "status_entrada": "Pendente", "status_final": "Pendente"
                }).execute()
                st.success("✅ Orçamento salvo!")
                st.rerun()

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO E EDIÇÃO DE PROJETOS")
    projetos, config = carregar_dados()
    for p in projetos:
        with st.expander(f"📌 PROJETO: {p.get('nome_projeto')} | CLIENTE: {p.get('cliente')}"):
            col_ed1, col_ed2 = st.columns(2)
            novo_nome = col_ed1.text_input("Editar Nome Projeto", value=p.get('nome_projeto'), key=f"n_{p['id']}")
            novo_cliente = col_ed2.text_input("Editar Cliente", value=p.get('cliente'), key=f"c_{p['id']}")
            nova_desc = st.text_area("Editar Descrição", value=p.get('descricao'), key=f"d_{p['id']}")
            
            st.write("---")
            st.subheader("Controle de Pagamentos (50/50)")
            f1, f2, f3 = st.columns(3)
            v_total = f1.selectbox("VALOR TOTAL", ["Pendente", "Recebido"], index=0 if p.get('status_total') == "Pendente" else 1, key=f"st_{p['id']}")
            v_ent = f2.selectbox("ENTRADA (50%)", ["Pendente", "Recebido"], index=0 if p.get('status_entrada') == "Pendente" else 1, key=f"se_{p['id']}")
            v_fin = f3.selectbox("FINAL (50%)", ["Pendente", "Recebido"], index=0 if p.get('status_final') == "Pendente" else 1, key=f"sf_{p['id']}")
            
            st.write("---")
            b1, b2, b3, b4 = st.columns(4)
            if b1.button("💾 ATUALIZAR", key=f"upd_{p['id']}"):
                supabase.table("projetos").update({
                    "nome_projeto": novo_nome, "cliente": novo_cliente, "descricao": nova_desc,
                    "status_total": v_total, "status_entrada": v_ent, "status_final": v_fin
                }).eq("id", p['id']).execute()
                st.rerun()
            
            try:
                pdf_output = criar_pdf_orcamento(p, config)
                b2.download_button(label="📄 BAIXAR PDF", data=pdf_output, file_name=f"Orcamento_{p['cliente']}.pdf", mime="application/pdf", key=f"dl_{p['id']}")
            except:
                b2.error("Erro ao gerar PDF")
            
            if b3.button("🧾 RECIBO", key=f"rec_{p['id']}"):
                st.info("Função Recibo em integração...")
                
            if b4.button("🗑️ EXCLUIR", key=f"del_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute()
                st.rerun()

elif menu == "CONFIGURAÇOES":
    st.title("⚙️ DADOS DA MINHA EMPRESA")
    _, config = carregar_dados()
    with st.form("cfg"):
        n_emp = st.text_input("Nome da Empresa", value=config.get('nome_empresa', ''))
        c_emp = st.text_input("CPF ou CNPJ da Empresa", value=config.get('cpf_cnpj', ''))
        w_emp = st.text_input("WhatsApp Profissional", value=config.get('whatsapp', ''))
        e_emp = st.text_input("E-mail Profissional", value=config.get('email', ''))
        end_emp = st.text_area("Endereço Completo", value=config.get('endereco', ''))
        if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
            supabase.table("configuracoes").update({"nome_empresa": n_emp, "cpf_cnpj": c_emp, "whatsapp": w_emp, "email": e_emp, "endereco": end_emp}).eq("id", 1).execute()
            st.rerun()
