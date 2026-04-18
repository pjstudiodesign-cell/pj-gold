import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. Configuração da Página
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

# 2. Estilo Visual PJ GOLD (Restaurado e Fiel)
def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #050505; }
        [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
            background-color: #050505 !important;
            border-right: 1px solid #FFD700;
        }
        [data-testid="stSidebarNav"] span, [data-testid="stSidebar"] p, label {
            color: #FFD700 !important;
            font-weight: bold !important;
        }
        h1, h2, h3, p, span { color: #FFD700 !important; }
        div[data-testid="metric-container"] {
            background-color: #111111;
            border: 1px solid #333;
            padding: 20px;
            border-radius: 10px;
        }
        [data-testid="stMetricValue"] { color: #FFD700 !important; }
        [data-testid="stMetricLabel"] { color: #ffffff !important; }
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%) !important;
            color: #000000 !important;
            font-weight: 900 !important;
            border-radius: 8px !important;
            text-transform: uppercase;
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
            background-color: #1a1a1a !important;
            color: #FFD700 !important;
            border: 1px solid #333 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# 3. Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados_projetos():
    try:
        df = conn.read(worksheet="Página1", ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["id", "cliente", "servico", "valor", "status_integral", "prazo", "pagamento", "obs", "telefone"])
        return df
    except:
        return pd.DataFrame(columns=["id", "cliente", "servico", "valor", "status_integral", "prazo", "pagamento", "obs", "telefone"])

def ler_config():
    try:
        df_conf = conn.read(worksheet="Config", ttl=0)
        if df_conf is not None and not df_conf.empty:
            return df_conf.iloc[0].to_dict()
    except:
        pass
    return {"nome_studio": "PJ GOLD", "slogan": "Elite Service", "contato": "", "email": "", "endereco": ""}

# 4. Interface Principal
def main():
    aplicar_estilo()
    df = ler_dados_projetos()
    info_f = ler_config()
    
    st.sidebar.markdown(f"<h2 style='color:#FFD700; text-align:center;'>⚜️ {info_f.get('nome_studio', 'PJ GOLD')}</h2>", unsafe_allow_html=True)
    menu = ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"]
    escolha = st.sidebar.radio("Navegar:", menu)

    if escolha == "Painel":
        st.title(f"💰 Painel {info_f.get('nome_studio', 'PJ GOLD')}")
        total_rec = 0.0
        total_pend = 0.0
        if not df.empty and 'valor' in df.columns:
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
            total_rec = df[df['status_integral'] == 'Recebido']['valor'].sum()
            total_pend = df[df['status_integral'] != 'Recebido']['valor'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Total em Caixa", f"R$ {total_rec:,.2f}")
        c2.metric("A Receber", f"R$ {total_pend:,.2f}")
        
        if not df.empty:
            st.markdown("---")
            st.dataframe(df[['cliente', 'valor', 'status_integral']].tail(5), use_container_width=True)

    elif escolha == "Novo Job":
        st.title("➕ Novo Contrato")
        with st.form("orc"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Nome do Cliente")
            t = c2.text_input("WhatsApp do Cliente")
            cv, cp = st.columns(2)
            v = cv.number_input("Valor", min_value=0.0)
            prz = cp.text_input("Prazo", "7 dias")
            ser = st.text_area("Descrição do Serviço")
            ob_cli = st.text_area("Exigências/OBS")
            pag = st.text_input("Pagamento", "50/50")
            if st.form_submit_button("SALVAR"):
                nova = pd.DataFrame([{"id": len(df)+1, "cliente": n, "telefone": t, "servico": ser, "valor": v, "status_integral": "Pendente", "prazo": prz, "pagamento": pag, "obs": ob_cli}])
                conn.update(worksheet="Página1", data=pd.concat([df, nova], ignore_index=True))
                st.success("✅ Salvo!"); st.rerun()

    elif escolha == "Configurações":
        st.title("⚙️ Configurações da Empresa")
        with st.form("conf_completa"):
            # RESTAURADO: Todos os campos que você tinha antes
            nome = st.text_input("Nome do Studio/Empresa", info_f.get('nome_studio', ''))
            slogan = st.text_input("Slogan ou Subtítulo", info_f.get('slogan', ''))
            zap = st.text_input("WhatsApp de Contato", info_f.get('contato', ''))
            mail = st.text_input("E-mail", info_f.get('email', ''))
            end = st.text_area("Endereço Completo", info_f.get('endereco', ''))
            
            if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
                df_conf = pd.DataFrame([{"nome_studio": nome, "slogan": slogan, "contato": zap, "email": mail, "endereco": end}])
                conn.update(worksheet="Config", data=df_conf)
                st.success("Dados da Empresa Salvos com Sucesso!"); st.rerun()

if __name__ == "__main__":
    main()
