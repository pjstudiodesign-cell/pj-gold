import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. Identidade PJ GOLD
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #050505; }
        [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #FFD700; }
        h1, h2, h3, p, span, label { color: #FFD700 !important; }
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%) !important;
            color: #000 !important; font-weight: bold; border-radius: 8px;
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background-color: #1a1a1a !important; color: #FFD700 !important; border: 1px solid #333 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# 2. Conexão Resiliente
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados(aba):
    try:
        df = conn.read(worksheet=aba, ttl=0)
        return df if df is not None else pd.DataFrame()
    except:
        return pd.DataFrame()

# 3. PDF com todos os campos (Prazo e Pagamento)
def gerar_pdf(dados, info):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(10, 10, 10); pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_y(15); pdf.set_font("Arial", 'B', 22); pdf.set_text_color(255, 215, 0)
    pdf.cell(0, 10, str(info.get('nome_studio', 'PJ GOLD')).upper(), ln=True, align='C')
    pdf.set_y(65); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"ORÇAMENTO: {dados['n'].upper()}", ln=True)
    pdf.set_font("Arial", '', 11)
    txt = (f"Serviço: {dados['s']}\nWhatsApp: {dados['t']}\nValor: R$ {dados['v']:,.2f}\n"
           f"Prazo: {dados['prz']}\nPagamento: {dados['pgt']}\nObs: {dados['obs']}")
    pdf.multi_cell(0, 8, txt)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 4. Execução Principal
def main():
    aplicar_estilo()
    df_p = ler_dados("Página1")
    df_c = ler_dados("Config")
    
    info = df_c.iloc[0].to_dict() if not df_c.empty else {"nome_studio": "PJ GOLD"}
    
    st.sidebar.title(f"⚜️ {info.get('nome_studio')}")
    menu = st.sidebar.radio("Navegar", ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"])

    if menu == "Painel":
        st.title("📊 Painel Financeiro")
        valor_caixa = pd.to_numeric(df_p['valor'], errors='coerce').sum() if not df_p.empty else 0.0
        c1, c2 = st.columns(2)
        c1.metric("Dinheiro em Caixa", f"R$ {valor_caixa:,.2f}")
        c2.metric("Dinheiro a Receber", "R$ 0.00")
        if not df_p.empty: st.dataframe(df_p, use_container_width=True)

    elif menu == "Novo Job":
        st.title("➕ Novo Orçamento")
        with st.form("f_job"):
            c1, c2 = st.columns(2)
            n, tel = c1.text_input("Nome do Cliente"), c2.text_input("WhatsApp")
            v, prz = st.number_input("Valor", min_value=0.0), st.text_input("Prazo")
            pgt = st.text_input("Forma de Pagamento")
            ser, obs = st.text_area("Serviço"), st.text_area("Observações")
            
            if st.form_submit_button("GERAR PDF E TENTAR SALVAR"):
                # Garante que o PDF seja gerado mesmo se o salvamento falhar
                st.session_state['orc_data'] = {"n":n,"t":tel,"s":ser,"v":v,"prz":prz,"pgt":pgt,"obs":obs}
                try:
                    novo = pd.DataFrame([{"id": len(df_p)+1, "cliente": n, "telefone": tel, "servico": ser, "valor": v, "prazo": prz, "pagamento": pgt, "obs": obs, "data": datetime.now().strftime('%d/%m/%Y')}])
                    df_up = pd.concat([df_p, novo], ignore_index=True)
                    conn.update(worksheet="Página1", data=df_up)
                    st.success("✅ Salvo no Google Sheets!")
                except:
                    st.warning("⚠️ Erro de permissão no Google Sheets. O PDF está disponível abaixo para você não perder o cliente!")

        if 'orc_data' in st.session_state:
            arq = gerar_pdf(st.session_state['orc_data'], info)
            st.download_button("📩 BAIXAR PDF DO CLIENTE", arq, f"Orc_{st.session_state['orc_data']['n']}.pdf")

    elif menu == "Gestão de Projetos":
        st.title("📋 Gestão de Projetos")
        if not df_p.empty: st.dataframe(df_p, use_container_width=True)
        else: st.info("Nenhum dado encontrado na planilha.")

    elif menu == "Configurações":
        st.title("⚙️ Configurações")
        st.text_input("Nome do Studio", info.get('nome_studio', 'PJ GOLD'))
        st.info("Nota: Para salvar alterações aqui e no banco de dados, é necessário configurar as credenciais JSON no Streamlit.")

if __name__ == "__main__":
    main()
