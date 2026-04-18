import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. Configuração e Estilo PJ GOLD
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #050505; }
        [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #FFD700; }
        h1, h2, h3, p, span, label { color: #FFD700 !important; }
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%) !important;
            color: #000000 !important; font-weight: bold !important; border-radius: 8px !important;
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background-color: #1a1a1a !important; color: #FFD700 !important; border: 1px solid #333 !important;
        }
        /* Estilo dos Cards do Painel */
        .metric-card {
            background-color: #111; border: 1px solid #333; padding: 20px; border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

# 2. Conexão
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados(aba):
    try:
        df = conn.read(worksheet=aba, ttl=0)
        return df if df is not None else pd.DataFrame()
    except:
        return pd.DataFrame()

# 3. PDF
def gerar_pdf(c, t, s, v, info):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(10, 10, 10); pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_y(15); pdf.set_font("Arial", 'B', 22); pdf.set_text_color(255, 215, 0)
    pdf.cell(0, 10, str(info.get('nome_studio', 'PJ GOLD')).upper(), ln=True, align='C')
    pdf.set_y(70); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"ORÇAMENTO PARA: {c.upper()}", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, f"Serviço: {s}\nWhatsApp: {t}\nValor Total: R$ {v:,.2f}")
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 4. App
def main():
    aplicar_estilo()
    df_p = ler_dados("Página1")
    df_c = ler_dados("Config")
    
    info = df_c.iloc[0].to_dict() if not df_c.empty else {"nome_studio": "PJ GOLD"}
    
    st.sidebar.title(f"⚜️ {info.get('nome_studio', 'PJ GOLD')}")
    menu = st.sidebar.radio("Navegar", ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"])

    if menu == "Painel":
        st.title(f"📊 Painel {info.get('nome_studio')}")
        # Recuperação dos Indicadores Financeiros
        if not df_p.empty:
            df_p['valor'] = pd.to_numeric(df_p['valor'], errors='coerce').fillna(0)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total em Caixa", f"R$ {df_p['valor'].sum():,.2f}")
            with col2:
                st.metric("A Receber", "R$ 0.00") # Campo mantido conforme imagem original
            st.write("---")
            st.dataframe(df_p, use_container_width=True)
        else:
            st.info("Aguardando lançamentos para calcular o caixa.")

    elif menu == "Novo Job":
        st.title("➕ Novo Orçamento")
        with st.form("f_job"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Nome do Cliente")
            tel = c2.text_input("WhatsApp")
            v = st.number_input("Valor do Serviço", min_value=0.0)
            ser = st.text_area("Descrição do Serviço")
            obs = st.text_area("Observações")
            if st.form_submit_button("SALVAR E GERAR PDF"):
                try:
                    nova = pd.DataFrame([{"id": len(df_p)+1, "cliente": n, "telefone": tel, "servico": ser, "valor": v, "obs": obs, "data": datetime.now().strftime('%d/%m/%Y')}])
                    df_up = pd.concat([df_p, nova], ignore_index=True)
                    conn.update(worksheet="Página1", data=df_up)
                    st.success("✅ Salvo!")
                    st.session_state['pdf'] = {"n":n,"t":tel,"s":ser,"v":v}
                except: st.error("Erro de Permissão: Altere o Sheets para 'Editor'.")

        if 'pdf' in st.session_state:
            p = st.session_state['pdf']
            arq = gerar_pdf(p['n'], p['t'], p['s'], p['v'], info)
            st.download_button("📩 BAIXAR PDF", arq, f"Orc_{p['n']}.pdf")

    elif menu == "Gestão de Projetos":
        st.title("📋 Gestão de Projetos")
        if not df_p.empty:
            st.dataframe(df_p, use_container_width=True)

    elif menu == "Configurações":
        st.title("⚙️ Configurações da Empresa")
        with st.form("f_conf"):
            nome = st.text_input("Nome do Studio", info.get('nome_studio', ''))
            slogan = st.text_input("Slogan", info.get('slogan', ''))
            zap = st.text_input("WhatsApp de Contato", info.get('contato', ''))
            mail = st.text_input("E-mail", info.get('email', ''))
            end = st.text_area("Endereço Completo", info.get('endereco', ''))
            if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
                try:
                    df_nc = pd.DataFrame([{"nome_studio":nome, "slogan":slogan, "contato":zap, "email":mail, "endereco":end}])
                    conn.update(worksheet="Config", data=df_nc)
                    st.success("Atualizado!"); st.rerun()
                except: st.error("Erro ao salvar.")

if __name__ == "__main__":
    main()
