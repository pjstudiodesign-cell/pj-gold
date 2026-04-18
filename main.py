import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. Configuração da Página
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

# 2. Estilo Visual PJ GOLD (Fundo Preto Total e Letras Ouro)
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
            # Retorna os dados que JÁ ESTÃO na planilha do Google
            return df_conf.iloc[0].to_dict()
    except:
        pass
    # Se der erro ou estiver vazio, usa os nomes que você definiu
    return {"nome_studio": "PJ GOLD", "slogan": "Elite Service", "contato": "", "email": "", "endereco": ""}

# 5. Interface
def main():
    aplicar_estilo()
    df = ler_dados_projetos()
    info_f = ler_config()
    
    st.sidebar.markdown(f"<h2 style='color:#FFD700; text-align:center;'>⚜️ {info_f['nome_studio']}</h2>", unsafe_allow_html=True)
    menu = ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"]
    escolha = st.sidebar.radio("Navegar:", menu)

    if escolha == "Painel":
        st.title(f"💰 Painel {info_f['nome_studio']}")
        
        # Dashboard SEMPRE mostra R$ 0,00 se não houver dados
        total_rec = 0.0
        total_pend = 0.0
        
        if not df.empty and 'valor' in df.columns:
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
            total_rec = df[df['status_integral'] == 'Recebido']['valor'].sum()
            total_pend = df[df['status_integral'] != 'Recebido']['valor'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Total em Caixa", f"R$ {total_rec:,.2f}")
        c2.metric("A Receber", f"R$ {total_pend:,.2f}")
        
        st.markdown("---")
        if not df.empty:
            st.dataframe(df[['cliente', 'valor', 'status_integral']].tail(5), use_container_width=True)
        else:
            st.write("Aguardando registros na planilha...")

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
                st.success("✅ Salvo no Sheets!"); st.rerun()

    elif escolha == "Configurações":
        st.title("⚙️ Configurações")
        with st.form("conf"):
            # Aqui ele puxa o que já estava salvo no Google Sheets
            novo_nome = st.text_input("Nome do Studio", info_f.get('nome_studio', 'PJ GOLD'))
            novo_slogan = st.text_input("Slogan", info_f.get('slogan', 'Elite Service'))
            if st.form_submit_button("SALVAR"):
                df_conf = pd.DataFrame([{"nome_studio": novo_nome, "slogan": novo_slogan, "contato": "", "email": "", "endereco": ""}])
                conn.update(worksheet="Config", data=df_conf)
                st.success("Configurações Preservadas!"); st.rerun()

if __name__ == "__main__":
    main()
