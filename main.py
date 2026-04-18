import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. ESTILO VISUAL MANTIDO (PADRÃO PJ GOLD)
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
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
            background-color: #1a1a1a !important; color: #FFD700 !important; border: 1px solid #333 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO MANTIDA
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados(aba):
    try:
        df = conn.read(worksheet=aba, ttl=0)
        return df if df is not None else pd.DataFrame()
    except:
        return pd.DataFrame()

# 3. PDF MANTIDO COM TODOS OS CAMPOS
def gerar_pdf(dados, info):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(10, 10, 10); pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_y(15); pdf.set_font("Arial", 'B', 22); pdf.set_text_color(255, 215, 0)
    pdf.cell(0, 10, str(info.get('nome_studio', 'PJ GOLD')).upper(), ln=True, align='C')
    pdf.set_y(65); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"ORÇAMENTO: {dados['n'].upper()}", ln=True)
    pdf.set_font("Arial", '', 11)
    conteudo = f"Serviço: {dados['s']}\nWhatsApp: {dados['t']}\nValor: R$ {dados['v']:,.2f}\nPrazo: {dados['prz']}\nPagamento: {dados['pgt']}\nObs: {dados['obs']}"
    pdf.multi_cell(0, 8, conteudo)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 4. INTERFACE E CORREÇÃO DE SALVAMENTO
def main():
    aplicar_estilo()
    df_p = ler_dados("Página1")
    df_c = ler_dados("Config")
    
    info = df_c.iloc[0].to_dict() if not df_c.empty else {"nome_studio": "PJ GOLD", "slogan": "", "contato": "", "email": "", "endereco": ""}
    
    st.sidebar.title(f"⚜️ {info.get('nome_studio')}")
    menu = st.sidebar.radio("Navegar", ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"])

    if menu == "Painel":
        st.title("📊 Painel Financeiro")
        valor_caixa = pd.to_numeric(df_p['valor'], errors='coerce').sum() if not df_p.empty else 0.0
        c1, c2 = st.columns(2)
        c1.metric("Dinheiro em Caixa", f"R$ {valor_caixa:,.2f}")
        c2.metric("Dinheiro a Receber", "R$ 0.00")
        if not df_p.empty: st.dataframe(df_p.tail(5), use_container_width=True)

    elif menu == "Novo Job":
        st.title("➕ Novo Orçamento")
        with st.form("f_job"):
            c1, c2 = st.columns(2)
            n, tel = c1.text_input("Nome do Cliente"), c2.text_input("WhatsApp")
            v, prz = st.number_input("Valor", min_value=0.0), st.text_input("Prazo")
            pgt = st.text_input("Forma de Pagamento")
            ser, obs = st.text_area("Serviço"), st.text_area("Observações")
            if st.form_submit_button("SALVAR E GERAR PDF"):
                try:
                    nova = pd.DataFrame([{"id": len(df_p)+1, "cliente": n, "telefone": tel, "servico": ser, "valor": v, "prazo": prz, "pagamento": pgt, "obs": obs, "data": datetime.now().strftime('%d/%m/%Y')}])
                    conn.update(worksheet="Página1", data=pd.concat([df_p, nova], ignore_index=True))
                    st.success("✅ Salvo com sucesso!")
                    st.session_state['orc'] = {"n":n,"t":tel,"s":ser,"v":v,"prz":prz,"pgt":pgt,"obs":obs}
                except: st.error("Erro ao salvar. Verifique se o Google Sheets está compartilhado corretamente.")

    elif menu == "Gestão de Projetos":
        st.title("📋 Gestão de Projetos")
        if not df_p.empty: st.dataframe(df_p, use_container_width=True)

    elif menu == "Configurações":
        st.title("⚙️ Configurações da Empresa")
        with st.form("f_conf"):
            n_st = st.text_input("Nome do Studio", info.get('nome_studio', ''))
            sl_st = st.text_input("Slogan", info.get('slogan', ''))
            ct_st = st.text_input("WhatsApp de Contato", info.get('contato', ''))
            em_st = st.text_input("E-mail", info.get('email', ''))
            en_st = st.text_area("Endereço Completo", info.get('endereco', ''))
            if st.form_submit_button("ATUALIZAR CONFIGURAÇÕES"):
                try:
                    df_conf_up = pd.DataFrame([{"nome_studio": n_st, "slogan": sl_st, "contato": ct_st, "email": em_st, "endereco": en_st}])
                    conn.update(worksheet="Config", data=df_conf_up)
                    st.success("✅ Configurações salvas!"); st.rerun()
                except Exception as e:
                    st.error("Erro ao salvar. O Google Sheets requer permissão de escrita.")

if __name__ == "__main__":
    main()
