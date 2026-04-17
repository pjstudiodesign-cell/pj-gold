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
        }
        section[data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #D4AF37; }
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
    # Seus dados reais que você configurou
    cursor.execute("""INSERT OR IGNORE INTO config (id, nome_studio, sub_titulo, contato, email, endereco) 
                      VALUES (1, 'PJ STUDIO DESIGN', 'Solucoes Inteligentes em Design e Software', 
                      '24981196037', 'pjstudiodesign@gmail.com', 'Rua Guilherme Marcondes, 505 - Barra Mansa - RJ')""")
    conn.commit()
    conn.close()

def gerar_pdf_orcamento(cliente, servico, valor, validade, pagamento, prazo, revisoes, obs, info_studio):
    pdf = FPDF()
    pdf.add_page()
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
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"CLIENTE: {cliente.upper()}", ln=0)
    pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
    pdf.ln(10); pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. DESCRICAO DO SERVICO", ln=True)
    pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}\n\nObs: {obs}")
    pdf.ln(5); pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. TERMOS E ENTREGA", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"- Prazo: {prazo} | Revisoes: {revisoes}", ln=True)
    pdf.cell(0, 8, f"- Pagamento: {pagamento} | Validade: {validade} dias", ln=True)
    pdf.set_y(-40); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# INTERFACE
# ==========================================
def main():
    aplicar_estilo_pj_gold()
    init_db()
    conn = sqlite3.connect('pj_gold_data.db')
    config_data = pd.read_sql_query("SELECT * FROM config WHERE id=1", conn).iloc[0]

    st.sidebar.title("⚜️ MENU REAL")
    menu = ["Painel", "Novo Job / Orçamento", "Gestão de Projetos", "Backup de Segurança", "Configurações"]
    escolha = st.sidebar.radio("Ir para:", menu)

    if escolha == "Painel":
        st.title(f"⚜️ {config_data['nome_studio']} | Painel")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        recebido = df[df['financeiro'] == 'Recebido']['valor'].sum() if not df.empty else 0
        a_receber = df[df['financeiro'] == 'Pendente']['valor'].sum() if not df.empty else 0
        c1, c2 = st.columns(2)
        c1.metric("Dinheiro no Bolso", f"R$ {recebido:,.2f}")
        c2.metric("Contas a Receber", f"R$ {a_receber:,.2f}")

    elif escolha == "Novo Job / Orçamento":
        st.title("⚜️ Novo Orçamento")
        with st.form("orc"):
            n = st.text_input("Cliente"); tel = st.text_input("WhatsApp")
            val = st.number_input("Valor R$", min_value=0.0); prz = st.text_input("Prazo")
            ser = st.text_area("Serviço"); obs = st.text_area("Exigências")
            pg = st.text_input("Pagamento")
            rev = st.selectbox("Revisões", ["1 Revisão", "2 Revisões", "Ilimitadas"])
            if st.form_submit_button("GERAR E SALVAR"):
                mes = datetime.now().strftime("%m/%Y")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO projetos (cliente, servico, valor, status, data_inicio, mes_ano, telefone, financeiro) VALUES (?,?,?,?,?,?,?,?)",
                               (n, ser, val, "Em Produção", datetime.now().strftime("%d/%m/%Y"), mes, tel, "Pendente"))
                conn.commit()
                pdf = gerar_pdf_orcamento(n, ser, val, 15, pg, prz, rev, obs, [config_data['nome_studio'], config_data['sub_titulo'], config_data['contato'], config_data['email'], config_data['endereco']])
                st.success("Projeto registrado!")
                st.download_button("📥 BAIXAR PDF", pdf, f"Orcamento_{n}.pdf")

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Gestão de Jobs")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        for i, row in df.iterrows():
            with st.expander(f"CLIENTE: {row['cliente']} | {row['status']}"):
                c1, c2, c3 = st.columns(3)
                ns = c1.selectbox("Status", ["Em Produção", "Finalizado"], key=f"s_{row['id']}")
                nf = c2.selectbox("Financeiro", ["Pendente", "Recebido"], key=f"f_{row['id']}")
                if c3.button("Salvar", key=f"b_{row['id']}"):
                    cursor = conn.cursor()
                    cursor.execute("UPDATE projetos SET status=?, financeiro=? WHERE id=?", (ns, nf, row['id']))
                    conn.commit(); st.rerun()

    elif escolha == "Backup de Segurança":
        st.title("📦 Backup e Proteção de Dados")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        if not df.empty:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Projetos')
            st.download_button(label="📥 GERAR BACKUP (EXCEL)", data=output.getvalue(), file_name=f"Backup_PJ_GOLD_{datetime.now().strftime('%d_%m_%Y')}.xlsx")
        else:
            st.info("Nada para exportar ainda.")

    elif escolha == "Configurações":
        st.title("⚙️ Dados do Studio")
        with st.form("config"):
            nome = st.text_input("Nome", config_data['nome_studio'])
            slogan = st.text_input("Slogan", config_data['sub_titulo'])
            zap = st.text_input("WhatsApp", config_data['contato'])
            mail = st.text_input("Email", config_data['email'])
            end = st.text_input("Endereço", config_data['endereco'])
            if st.form_submit_button("SALVAR"):
                cursor = conn.cursor()
                cursor.execute("UPDATE config SET nome_studio=?, sub_titulo=?, contato=?, email=?, endereco=? WHERE id=1", (nome, slogan, zap, mail, end))
                conn.commit(); st.rerun()

if __name__ == "__main__":
    main()