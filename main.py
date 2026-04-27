import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
from datetime import datetime

# ==========================================
# BLINDAGEM DE CONFIGURAÇÃO E CONEXÃO
# ==========================================
st.set_page_config(page_title="PJ GOLD PRO", layout="wide", page_icon="💰")

# Substitua pelas suas credenciais reais do Supabase
URL = "SUA_URL_DO_SUPABASE"
KEY = "SUA_KEY_DO_SUPABASE"

@st.cache_resource
def get_supabase() -> Client:
    return create_client(URL, KEY)

supabase = get_supabase()

# ==========================================
# ESTILIZAÇÃO PREMIUM (INTOCÁVEL)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #001f3f;
        color: #d4af37;
        font-weight: bold;
        border: 1px solid #d4af37;
    }
    .stButton>button:hover {
        background-color: #d4af37;
        color: #001f3f;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# FUNÇÕES DE APOIO (PDF E DADOS)
# ==========================================
def gerar_pdf(dados_projeto, dados_empresa, tipo="Orcamento"):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Gold
    pdf.set_fill_color(212, 175, 55)
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_y(10)
    pdf.cell(0, 10, f"{dados_empresa['nome_empresa']}", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 8)
    info_topo = f"CNPJ/CPF: {dados_empresa['cpf_cnpj']} | WhatsApp: {dados_empresa['whatsapp']} | E-mail: {dados_empresa['email']}"
    pdf.cell(0, 5, info_topo, 0, 1, 'C')
    pdf.cell(0, 5, f"Endereço: {dados_empresa['endereco']}", 0, 1, 'C')
    
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"{tipo.upper()}: {dados_projeto['nome_projeto']}".upper(), "B", 1, 'L')
    
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"Cliente: {dados_projeto['cliente']}", 0, 1)
    pdf.cell(0, 8, f"Prazo: {dados_projeto['prazo']}", 0, 1)
    pdf.multi_cell(0, 8, f"Descrição: {dados_projeto['descricao']}")
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"VALOR TOTAL: R$ {dados_projeto['valor_total']:.2f}", 0, 1, 'R')
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# NAVEGAÇÃO PRINCIPAL
# ==========================================
menu = st.sidebar.selectbox("MENU PRINCIPAL", ["Painel de Controle", "Novo Orçamento", "Gestão de Projetos", "Configurações"])

# Puxar dados da empresa para uso geral
config_res = supabase.table("configuracoes").select("*").limit(1).execute()
dados_empresa = config_res.data[0] if config_res.data else {"nome_empresa": "PJ Studio Design", "cpf_cnpj": "", "whatsapp": "", "email": "", "endereco": ""}

