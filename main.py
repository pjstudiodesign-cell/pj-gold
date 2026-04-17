import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os

# ==========================================
# CONFIGURAÇÃO VISUAL PJ GOLD
# ==========================================
# Alterado para facilitar o nome no ícone do celular
st.set_page_config(page_title="PJ GOLD", page_icon="⚜️", layout="wide")

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
        section[data-testid="stSidebar"] { 
            background-color: #111111; 
            border-right: 2px solid #D4AF37; 
        }
        .stMetric {
            background-color: #1a1a1a;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #333;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# FUNÇÕES DE BANCO E ARQUIVOS
# ==========================================
def init_db():
    if not os.path.exists('PDFs_Orcamentos'):
        os.makedirs('PDFs_Orcamentos')
    conn = sqlite3.connect('pj_gold_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS projetos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, servico TEXT, 
                       valor REAL, status TEXT, data_inicio TEXT, mes_ano TEXT, 
                       telefone TEXT, financeiro TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS config 
                      (id INTEGER PRIMARY KEY, nome_studio TEXT, sub_titulo TEXT, 
                       contato TEXT, email TEXT, endereco TEXT)''')
    
    # Insere dados iniciais se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM config")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""INSERT INTO config (id, nome_studio, sub_titulo, contato, email, endereco) 
                          VALUES (1, 'PJ STUDIO DESIGN', 'Soluções Inteligentes em Design e Software', 
                          '24981196037', 'pjstudiodesign@gmail.com', 'Rua Guilherme Marcondes, 505 - Barra Mansa - RJ')""")
    conn.commit()
    conn.close()

def gerar_pdf_orcamento(cliente, servico, valor, validade, pagamento, prazo, revisoes, obs, info_studio):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Dourado e Preto
    pdf.set_fill_color(20, 20, 20)
    pdf.rect(0, 0, 210, 55, 'F')
    
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 15, info_studio[0], ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 5, info_studio[1], ln=True, align='C')
    
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"WhatsApp: {info_studio[2]} | Email: {info_studio[3]}", ln=True, align='C')
    pdf.cell(0, 5, f"Endereco: {info_studio[4]}", ln=True, align='C')
    
    pdf.ln(20)
    
    # Dados do Cliente
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"CLIENTE: {cliente.upper()}", ln=0)
    pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. DESCRICAO DO SERVICO", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, f"{servico}\n\nObs: {obs}")
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. TERMOS E ENTREGA", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"- Prazo: {prazo} | Revisoes: {revisoes}", ln=True)
    pdf.cell(0, 8, f"- Pagamento: {pagamento} | Validade: {validade} dias", ln=True)
    
    # Valor Final
    pdf.set_y(-40)
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
def main():
    aplicar_estilo_pj_gold()
    init_db()
    
    conn = sqlite3.connect('pj_gold_data.db')
    # Carrega configurações
    config_df = pd.read_sql_query("SELECT * FROM config WHERE id=1", conn)
    if not config_df.empty:
        config_data = config_df.iloc[0]
    else:
        st.error("Erro ao carregar configurações.")
        return

    st.sidebar.title("⚜️ PJ GOLD MENU")
    menu = ["Painel", "Novo Job / Orçamento", "Gestão de Projetos", "Backup de Segurança", "Configurações"]
    escolha = st.sidebar.radio("Navegação:", menu)

    if escolha == "Painel":
        st.title(f"⚜️ {config_data['nome_studio']}")
        st.subheader("Resumo Financeiro de Elite")
        
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        recebido = df[df['financeiro'] == 'Recebido']['valor'].sum() if not
