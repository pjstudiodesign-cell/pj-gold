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
    conn = sqlite3.connect('pj_gold_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS projetos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, servico TEXT, 
                       valor REAL, status TEXT, data_inicio TEXT, mes_ano TEXT, 
                       telefone TEXT, financeiro TEXT, valor_entrada REAL, 
                       status_entrada TEXT, valor_final REAL, status_final TEXT,
                       status_integral TEXT)''')
    
    colunas = [
        ("valor_entrada", "REAL DEFAULT 0"),
        ("status_entrada", "TEXT DEFAULT 'Pendente'"),
        ("valor_final", "REAL DEFAULT 0"),
        ("status_final", "TEXT DEFAULT 'Pendente'"),
        ("status_integral", "TEXT DEFAULT 'Pendente'")
    ]
    for col, tipo in colunas:
        try:
            cursor.execute(f"ALTER TABLE projetos ADD COLUMN {col} {tipo}")
        except:
            pass

    cursor.execute('''CREATE TABLE IF NOT EXISTS config 
                      (id INTEGER PRIMARY KEY, nome_studio TEXT, sub_titulo TEXT, 
                       contato TEXT, email TEXT, endereco TEXT)''')
    
    cursor.execute("SELECT COUNT(*) FROM config")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""INSERT INTO config (id, nome_studio, sub_titulo, contato, email, endereco) 
                          VALUES (1, 'PJ STUDIO DESIGN', 'Soluções Inteligentes em Design e Software', 
                          '24981196037', 'pjstudiodesign@gmail.com', 'Rua Guilherme Marcondes, 505 - Barra Mansa - RJ')""")
    conn.commit()
    conn.close()

def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs, info_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(20, 20, 20)
    pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 15, str(info_list[0]), ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 5, str(info_list[1]), ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"WhatsApp: {info_list[2]} | Email: {info_list[3]}", ln=True, align='C')
    pdf.cell(0, 5, f"Endereco: {info_list[4]}", ln=True, align='C')
    pdf.ln(20)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
    pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. DESCRICAO DO SERVICO", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, f"{servico}\n\nObs: {obs}")
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. CONDICOES E ENTREGA", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"- Prazo: {prazo} | Revisoes: {rev}", ln=True)
    pdf.cell(0, 8, f"- Pagamento: {pgto}", ln=True)
    pdf.cell(0, 8, f"- Obs: Aceitamos entrada de 50% e 50% na entrega ou valor integral.", ln=True)
    pdf.set_y(-40)
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

def main():
    aplicar_estilo_pj_gold()
    init_db()
    conn = sqlite3.connect('pj_gold_data.db')
    config_df = pd.read_sql_query("SELECT * FROM config WHERE id=1", conn)
    
    if config_df.empty:
        st.error("Erro nas configurações.")
        return
        
    config_row = config_df.iloc[0]
    # Criamos uma lista simples para o PDF não dar erro de chave
    info_para_pdf = [config_row['nome_studio'], config_row['sub_titulo'], config_row['contato'], config_row['email'], config_row['endereco']]

    st.sidebar.title("⚜️ PJ GOLD MENU")
    menu = ["Painel", "Novo Job / Orçamento", "Gestão de Projetos", "Backup de Segurança", "Configurações"]
    escolha = st.sidebar.radio("Navegação:", menu)

    if escolha == "Painel":
        st.title(f"⚜️ {config_row['nome_studio']}")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        total_recebido, total_pendente = 0.0, 0.0
        if not df.empty:
            for _, row in df.iterrows():
                if row['status_integral'] == 'Recebido':
                    total_recebido += row['valor']
                else:
                    rec = (row['valor_entrada'] if row['status_entrada'] == 'Recebido' else 0) + \
                          (row['valor_final'] if row['status_final'] == 'Recebido' else 0)
                    total_recebido += rec
                    total_pendente += (row['valor'] - rec)
        
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='stMetric'><b>Total em Caixa</b><br><h2 style='color:#D4AF37'>R$ {total_recebido:,.2f}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stMetric'><b>A Receber</b><br><h2 style='color:#D4AF37'>R$ {total_pendente:,.2f}</h2></div>", unsafe_allow_html=True)

    elif escolha == "Novo Job / Orçamento":
        st.title("⚜️ Novo Orçamento")
        with st.form("form_orcamento", clear_on_submit=False):
            c_a, c_b = st.columns(2)
            n = c_a.text_input("Nome do Cliente")
            tel = c_b.text_input("WhatsApp")
            val = st.number_input("Valor Total (R$)", min_value=0.0, step=50.0)
            ser = st.text_area("Descrição do Serviço")
            obs = st.text_input("Observações")
            c_c, c_d = st.columns(2)
            prz = c_c.text_input("Prazo")
            pg = c_d.text_input("Forma de Pagamento")
            rev = st.selectbox("Revisões", ["1 Revisão", "2 Revisões", "3 Revisões", "Ilimitadas"])
            
            if st.form_submit_button("SALVAR E PREPARAR PDF"):
                if n and ser:
                    v_metade = val / 2
                    cursor = conn.cursor()
                    cursor.execute("""INSERT INTO projetos 
                        (cliente, servico, valor, status, data_inicio, mes_ano, telefone, 
                         financeiro, valor_entrada, status_entrada, valor_final, status_final, status_integral) 
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (n, ser, val, "Em Produção", datetime.now().strftime("%d/%m/%Y"), 
                         datetime.now().strftime("%m/%Y"), tel, "Pendente", v_metade, "Pendente", v_metade, "Pendente", "Pendente"))
                    conn.commit()
                    st.session_state.pdf_data = gerar_pdf_orcamento(n, ser, val, pg, prz, rev, obs, info_para_pdf)
                    st.session_state.pdf_nome = n
                    st.success("Salvo com sucesso! Baixe o PDF abaixo.")
                else:
                    st.error("Preencha Nome e Serviço!")

        if 'pdf_data' in st.session_state:
            st.download_button("📥 BAIXAR ORÇAMENTO PDF", st.session_state.pdf_data, f"Orcamento_{st.session_state.pdf_nome}.pdf", "application/pdf")

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Gestão de Jobs")
        df = pd.read_