# ------------------------------------------
# ABA: NOVO ORÇAMENTO (COM TRAVA DE DUPLICAÇÃO)
# ------------------------------------------
if menu == "Novo Orçamento":
    st.header("📝 Criar Novo Orçamento")
    
    with st.form("form_orcamento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cliente = st.text_input("Nome do Cliente")
            cpf_cnpj = st.text_input("CPF/CNPJ Cliente")
            whatsapp = st.text_input("WhatsApp Cliente")
        with col2:
            email = st.text_input("E-mail Cliente")
            endereco = st.text_input("Endereço Cliente")
            nome_projeto = st.text_input("Nome do Projeto")
            
        descricao = st.text_area("Descrição do Serviço")
        
        col3, col4 = st.columns(2)
        with col3:
            prazo = st.text_input("Prazo de Entrega (ex: 7 dias úteis)")
        with col4:
            valor_total = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
            
        btn_salvar = st.form_submit_button("GERAR E SALVAR ORÇAMENTO")

        if btn_salvar:
            if not cliente or not nome_projeto:
                st.error("Por favor, preencha o nome do cliente e do projeto.")
            else:
                try:
                    dados_insert = {
                        "cliente": cliente,
                        "cpf_cnpj": cpf_cnpj,
                        "whatsapp_cliente": whatsapp,
                        "email_cliente": email,
                        "endereco_cliente": endereco,
                        "nome_projeto": nome_projeto,
                        "descricao": descricao,
                        "prazo": prazo,
                        "valor_total": valor_total,
                        "status_total": "Pendente",
                        "status_entrada": "Pendente",
                        "status_final": "Pendente"
                    }
                    
                    # INSERÇÃO NO BANCO
                    res = supabase.table("projetos").insert(dados_insert).execute()
                    
                    if res.data:
                        st.success("✅ Orçamento salvo e registrado com sucesso!")
                        
                        # --- BLINDAGEM ANTI-DUPLICAÇÃO ---
                        st.cache_data.clear() # Limpa cache de consultas
                        st.rerun()            # Interrompe o processo e limpa o estado do botão
                        # ---------------------------------
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

# ------------------------------------------
# ABA: GESTÃO DE PROJETOS (INTOCÁVEL)
# ------------------------------------------
elif menu == "Gestão de Projetos":
    st.header("📋 Gestão de Projetos e Fluxo de Caixa")
    
    # Busca dados atualizados
    projetos_res = supabase.table("projetos").select("*").order("created_at", desc=True).execute()
    projetos = projetos_res.data
    
    if not projetos:
        st.info("Nenhum projeto encontrado.")
    else:
        for p in projetos:
            with st.expander(f"📌 {p['cliente']} - {p['nome_projeto']} (R$ {p['valor_total']:.2f})"):
                col_ed1, col_ed2 = st.columns(2)
                
                with col_ed1:
                    novo_status_entrada = st.selectbox("Status Entrada", ["Pendente", "Pago"], 
                                                      index=0 if p['status_entrada'] == "Pendente" else 1, key=f"ent_{p['id']}")
                    novo_status_final = st.selectbox("Status Final", ["Pendente", "Pago"], 
                                                     index=0 if p['status_final'] == "Pendente" else 1, key=f"fin_{p['id']}")
                
                with col_ed2:
                    # BOTOES DE PDF (Blindados com os dados da empresa)
                    pdf_orc = gerar_pdf(p, dados_empresa, "Orcamento")
                    st.download_button("📥 Baixar Orçamento", pdf_orc, f"Orcamento_{p['cliente']}.pdf", "application/pdf", key=f"btn_orc_{p['id']}")
                    
                if st.button("Atualizar Status", key=f"up_{p['id']}"):
                    supabase.table("projetos").update({
                        "status_entrada": novo_status_entrada,
                        "status_final": novo_status_final,
                        "status_total": "Concluído" if novo_status_final == "Pago" else "Em Andamento"
                    }).eq("id", p['id']).execute()
                    st.success("Atualizado!")
                    st.cache_data.clear()
                    st.rerun()

# ------------------------------------------
# ABA: PAINEL DE CONTROLE (RESUMO)
# ------------------------------------------
elif menu == "Painel de Controle":
    st.title("🚀 Dashboard PJ GOLD PRO")
    res_soma = supabase.table("projetos").select("valor_total").execute()
    total_bruto = sum([item['valor_total'] for item in res_soma.data]) if res_soma.data else 0.0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento Total", f"R$ {total_bruto:,.2f}")
    c2.metric("Projetos Ativos", len(res_soma.data) if res_soma.data else 0)
    c3.metric("Estúdio", "PJ Studio Design")

# ------------------------------------------
# ABA: CONFIGURAÇÕES (EMPRESA)
# ------------------------------------------
elif menu == "Configurações":
    st.header("⚙️ Configurações do Estúdio")
    with st.form("form_config"):
        nome_e = st.text_input("Nome da Empresa", value=dados_empresa['nome_empresa'])
        doc_e = st.text_input("CPF/CNPJ", value=dados_empresa['cpf_cnpj'])
        zap_e = st.text_input("WhatsApp", value=dados_empresa['whatsapp'])
        mail_e = st.text_input("E-mail", value=dados_empresa['email'])
        end_e = st.text_input("Endereço Completo", value=dados_empresa['endereco'])
        
        if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
            data_config = {
                "nome_empresa": nome_e, "cpf_cnpj": doc_e, 
                "whatsapp": zap_e, "email": mail_e, "endereco": end_e
            }
            if config_res.data:
                supabase.table("configuracoes").update(data_config).eq("id", dados_empresa['id']).execute()
            else:
                supabase.table("configuracoes").insert(data_config).execute()
            st.success("Configurações atualizadas!")
            st.rerun()
