import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 1. Configuração da Página
st.set_page_config(page_title="PJ Gold System", page_icon="💰", layout="wide")

# 2. Estilo Visual PJ GOLD (Correção de visibilidade de textos)
def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #0a0a0a; }
        h1, h2, h3 { color: #FFD700 !important; }
        [data-testid="stSidebarNav"] span { color: #ffffff !important; font-weight: bold !important; }
        
        /* Forçando visibilidade de textos dentro de expanders e formulários */
        .st-emotion-cache-p5msec, .st-emotion-cache-1h9usn2, p, span, label { 
            color: #ffffff !important; 
        }
        
        /* Rótulos dos Selectbox e Inputs em Dourado para destaque */
        label { color: #FFD700 !important; font-weight: bold !important; }
        
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%) !important;
            color: #000000 !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            width: 100% !important;
            border: none !important;
            height: 3em !important;
        }
        .stDownloadButton>button p { color: #000000 !important; }
        section[data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #FFD700; }
        .stMetric { background-color: #161616; padding: 20px; border-radius: 12px; border: 1px solid #333; }
        [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 1.2em !important; }
        [data-testid="stMetricValue"] { color: #FFD700 !important; }
        </style>
    """, unsafe_allow_html=True)

# 3. Busca de Dados
def buscar_dados_empresa():
    try:
        conn = sqlite3.connect('pjgold_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nome_studio, sub_titulo, contato, email, endereco FROM config WHERE id=1")
        res = cursor.fetchone()
        conn.close()
        if res: return res
    except: pass
    return ("PJ Gold", "Gestão de Elite", "", "", "")

# 4. Funções de PDF (Padrão SaarteSvm com Dados Completos)
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs):
    try:
        info = buscar_dados_empresa()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(15, 15, 15); pdf.rect(0, 0, 210, 65, 'F')
        
        # Cabeçalho - SaarteSvm Style (Nome tam 20)
        pdf.set_y(12); pdf.set_font("Arial", 'B', 20); pdf.set_text_color(255, 215, 0)
        pdf.cell(0, 12, "PJ Gold", ln=True, align='C')
        
        pdf.set_font("Arial", 'I', 10); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 6, str(info[1]), ln=True, align='C')
        
        # Dados da Empresa no PDF
        pdf.set_font("Arial", '', 9); pdf.set_text_color(180, 180, 180)
        contato_info = f"WhatsApp: {info[2]} | Email: {info[3]}"
        pdf.cell(0, 6, contato_info, ln=True, align='C')
        if info[4]: pdf.multi_cell(0, 5, f"Endereço: {info[4]}", align='C')
        
        # Corpo do Orçamento
        pdf.set_y(75); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
        pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
        pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
        
        pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "1. ESCOPO DO SERVICO", ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}")
        if obs:
            pdf.ln(2); pdf.set_font("Arial", 'B', 11); pdf.cell(10, 7, "Obs: "); pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{obs}")
        
        pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "2. CONDICOES", ln=True)
        pdf.set_font("Arial", '', 11); pdf.cell(0, 8, f"- Prazo: {prazo} | Revisões: {rev}", ln=True)
        pdf.cell(0, 8, f"- Pagamento: {pgto}", ln=True)
        
        pdf.set_y(-40); pdf.set_font("Arial", 'B', 18); pdf.set_text_color(184, 134, 11)
        pdf.cell(0, 15, f"VALOR TOTAL: R$ {valor:,.2f}", ln=True, align='R')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

def gerar_pdf_recibo(cliente, servico, valor):
    try:
        info = buscar_dados_empresa()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_draw_color(255, 215, 0); pdf.rect(5, 5, 200, 120)
        pdf.set_font("Arial", 'B', 18); pdf.set_y(15); pdf.cell(0, 15, "RECIBO PJ GOLD", ln=True, align='C')
        pdf.ln(10); pdf.set_font("Arial", '', 12)
        texto = f"Recebemos de {str(cliente).upper()}, a importância de R$ {valor:,.2f} referente ao serviço de: {servico}."
        pdf.multi_cell(0, 10, texto, align='L')
        pdf.ln(10); pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
        pdf.ln(15); pdf.cell(0, 10, "__________________________________________________", ln=True, align='C')
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, "PJ Gold", ln=True, align='C')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

# 5. Banco de Dados
def iniciar_db():
    conn = sqlite3.connect('pjgold_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS projetos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, servico TEXT, valor REAL, status TEXT, 
        data_inicio TEXT, telefone TEXT, valor_entrada REAL, status_entrada TEXT, valor_final REAL, 
        status_final TEXT, status_integral TEXT, prazo_salvo TEXT, pagamento_salvo TEXT, 
        revisao_salva TEXT, obs_salva TEXT)""")
    cursor.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, nome_studio TEXT, sub_titulo TEXT, contato TEXT, email TEXT, endereco TEXT)")
    cursor.execute("SELECT COUNT(*) FROM config")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO config (id, nome_studio, sub_titulo, contato, email, endereco) VALUES (1, 'PJ Gold', 'Elite Service', '', '', '')")
        conn.commit()
    return conn

# 6. Interface Principal
def main():
    aplicar_estilo()
    conn = iniciar_db()
    cursor = conn.cursor()
    info_sidebar = buscar_dados_empresa()
    st.sidebar.title(f"⚜️ {info_sidebar[0]}")
    menu = ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"]
    escolha = st.sidebar.radio("Navegar:", menu)

    if escolha == "Painel":
        st.title(f"💰 Painel {info_sidebar[0]}")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        total_rec = 0.0; total_pend = 0.0
        if not df.empty:
            for _, r in df.iterrows():
                v_total = r['valor'] or 0
                if r['status_integral'] == 'Recebido': total_rec += v_total
                else:
                    total_rec += (r['valor_entrada'] if r['status_entrada'] == 'Recebido' else 0)
                    total_rec += (r['valor_final'] if r['status_final'] == 'Recebido' else 0)
            total_pend = (df['valor'].sum() or 0) - total_rec
        col1, col2 = st.columns(2)
        with col1: st.metric("Total em Caixa", f"R$ {total_rec:,.2f}")
        with col2: st.metric("A Receber", f"R$ {total_pend:,.2f}")

    elif escolha == "Novo Job":
        st.title("➕ Novo Projeto")
        with st.form("orc_form"):
            c1, c2 = st.columns(2); n = c1.text_input("Cliente"); tel = c2.text_input("WhatsApp")
            v = st.number_input("Valor do Job", min_value=0.0, step=0.01)
            ser = st.text_area("Escopo do Serviço"); obs_in = st.text_input("Observações")
            c3, c4, c5 = st.columns(3); prz = c3.text_input("Prazo", "7 dias")
            rev = c4.selectbox("Revisões", ["1", "2", "3", "Ilimitadas"])
            pag = c5.text_input("Pagamento", "50% entrada / 50% entrega")
            if st.form_submit_button("SALVAR"):
                if n and ser:
                    cursor.execute("""INSERT INTO projetos (cliente, servico, valor, status, data_inicio, telefone, 
                        valor_entrada, status_entrada, valor_final, status_final, status_integral, 
                        prazo_salvo, pagamento_salvo, revisao_salva, obs_salva) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (n, ser, v, "Ativo", datetime.now().strftime("%d/%m/%Y"), tel, v/2, "Pendente", v/2, "Pendente", "Pendente", prz, pag, rev, obs_in))
                    conn.commit(); st.success("Cadastrado!")
                else: st.error("Faltam dados.")

    elif escolha == "Gestão de Projetos":
        st.title("📂 Controle de Jobs e Fluxo")
        df = pd.read_sql_query("SELECT * FROM projetos ORDER BY id DESC", conn)
        for _, r in df.iterrows():
            with st.expander(f"⚜️ {r['cliente']} | R$ {r['valor']:.2f}"):
                # Mostrando Escopo e Obs claramente
                st.markdown(f"**Escopo:** {r['servico']}")
                if r['obs_salva']:
                    st.markdown(f"**Observações:** {r['obs_salva']}")
                
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                s_int = col1.selectbox("Pag. Total", ["Pendente", "Recebido"], index=0 if r['status_integral'] == "Pendente" else 1, key=f"i{r['id']}")
                s_ent = col2.selectbox("Entrada (50%)", ["Pendente", "Recebido"], index=0 if r['status_entrada'] == "Pendente" else 1, key=f"e{r['id']}")
                s_fin = col3.selectbox("Final (50%)", ["Pendente", "Recebido"], index=0 if r['status_final'] == "Pendente" else 1, key=f"f{r['id']}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                c_at, c_orc, c_rec, c_del = st.columns(4)
                
                if c_at.button("Atualizar Status", key=f"s{r['id']}"):
                    cursor.execute("UPDATE projetos SET status_entrada=?, status_final=?, status_integral=? WHERE id=?", (s_ent, s_fin, s_int, r['id'])); conn.commit(); st.rerun()
                
                if c_orc.button("Orçamento PDF", key=f"btn_orc{r['id']}"):
                    pdf_o = gerar_pdf_orcamento(r['cliente'], r['servico'], r['valor'], r['pagamento_salvo'], r['prazo_salvo'], r['revisao_salva'], r['obs_salva'])
                    if pdf_o: st.download_button("Baixar Orçamento", pdf_o, f"Orcamento_{r['cliente']}.pdf", key=f"dl_orc{r['id']}")
                
                if c_rec.button("Recibo PDF", key=f"btn_rec{r['id']}"):
                    v_pago = r['valor'] if s_int == "Recebido" else (r['valor_entrada'] if s_ent == "Recebido" else 0)
                    pdf_r = gerar_pdf_recibo(r['cliente'], r['servico'], v_pago)
                    if pdf_r: st.download_button("Baixar Recibo", pdf_r, f"Recibo_{r['cliente']}.pdf", key=f"dl_rec{r['id']}")
                
                if c_del.button("Remover Projeto", key=f"del{r['id']}"):
                    cursor.execute("DELETE FROM projetos WHERE id=?", (r['id'],)); conn.commit(); st.rerun()

    elif escolha == "Configurações":
        st.title("⚙️ Dados PJ Gold")
        info_f = buscar_dados_empresa()
        with st.form("form_config"):
            nome_emp = st.text_input("Nome Comercial", info_f[0])
            slogan_emp = st.text_input("Slogan", info_f[1])
            whats_emp = st.text_input("WhatsApp", info_f[2])
            email_emp = st.text_input("E-mail", info_f[3])
            end_emp = st.text_area("Endereço", info_f[4])
            if st.form_submit_button("SALVAR"):
                cursor.execute("UPDATE config SET nome_studio=?, sub_titulo=?, contato=?, email=?, endereco=? WHERE id=1", (nome_emp, slogan_emp, whats_emp, email_emp, end_emp))
                conn.commit(); st.success("Atualizado!"); st.rerun()
    conn.close()

if __name__ == "__main__":
    main()
