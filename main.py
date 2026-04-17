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
# FUNÇÕES DE DOCUMENTOS (PDF)
# ==========================================
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs, info_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(20, 20, 20)
    pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 15, str(info_list[0]), ln=True, align='C')
    pdf.set_font("Arial", 'I', 10); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 5, str(info_list[1]), ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"WhatsApp: {info_list[2]} | Email: {info_list[3]}", ln=True, align='C')
    pdf.cell(0, 5, f"Endereco: {info_list[4]}", ln=True, align='C')
    pdf.ln(20); pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
    pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
    pdf.ln(10); pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. DESCRICAO DO SERVICO", ln=True)
    pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}\n\nObs: {obs}")
    pdf.ln(5); pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. CONDICOES GERAIS", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"- Prazo: {prazo} | Revisoes: {rev}", ln=True)
    pdf.cell(0, 8, f"- Pagamento: {pgto}", ln=True)
    pdf.set_y(-40); pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

def gerar_pdf_recibo(cliente, servico, valor, info_list):
    pdf = FPDF()
    pdf.add_page()
    # Moldura Elegante
    pdf.set_draw_color(212, 175, 55); pdf.rect(5, 5, 200, 120)
    # Cabeçalho
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 15, "RECIBO DE PAGAMENTO", ln=True, align='C')
    pdf.ln(5)
    # Conteúdo
    pdf.set_font("Arial", '', 12)
    texto = (f"Recebi(emos) de {str(cliente).upper()}, a importância de "
             f"R$ {valor:,.2f} referente ao serviço de: {servico}.")
    pdf.multi_cell(0, 10, texto, align='L')
    pdf.ln(10)
    # Local e Data
    pdf.cell(0, 10, f"Barra Mansa, {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
    pdf.ln(15)
    # Assinatura
    pdf.cell(0, 10, "__________________________________________________", ln=True, align='C')
    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, str(info_list[0]), ln=True, align='C')
    pdf.set_font("Arial", '', 9); pdf.cell(0, 5, f"Contato: {info_list[2]}", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
def main():
    aplicar_estilo_pj_gold()
    conn = sqlite3.connect('pj_gold_data.db'); cursor = conn.cursor()
    
    # Criar tabelas se não existirem
    cursor.execute('''CREATE TABLE IF NOT EXISTS projetos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, servico TEXT, 
                       valor REAL, status TEXT, data_inicio TEXT, mes_ano TEXT, 
                       telefone TEXT, financeiro TEXT, valor_entrada REAL, 
                       status_entrada TEXT, valor_final REAL, status_final TEXT,
                       status_integral TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS config 
                      (id INTEGER PRIMARY KEY, nome_studio TEXT, sub_titulo TEXT, 
                       contato TEXT, email TEXT, endereco TEXT)''')
    
    # Carregar Config
    cursor.execute("SELECT nome_studio, sub_titulo, contato, email, endereco FROM config WHERE id=1")
    config_res = cursor.fetchone()
    if not config_res:
        cursor.execute("INSERT INTO config (id, nome_studio, sub_titulo, contato, email, endereco) VALUES (1, 'PJ STUDIO DESIGN', 'Design & Software', '24981196037', 'pj@gmail.com', 'Endereço')")
        conn.commit(); config_res = ('PJ STUDIO DESIGN', 'Design & Software', '24981196037', 'pj@gmail.com', 'Endereço')
    info_estudio = list(config_res)

    st.sidebar.title("⚜️ PJ GOLD")
    menu = ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"]
    escolha = st.sidebar.radio("Navegar:", menu)

    if escolha == "Painel":
        st.title(f"⚜️ {info_estudio[0]}")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        total_rec = 0.0
        if not df.empty:
            for _, r in df.iterrows():
                if r.get('status_integral') == 'Recebido': total_rec += r['valor']
                else:
                    if r.get('status_entrada') == 'Recebido': total_rec += (r.get('valor_entrada') or 0)
                    if r.get('status_final') == 'Recebido': total_rec += (r.get('valor_final') or 0)
        st.metric("Total em Caixa", f"R$ {total_rec:,.2f}")

    elif escolha == "Novo Job":
        st.title("⚜️ Criar Orçamento")
        with st.form("orc"):
            n = st.text_input("Cliente"); s = st.text_area("Serviço")
            v = st.number_input("Valor Total", min_value=0.0)
            p = st.text_input("Prazo", "7 dias úteis")
            f = st.text_input("Pagamento", "50% entrada / 50% entrega")
            if st.form_submit_button("SALVAR"):
                v_e = v / 2
                cursor.execute("INSERT INTO projetos (cliente, servico, valor, status, data_inicio, telefone, valor_entrada, status_entrada, valor_final, status_final, status_integral) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                             (n, s, v, "Em Produção", datetime.now().strftime("%d/%m/%Y"), "", v_e, "Pendente", v_e, "Pendente", "Pendente"))
                conn.commit(); st.success("Projeto salvo na Gestão!")

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Controle e Documentos")
        df = pd.read_sql_query("SELECT * FROM projetos ORDER BY id DESC", conn)
        for _, r in df.iterrows():
            with st.expander(f"📌 {r['cliente']} - R$ {r['valor']:.2f}"):
                # Controles de Status
                c1, c2, c3 = st.columns(3)
                st_int = c1.selectbox("Integral", ["Pendente", "Recebido"], index=0 if r['status_integral'] == "Pendente" else 1, key=f"int{r['id']}")
                st_ent = c2.selectbox("Entrada", ["Pendente", "Recebido"], index=0 if r['status_entrada'] == "Pendente" else 1, key=f"ent{r['id']}")
                st_fin = c3.selectbox("Final", ["Pendente", "Recebido"], index=0 if r['status_final'] == "Pendente" else 1, key=f"fin{r['id']}")
                
                if st.button("Salvar Alterações", key=f"save{r['id']}"):
                    if st_int == "Recebido": st_ent, st_fin = "Recebido", "Recebido"
                    cursor.execute("UPDATE projetos SET status_entrada=?, status_final=?, status_integral=? WHERE id=?", (st_ent, st_fin, st_int, r['id']))
                    conn.commit(); st.rerun()

                st.markdown("---")
                # BOTÕES DE DOCUMENTOS
                col1, col2, col3 = st.columns(3)
                
                # Reemitir Orçamento (Pega os dados que já estão salvos)
                pdf_orc = gerar_pdf_orcamento(r['cliente'], r['servico'], r['valor'], "Conforme combinado", "Verificar", "Padrão", "", info_estudio)
                col1.download_button("📄 Reemitir Orçamento", pdf_orc, f"Orcamento_{r['cliente']}.pdf", "application/pdf", key=f"re_orc{r['id']}")
                
                # Emitir Recibo (Lógica: se a entrada tá paga e o final não, gera recibo da entrada. Se o integral tá pago, gera do total)
                valor_recibo = r['valor'] if st_int == "Recebido" else r['valor_entrada']
                pdf_rec = gerar_pdf_recibo(r['cliente'], r['servico'], valor_recibo, info_estudio)
                col2.download_button("🧾 Emitir Recibo", pdf_rec, f"Recibo_{r['cliente']}.pdf", "application/pdf", key=f"rec{r['id']}")
                
                if col3.button("Excluir", key=f"del{r['id']}"):
                    cursor.execute("DELETE FROM projetos WHERE id=?", (r['id'],)); conn.commit(); st.rerun()

    elif escolha == "Configurações":
        st.title("⚙️ Dados do Studio")
        with st.form("cfg"):
            n_s = st.text_input("Nome", info_estudio[0]); z_s = st.text_input("WhatsApp", info_estudio[2])
            e_s = st.text_input("Endereço", info_estudio[4])
            if st.form_submit_button("SALVAR"):
                cursor.execute("UPDATE config SET nome_studio=?, contato=?, endereco=? WHERE id=1", (n_s, z_s, e_s))
                conn.commit(); st.rerun()
    conn.close()

if __name__ == "__main__":
    main()
