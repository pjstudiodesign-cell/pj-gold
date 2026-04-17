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
    
    # Garante que as novas colunas existam
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
    pdf.set_font("Arial", 'B', 20)
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
    pdf.cell(0, 10, "2. CONDICOES", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"- Prazo: {prazo} | Revisoes: {rev}", ln=True)
    pdf.cell(0, 8, f"- Pagamento: {pgto}", ln=True)
    pdf.set_y(-40)
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

def main():
    aplicar_estilo_pj_gold()
    init_db()
    conn = sqlite3.connect('pj_gold_data.db')
    
    # Carrega Configurações
    cursor = conn.cursor()
    cursor.execute("SELECT nome_studio, sub_titulo, contato, email, endereco FROM config WHERE id=1")
    config_data = cursor.fetchone()
    info_para_pdf = list(config_data)

    st.sidebar.title("⚜️ PJ GOLD MENU")
    menu = ["Painel", "Novo Job / Orçamento", "Gestão de Projetos", "Backup", "Configurações"]
    escolha = st.sidebar.radio("Ir para:", menu)

    if escolha == "Painel":
        st.title(f"⚜️ {config_data[0]}")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        total_rec, total_pend = 0.0, 0.0
        if not df.empty:
            for _, r in df.iterrows():
                if r['status_integral'] == 'Recebido':
                    total_rec += r['valor']
                else:
                    v_e = r['valor_entrada'] if r['status_entrada'] == 'Recebido' else 0
                    v_f = r['valor_final'] if r['status_final'] == 'Recebido' else 0
                    total_rec += (v_e + v_f)
                    total_pend += (r['valor'] - (v_e + v_f))
        
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='stMetric'><b>Total em Caixa</b><br><h2>R$ {total_rec:,.2f}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stMetric'><b>A Receber</b><br><h2>R$ {total_pend:,.2f}</h2></div>", unsafe_allow_html=True)

    elif escolha == "Novo Job / Orçamento":
        st.title("⚜️ Novo Orçamento")
        with st.form("orc", clear_on_submit=False):
            nome = st.text_input("Cliente")
            whats = st.text_input("WhatsApp")
            valor = st.number_input("Valor Total", min_value=0.0)
            serv = st.text_area("Serviço")
            prazo = st.text_input("Prazo")
            pag = st.text_input("Pagamento")
            rev = st.selectbox("Revisões", ["1", "2", "3", "Ilimitadas"])
            obs = st.text_input("Obs")
            
            if st.form_submit_button("SALVAR"):
                if nome and serv:
                    v_metade = valor / 2
                    cursor.execute("""INSERT INTO projetos 
                        (cliente, servico, valor, status, data_inicio, mes_ano, telefone, 
                         financeiro, valor_entrada, status_entrada, valor_final, status_final, status_integral) 
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (nome, serv, valor, "Em Produção", datetime.now().strftime("%d/%m/%Y"), 
                         datetime.now().strftime("%m/%Y"), whats, "Pendente", v_metade, "Pendente", v_metade, "Pendente", "Pendente"))
                    conn.commit()
                    st.session_state.pdf_bytes = gerar_pdf_orcamento(nome, serv, valor, pag, prazo, rev, obs, info_para_pdf)
                    st.session_state.pdf_n = nome
                    st.success("Salvo!")
                else:
                    st.error("Preencha Nome e Serviço")

        if 'pdf_bytes' in st.session_state:
            st.download_button("📥 BAIXAR PDF", st.session_state.pdf_bytes, f"Orcamento_{st.session_state.pdf_n}.pdf", "application/pdf")

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Gestão")
        df = pd.read_sql_query("SELECT * FROM projetos ORDER BY id DESC", conn)
        for _, r in df.iterrows():
            with st.expander(f"📌 {r['cliente']} - R$ {r['valor']:.2f}"):
                s_int = st.selectbox("INTEGRAL", ["Pendente", "Recebido"], index=0 if r['status_integral'] == "Pendente" else 1, key=f"int{r['id']}")
                st.write("---")
                c1, c2, c3 = st.columns(3)
                s_prod = c1.selectbox("Produção", ["Em Produção", "Finalizado"], index=0 if r['status'] == "Em Produção" else 1, key=f"p{r['id']}")
                s_ent = c2.selectbox(f"Entrada", ["Pendente", "Recebido"], index=0 if r['status_entrada'] == "Pendente" else 1, key=f"e{r['id']}")
                s_fin = c3.selectbox(f"Final", ["Pendente", "Recebido"], index=0 if r['status_final'] == "Pendente" else 1, key=f"f{r['id']}")
                
                if st.button("Salvar", key=f"btn{r['id']}"):
                    if s_int == "Recebido": s_ent, s_fin = "Recebido", "Recebido"
                    f_geral = "Recebido" if (s_int == "Recebido" or (s_ent == "Recebido" and s_fin == "Recebido")) else "Pendente"
                    cursor.execute("""UPDATE projetos SET status=?, status_entrada=?, status_final=?, status_integral=?, financeiro=? WHERE id=?""",
                                 (s_prod, s_ent, s_fin, s_int, f_geral, r['id']))
                    conn.commit()
                    st.rerun()
                if st.button("Excluir", key=f"del{r['id']}"):
                    cursor.execute("DELETE FROM projetos WHERE id=?", (r['id'],))
                    conn.commit()
                    st.rerun()

    elif escolha == "Backup":
        st.title("📦 Backup")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        if not df.empty:
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                df.to_excel(wr, index=False)
            st.download_button("📥 EXCEL", out.getvalue(), "Backup.xlsx")

    elif escolha == "Configurações":
        st.title("⚙️ Config")
        with st.form("c"):
            n_s = st.text_input("Nome", config_data[0])
            s_s = st.text_input("Slogan", config_data[1])
            z_s = st.text_input("WhatsApp", config_data[2])
            m_s = st.text_input("E-mail", config_data[3])
            e_s = st.text_input("Endereço", config_data[4])
            if st.form_submit_button("SALVAR"):
                cursor.execute("UPDATE config SET nome_studio=?, sub_titulo=?, contato=?, email=?, endereco=? WHERE id=1", (n_s, s_s, z_s, m_s, e_s))
                conn.commit()
                st.rerun()
    conn.close()

if __name__ == "__main__":
    main()
