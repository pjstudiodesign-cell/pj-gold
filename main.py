import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração e Estilo (Mantidos para o padrão PJ Gold)
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #0d0d0d; }
        h1, h2, h3 { color: #D4AF37 !important; }
        label { color: #D4AF37 !important; font-weight: bold !important; }
        .stButton>button {
            background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%) !important;
            color: #000000 !important;
            font-weight: bold !important;
        }
        section[data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #D4AF37; }
        </style>
    """, unsafe_allow_html=True)

# Conexão Direta e Estável
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1PduECxYhVlp8QC5lTu2nasRQbBPGtDI8vEhs1qL6IgE"
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados(aba):
    try:
        # ttl=0 garante que ele pegue o dado mais novo sem cache
        return conn.read(spreadsheet=URL_PLANILHA, worksheet=aba, ttl=0).dropna(how='all')
    except:
        return pd.DataFrame()

# Interface Principal
def main():
    aplicar_estilo()
    st.sidebar.title("⚜️ PJ Gold")
    aba_ativa = st.sidebar.radio("Navegar:", ["Painel", "Novo Job", "Configurações"])
    
    df_jobs = carregar_dados("Projetos")
    df_cfg = carregar_dados("Config_Empresa")

    if aba_ativa == "Painel":
        st.title("⚜️ Painel PJ Gold")
        if not df_jobs.empty:
            v_total = pd.to_numeric(df_jobs['valor'], errors='coerce').sum()
            st.metric("Volume Total", f"R$ {v_total:,.2f}")
        else:
            st.info("Aguardando primeiro lançamento.")

    elif aba_ativa == "Novo Job":
        st.title("⚜️ Lançar Novo Job")
        with st.form("form_job"):
            col1, col2 = st.columns(2)
            c = col1.text_input("Cliente")
            v = col2.number_input("Valor", min_value=0.0)
            s = st.text_area("Serviço")
            if st.form_submit_button("GRAVAR NA NUVEM"):
                if c and s:
                    # Prepara o dado novo
                    novo = pd.DataFrame([{"cliente": c, "servicos": s, "valor": v, "data_inicio": datetime.now().strftime("%d/%m/%Y")}])
                    # Junta com o que já tem e salva
                    final = pd.concat([df_jobs, novo], ignore_index=True)
                    try:
                        conn.update(spreadsheet=URL_PLANILHA, data=final, worksheet="Projetos")
                        st.success("Gravado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}. Verifique se a planilha está aberta.")

    elif aba_ativa == "Configurações":
        st.title("⚜️ Configurar Empresa")
        with st.form("form_cfg"):
            nome_atual = df_cfg['nome'].iloc[0] if not df_cfg.empty else "PJ Gold"
            n = st.text_input("Nome da Marca", nome_atual)
            if st.form_submit_button("Atualizar"):
                nova_cfg = pd.DataFrame([{"nome": n, "slogam": "", "contato": "", "endereco": ""}])
                conn.update(spreadsheet=URL_PLANILHA, data=nova_cfg, worksheet="Config_Empresa")
                st.success("Configuração atualizada!")
                st.rerun()

if __name__ == "__main__":
    main()
