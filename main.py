import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

# ==========================================
# CONFIGURAÇÃO VISUAL ORIGINAL PJ GOLD
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
# FUNÇÕES DE PDF (ORÇAMENTO E RECIBO)
# ==========================================
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs, info):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(20, 20, 20)
    pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 15, str(info[0]), ln=True, align='C')
    pdf.set_font("Arial", 'I', 10); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 5, str(info[1]), ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"WhatsApp: {info[2]} | Email: {info[3]}", ln=True, align='C')
    pdf.cell(0, 5, f"Endereco: {info[4]}", ln=True, align='C')
    pdf.ln(20); pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
    pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
    pdf.ln(10); pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. DESCRICAO DO SERVICO", ln=True)
    pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}")
    if obs:
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 11); pdf.cell(10, 7, "Obs: "); pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{obs}")
    
    pdf.ln(5); pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. CONDICOES E ENTREGA", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"- Prazo: {prazo} | Revisoes: {rev}", ln=True)
    pdf.cell(0, 8, f"- Pagamento: {pgto}", ln=True)
    pdf.set_y(-40); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

def gerar_pdf_recibo(cliente, servico, valor, info):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_draw_color(212, 175, 55); pdf.rect(5, 5, 200, 100)
    pdf.set_font("Arial", 'B', 18); pdf.cell(0, 15, "RECIBO DE PAGAMENTO", ln=True, align='C')
    pdf.ln(5); pdf.set_font("Arial", '', 12)
    texto = f"Recebemos de {str(cliente).upper()}, a importancia de R$ {valor:,.2f} referente ao servico de: {servico}."
    pdf.multi_cell(0, 10, texto, align='L')
    pdf.ln(10); pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
    pdf.ln(10); pdf.cell(0, 10, "__________________________________________________", ln=True, align='C')
    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, str(info[0]), ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# ==========================================
