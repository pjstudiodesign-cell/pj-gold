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
    
    cursor.execute("SELECT COUNT(*) FROM config")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""INSERT INTO config (id, nome_studio, sub_titulo, contato, email, endereco) 
                          VALUES (1, 'PJ STUDIO DESIGN', 'Soluções Inteligentes em Design e Software', 
                          '24981196037', 'pjstudiodesign@gmail.com', 'Rua Guilherme Marcondes, 505 - Barra Mansa - RJ')""")
    conn.commit()
    conn.close()

def gerar_pdf_orcamento(cliente, servico, valor, validade, pagamento, prazo, revisoes, obs, info_studio):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(20, 20, 20)
        pdf.rect(0, 0, 210, 55, 'F')
        pdf.set_font("Arial", 'B', 24)
        pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 15, str(info_studio[0]), ln=True, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 5, str(info_studio[1]), ln=True, align='C')
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 5, f"WhatsApp: {info_studio[2]} | Email: {info_studio[3]}", ln=True, align='C')
        pdf.cell(0, 5, f"Endereco: {info_studio[4]}", ln=True, align='C')
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
        pdf.cell(0, 10, "2. TERMOS E ENTREGA", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"- Prazo: {prazo} | Revisoes: {revisoes}", ln=True)
        pdf.cell(0, 8, f"- Pagamento: {pagamento} | Validade: {validade} dias", ln=True)
        pdf.set_y(-40)
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
        return pdf.output(dest='S').encode('latin-1')
    except:
        # Fallback para evitar erro de encoding se houver caracteres especiais
        return pdf.output(dest='S').encode('utf-8', 'ignore')

def main():
    aplicar_estilo_pj_gold()
    init_db()
    conn = sqlite3.connect('pj_gold_data.db')
    config_df = pd.read_sql_query("SELECT * FROM config WHERE id=1", conn)
    
    if config_df.empty:
        st.error("Erro ao carregar configurações.")
        return
    
    config_data = config_df.iloc[0]
    st.sidebar.title("⚜️ PJ GOLD MENU")
    menu = ["Painel", "Novo Job / Orçamento", "Gestão de Projetos", "Backup de Segurança", "Configurações"]
    escolha = st.sidebar.radio("Navegação:", menu)

    if escolha == "Painel":
        st.title(f"⚜️ {config_data['nome_studio']}")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        recebido = 0.0
        a_receber = 0.0
        if not df.empty:
            recebido = df[df['financeiro'] == 'Recebido']['valor'].sum()
            a_receber = df[df['financeiro'] == 'Pendente']['valor'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='stMetric'><b>Dinheiro no Bolso</b><br><h2 style='color:#D4AF37'>R$ {recebido:,.2f}</h2></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='stMetric'><b>Contas a Receber</b><br><h2 style='color:#D4AF37'>R$ {a_receber:,.2f}</h2></div>", unsafe_allow_html=True)

    elif escolha == "Novo Job / Orçamento":
        st.title("⚜️ Gerar Novo Orçamento")
        
        # Variáveis para guardar o PDF gerado
        if 'pdf_gerado' not in st.session_state:
            st.session_state.pdf_gerado = None
            st.session_state.cliente_atual = ""

        with st.form("form_orcamento"):
            col_a, col_b = st.columns(2)
            n = col_a.text_input("Nome do Cliente")
            tel = col_b.text_input("WhatsApp/Celular")
            val = st.number_input("Valor do Investimento (R$)", min_value=0.0, step=50.0)
            ser = st.text_area("Descrição Detalhada do Serviço")
            obs = st.text_input("Observações Adicionais")
            col_c, col_d = st.columns(2)
            prz = col_c.text_input("Prazo de Entrega")
            pg = col_d.text_input("Forma de Pagamento")
            rev = st.selectbox("Quantidade de Revisões", ["1 Revisão", "2 Revisões", "3 Revisões", "Ilimitadas"])
            
            submit = st.form_submit_button("SALVAR E GERAR PDF")
            
            if submit:
                if n and ser:
                    mes_atual = datetime.now().strftime("%m/%Y")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO projetos (cliente, servico, valor, status, data_inicio, mes_ano, telefone, financeiro) VALUES (?,?,?,?,?,?,?,?)",
                                   (n, ser, val, "Em Produção", datetime.now().strftime("%d/%m/%Y"), mes_atual, tel, "Pendente"))
                    conn.commit()
                    
                    # Gera o PDF e guarda no estado da sessão (fora do form)
                    st.session_state.pdf_gerado = gerar_pdf_orcamento(n, ser, val, 15, pg, prz, rev, obs, [config_data['nome_studio'], config_data['sub_titulo'], config_data['contato'], config_data['email'], config_data['endereco']])
                    st.session_state.cliente_atual = n
                    st.success(f"Projeto de {n} salvo com sucesso!")
                else:
                    st.warning("Por favor, preencha o Nome e a Descrição.")

        # O BOTÃO DE DOWNLOAD FICA AQUI FORA DO FORM
        if st.session_state.pdf_gerado:
            st.download_button(
                label="📥 CLIQUE AQUI PARA BAIXAR O PDF",
                data=st.session_state.pdf_gerado,
                file_name=f"Orcamento_{st.session_state.cliente_atual}.pdf",
                mime="application/pdf"
            )

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Acompanhamento de Jobs")
        df = pd.read_sql_query("SELECT * FROM projetos ORDER BY id DESC", conn)
        if df.empty:
            st.info("Nenhum projeto cadastrado.")
        else:
            for i, row in df.iterrows():
                with st.expander(f"📌 {row['cliente']} - {row['servico'][:30]}..."):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    ns = c1.selectbox("Status Produção", ["Em Produção", "Finalizado"], index=0 if row['status'] == "Em Produção" else 1, key=f"s_{row['id']}")
                    nf = c2.selectbox("Status Financeiro", ["Pendente", "Recebido"], index=0 if row['financeiro'] == "Pendente" else 1, key=f"f_{row['id']}")
                    if c3.button("Salvar", key=f"b_{row['id']}"):
                        cursor = conn.cursor()
                        cursor.execute("UPDATE projetos SET status=?, financeiro=? WHERE id=?", (ns, nf, row['id']))
                        conn.commit()
                        st.rerun()

    elif escolha == "Backup de Segurança":
        st.title("📦 Backup dos Dados")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        if not df.empty:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Relatorio')
            st.download_button(label="📥 DESCARREGAR EXCEL", data=output.getvalue(), file_name="Backup_PJ_GOLD.xlsx")

    elif escolha == "Configurações":
        st.title("⚙️ Dados do Studio")
        with st.form("cfg"):
            n_s = st.text_input("Nome do Studio", config_data['nome_studio'])
            s_s = st.text_input("Slogan", config_data['sub_titulo'])
            z_s = st.text_input("WhatsApp", config_data['contato'])
            m_s = st.text_input("E-mail", config_data['email'])
            e_s = st.text_input("Endereço", config_data['endereco'])
            if st.form_submit_button("SALVAR"):
                cursor = conn.cursor()
                cursor.execute("UPDATE config SET nome_studio=?, sub_titulo=?, contato=?, email=?, endereco=? WHERE id=1", (n_s, s_s, z_s, m_s, e_s))
                conn.commit()
                st.rerun()
    conn.close()

if __name__ == "__main__":
    main()
