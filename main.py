import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os
from st_supabase_connection import SupabaseConnection

# ==========================================
# CONFIGURAÇÃO VISUAL PJ GOLD (PRESERVADA)
# ==========================================
st.set_page_config(page_title="PJ Gold - Gestão de Elite", page_icon="⚜️", layout="wide")

def aplicar_estilo_pj_gold():
    st.markdown("""
        <style>
        .stApp { background-color: #0d0d0d; }
        h1, h2, h3, label, p { color: #D4AF37 !important; }
        .stButton>button {
            background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%);
            color: #000 !important;
            font-weight: bold;
            border-radius: 8px;
            width: 100%;
            border: none;
        }
        .stMetric { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #D4AF37; }
        section[data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #D4AF37; }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# CONEXÃO SUPABASE (MOTOR DE ELITE)
# ==========================================
# O Streamlit gerencia a conexão automaticamente via Secrets ou Variáveis de Ambiente
conn = st.connection("supabase", type=SupabaseConnection)

def buscar_config():
    """Busca dados do studio. Se não existir, retorna padrão."""
    try:
        response = conn.table("config").select("*").eq("id", 1).execute()
        if len(response.data) > 0:
            return response.data[0]
        else:
            # Dados padrão caso o banco esteja vazio
            return {
                "nome_studio": "PJ STUDIO DESIGN",
                "sub_titulo": "Solucoes Inteligentes em Design e Software",
                "contato": "24981196037",
                "email": "pjstudiodesign@gmail.com",
                "endereco": "Rua Guilherme Marcondes, 505 - Barra Mansa - RJ"
            }
    except:
        return {
            "nome_studio": "PJ STUDIO DESIGN",
            "sub_titulo": "Erro de Conexão",
            "contato": "", "email": "", "endereco": ""
        }

# ==========================================
# FUNÇÃO DE PDF (PRESERVADA)
# ==========================================
def gerar_pdf_orcamento(cliente, servico, valor, validade, pagamento, prazo, revisoes, obs, info_studio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(20, 20, 20)
    pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 15, info_studio['nome_studio'], ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 5, info_studio['sub_titulo'], ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"WhatsApp: {info_studio['contato']} | Email: {info_studio['email']}", ln=True, align='C')
    pdf.cell(0, 5, f"Endereco: {info_studio['endereco']}", ln=True, align='C')
    pdf.ln(20)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"CLIENTE: {cliente.upper()}", ln=0)
    pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
    pdf.ln(10); pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. DESCRICAO DO SERVICO", ln=True)
    pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}\n\nExigencias: {obs}")
    pdf.ln(5); pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. TERMOS E ENTREGA", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"- Prazo: {prazo} | Revisoes: {revisoes}", ln=True)
    pdf.cell(0, 8, f"- Pagamento: {pagamento} | Validade: {validade} dias", ln=True)
    pdf.set_y(-40); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
def main():
    aplicar_estilo_pj_gold()
    config_data = buscar_config()

    st.sidebar.title("⚜️ MENU REAL")
    menu = ["Painel", "Novo Job / Orçamento", "Gestão de Projetos", "Backup de Segurança", "Configurações"]
    escolha = st.sidebar.radio("Ir para:", menu)

    if escolha == "Painel":
        st.title(f"⚜️ {config_data['nome_studio']} | Painel")
        # Busca projetos do Supabase
        res = conn.table("projetos").select("valor, financeiro").execute()
        df = pd.DataFrame(res.data)
        
        recebido = df[df['financeiro'] == 'Recebido']['valor'].sum() if not df.empty else 0
        a_receber = df[df['financeiro'] == 'Pendente']['valor'].sum() if not df.empty else 0
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Dinheiro no Bolso", f"R$ {recebido:,.2f}")
        with c2:
            st.metric("Contas a Receber", f"R$ {a_receber:,.2f}")

    elif escolha == "Novo Job / Orçamento":
        st.title("⚜️ Novo Orçamento")
        with st.form("orc"):
            n = st.text_input("Cliente")
            tel = st.text_input("WhatsApp")
            val = st.number_input("Valor R$", min_value=0.0)
            prz = st.text_input("Prazo (ex: 5 dias úteis)")
            ser = st.text_area("Descrição do Serviço")
            obs = st.text_area("Exigências / Observações")
            pg = st.text_input("Forma de Pagamento")
            rev = st.selectbox("Revisões", ["1 Revisão", "2 Revisões", "Ilimitadas"])
            
            if st.form_submit_button("GERAR E SALVAR"):
                # Salvar no Supabase
                dados_job = {
                    "cliente": n,
                    "servico": ser,
                    "valor": val,
                    "status": "Em Produção",
                    "data_inicio": datetime.now().strftime("%d/%m/%Y"),
                    "mes_ano": datetime.now().strftime("%m/%Y"),
                    "telefone": tel,
                    "financeiro": "Pendente",
                    "prazo": prz,
                    "revisoes": rev,
                    "exigencias": obs
                }
                conn.table("projetos").insert([dados_job]).execute()
                
                # Gerar PDF
                pdf = gerar_pdf_orcamento(n, ser, val, 15, pg, prz, rev, obs, config_data)
                st.success("Projeto registrado na nuvem com sucesso!")
                st.download_button("📥 BAIXAR PDF", pdf, f"Orcamento_{n}.pdf")

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Gestão de Jobs")
        res = conn.table("projetos").select("*").order("id", desc=True).execute()
        df = pd.DataFrame(res.data)
        
        if not df.empty:
            for i, row in df.iterrows():
                with st.expander(f"CLIENTE: {row['cliente']} | {row['status']}"):
                    c1, c2, c3 = st.columns(3)
                    ns = c1.selectbox("Status", ["Em Produção", "Finalizado"], index=0 if row['status'] == "Em Produção" else 1, key=f"s_{row['id']}")
                    nf = c2.selectbox("Financeiro", ["Pendente", "Recebido"], index=0 if row['financeiro'] == "Pendente" else 1, key=f"f_{row['id']}")
                    
                    if c3.button("Atualizar", key=f"b_{row['id']}"):
                        conn.table("projetos").update({"status": ns, "financeiro": nf}).eq("id", row['id']).execute()
                        st.rerun()
        else:
            st.info("Nenhum projeto encontrado.")

    elif escolha == "Backup de Segurança":
        st.title("📦 Backup e Proteção de Dados")
        res = conn.table("projetos").select("*").execute()
        df = pd.DataFrame(res.data)
        
        if not df.empty:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Projetos_Nuvem')
            st.download_button(label="📥 GERAR BACKUP (EXCEL)", data=output.getvalue(), file_name=f"Backup_PJ_GOLD_Nuvem_{datetime.now().strftime('%d_%m_%Y')}.xlsx")
        else:
            st.info("Sem dados para exportar.")

    elif escolha == "Configurações":
        st.title("⚙️ Dados do Studio")
        with st.form("config_form"):
            nome = st.text_input("Nome do Studio", config_data['nome_studio'])
            slogan = st.text_input("Slogan/Sub-título", config_data['sub_titulo'])
            zap = st.text_input("WhatsApp de Contato", config_data['contato'])
            mail = st.text_input("Email Profissional", config_data['email'])
            end = st.text_input("Endereço", config_data['endereco'])
            
            if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
                novos_dados = {
                    "id": 1,
                    "nome_studio": nome,
                    "sub_titulo": slogan,
                    "contato": zap,
                    "email": mail,
                    "endereco": end
                }
                # Upsert: Insere se não existir, atualiza se existir
                conn.table("config").upsert([novos_dados]).execute()
                st.success("Configurações atualizadas!")
                st.rerun()

if __name__ == "__main__":
    main()