# LOGICA DO SISTEMA
# ==========================================
def main():
    aplicar_estilo_pj_gold()
    conn = sqlite3.connect('pj_gold_data.db', check_same_thread=False); cursor = conn.cursor()
    
    # Criar Tabelas
    cursor.execute('''CREATE TABLE IF NOT EXISTS projetos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, servico TEXT, valor REAL, status TEXT, 
                       data_inicio TEXT, mes_ano TEXT, telefone TEXT, financeiro TEXT, valor_entrada REAL, 
                       status_entrada TEXT, valor_final REAL, status_final TEXT, status_integral TEXT,
                       prazo_salvo TEXT, pagamento_salvo TEXT, revisao_salva TEXT, obs_salva TEXT)''')
    
    # Migrações seguras das colunas novas
    for col, tip in [("prazo_salvo", "TEXT"), ("pagamento_salvo", "TEXT"), ("revisao_salva", "TEXT"), ("obs_salva", "TEXT")]:
        try: cursor.execute(f"ALTER TABLE projetos ADD COLUMN {col} {tip}")
        except: pass

    cursor.execute('''CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, nome_studio TEXT, sub_titulo TEXT, contato TEXT, email TEXT, endereco TEXT)''')
    cursor.execute("SELECT nome_studio, sub_titulo, contato, email, endereco FROM config WHERE id=1")
    config_res = cursor.fetchone()
    
    st.sidebar.title("⚜️ PJ GOLD")
    menu = ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"]
    escolha = st.sidebar.radio("Navegar:", menu)

    if escolha == "Painel":
        st.title(f"⚜️ {config_res[0]}")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        total_rec = 0.0; total_pend = 0.0
        if not df.empty:
            for _, r in df.iterrows():
                v_total = r['valor'] or 0
                v_ent = r['valor_entrada'] or 0
                if r['status_integral'] == 'Recebido': total_rec += v_total
                else:
                    entrada = v_ent if r['status_entrada'] == 'Recebido' else 0
                    final = v_ent if r['status_final'] == 'Recebido' else 0
                    total_rec += (entrada + final); total_pend += (v_total - (entrada + final))
        
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"<div class='stMetric'><b>Total em Caixa</b><br><h2>R$ {total_rec:,.2f}</h2></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stMetric'><b>A Receber</b><br><h2>R$ {total_pend:,.2f}</h2></div>", unsafe_allow_html=True)

    elif escolha == "Novo Job":
        st.title("⚜️ Novo Orçamento")
        
        # Formulário estável sem clear_on_submit para não apagar enquanto você digita
        with st.form("orc_form"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Cliente")
            tel = c2.text_input("WhatsApp")
            v = st.number_input("Valor Total", min_value=0.0, step=0.01)
            ser = st.text_area("Serviço")
            obs_input = st.text_input("Observações")
            c3, c4, c5 = st.columns(3)
            prz = c3.text_input("Prazo", "10 dias úteis")
            rev_input = c4.selectbox("Revisões", ["Padrão", "1", "2", "3", "Ilimitadas"])
            pag = c5.text_input("Forma de Pagamento", "50% entrada / 50% entrega")
            
            if st.form_submit_button("SALVAR E GERAR PDF"):
                if n and ser:
                    v_m = v / 2
                    cursor.execute("""INSERT INTO projetos (cliente, servico, valor, status, data_inicio, telefone, 
                                     valor_entrada, status_entrada, valor_final, status_final, status_integral, 
                                     prazo_salvo, pagamento_salvo, revisao_salva, obs_salva) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                 (n, ser, v, "Em Produção", datetime.now().strftime("%d/%m/%Y"), tel, v_m, "Pendente", v_m, "Pendente", "Pendente", prz, pag, rev_input, obs_input))
                    conn.commit()
                    st.session_state.pdf_data = gerar_pdf_orcamento(n, ser, v, pag, prz, rev_input, obs_input, config_res)
                    st.session_state.pdf_name = n
                    st.success("Salvo com sucesso!")
                else:
                    st.error("Preencha Cliente e Serviço.")

        if 'pdf_data' in st.session_state:
            st.download_button("📥 BAIXAR PDF", st.session_state.pdf_data, f"Orcamento_{st.session_state.pdf_name}.pdf", "application/pdf")

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Gestão de Projetos")
        df = pd.read_sql_query("SELECT * FROM projetos ORDER BY id DESC", conn)
        for _, r in df.iterrows():
            with st.expander(f"📌 {r['cliente']} - R$ {r['valor']:.2f}"):
                st.write(f"**Serviço:** {r['servico']}")
                c1, c2, c3 = st.columns(3)
                s_int = c1.selectbox("Integral", ["Pendente", "Recebido"], index=0 if r['status_integral'] == "Pendente" else 1, key=f"i{r['id']}")
                s_ent = c2.selectbox("Entrada", ["Pendente", "Recebido"], index=0 if r['status_entrada'] == "Pendente" else 1, key=f"e{r['id']}")
                s_fin = c3.selectbox("Final", ["Pendente", "Recebido"], index=0 if r['status_final'] == "Pendente" else 1, key=f"f{r['id']}")
                
                col_a, col_b, col_c, col_d = st.columns(4)
                if col_a.button("Salvar Status", key=f"s{r['id']}"):
                    if s_int == "Recebido": s_ent, s_fin = "Recebido", "Recebido"
                    cursor.execute("UPDATE projetos SET status_entrada=?, status_final=?, status_integral=? WHERE id=?", (s_ent, s_fin, s_int, r['id']))
                    conn.commit(); st.rerun()
                
                # Re-Orçamento cirúrgico
                pdf_re = gerar_pdf_orcamento(r['cliente'], r['servico'], r['valor'], r['pagamento_salvo'], r['prazo_salvo'], r['revisao_salva'], r['obs_salva'], config_res)
                col_b.download_button("📄 Re-Orcamento", pdf_re, f"Orcamento_{r['cliente']}.pdf", key=f"re{r['id']}")
                
                v_rec = r['valor'] if s_int == "Recebido" else r['valor_entrada']
                pdf_rec = gerar_pdf_recibo(r['cliente'], r['servico'], v_rec, config_res)
                col_c.download_button("🧾 Recibo", pdf_rec, f"Recibo_{r['cliente']}.pdf", key=f"rec{r['id']}")
                
                if col_d.button("Excluir", key=f"del{r['id']}"):
                    cursor.execute("DELETE FROM projetos WHERE id=?", (r['id'],)); conn.commit(); st.rerun()

    elif escolha == "Configurações":
        st.title("⚙️ Configurações")
        with st.form("cfg"):
            n_s = st.text_input("Nome Studio", config_res[0]); t_s = st.text_input("WhatsApp", config_res[2]); e_s = st.text_input("Endereço", config_res[4])
            if st.form_submit_button("Salvar"):
                cursor.execute("UPDATE config SET nome_studio=?, contato=?, endereco=? WHERE id=1", (n_s, t_s, e_s))
                conn.commit(); st.rerun()
    conn.close()

if __name__ == "__main__":
    main()
