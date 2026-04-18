import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. Configuração Visual PJ GOLD / SaarteSvm
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #050505; }
        [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #FFD700; }
        h1, h2, h3, p, span, label { color: #FFD700 !important; }
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%) !important;
            color: #000000 !important; font-weight: bold !important;
            border-radius: 8px !important;
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background-color: #1a1a1a !important; color: #FFD700 !important; border: 1px solid #333 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# 2. Conexão com a Planilha (Link simplificado nos Secrets é essencial)
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados(aba):
    try:
        df = conn.read(worksheet=aba, ttl=0)
        return df if df is not None else pd.DataFrame()
    except:
        return pd.DataFrame()

# 3. Função de PDF Profissional
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

# 4. Interface Principal
def main():
    aplicar_estilo()
    df_projetos = ler_dados("Página1")
    df_config = ler_dados("Config")
    
    # Carregar configurações salvas ou usar padrão
    info = df_config.iloc[0].to_dict() if not df_config.empty else {"nome_studio": "PJ GOLD", "slogan": "Elite Service"}
    
    st.sidebar.title(f"⚜️ {info.get('nome_studio')}")
    menu = st.sidebar.radio("Navegar", ["Painel", "Novo Job", "Configurações"])

    if menu == "Painel":
        st.title(f"📊 Painel {info.get('nome_studio')}")
        if not df_projetos.empty:
            # Garante que a coluna valor é numérica para o cálculo
            df_projetos['valor'] = pd.to_numeric(df_projetos['valor'], errors='coerce').fillna(0)
            total = df_projetos['valor'].sum()
            st.metric("Total em Orçamentos", f"R$ {total:,.2f}")
            st.dataframe(df_projetos, use_container_width=True)
        else:
            st.warning("Nenhum dado encontrado na planilha Página1.")

    elif menu == "Novo Job":
        st.title("➕ Novo Orçamento")
        with st.form("f_job"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Nome do Cliente")
            tel = c2.text_input("WhatsApp")
            v = st.number_input("Valor do Serviço", min_value=0.0)
            ser = st.text_area("Descrição do Serviço")
            if st.form_submit_button("SALVAR E GERAR PDF"):
                if n and ser:
                    try:
                        nova_linha = pd.DataFrame([{"id": len(df_projetos)+1, "cliente": n, "telefone": tel, "servico": ser, "valor": v, "data": datetime.now().strftime('%d/%m/%Y')}])
                        df_atualizado = pd.concat([df_projetos, nova_linha], ignore_index=True)
                        conn.update(worksheet="Página1", data=df_atualizado)
                        st.success("✅ Orçamento salvo na planilha!")
                        st.session_state['pdf_data'] = {"n": n, "t": tel, "s": ser, "v": v}
                    except Exception as e:
                        st.error(f"Erro ao salvar: Verifique se a aba 'Página1' existe na planilha.")
                else:
                    st.error("Preencha o nome do cliente e o serviço.")

        if 'pdf_data' in st.session_state:
            p = st.session_state['pdf_data']
            pdf_arq = gerar_pdf(p['n'], p['t'], p['s'], p['v'], info)
            st.download_button("📩 BAIXAR PDF DO ORÇAMENTO", pdf_arq, f"Orcamento_{p['n']}.pdf")

    elif menu == "Configurações":
        st.title("⚙️ Configurações da Empresa")
        with st.form("f_conf"):
            nome = st.text_input("Nome do Studio/Empresa", info.get('nome_studio', ''))
            slogan = st.text_input("Slogan ou Subtítulo", info.get('slogan', ''))
            if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
                try:
                    df_novo_conf = pd.DataFrame([{"nome_studio": nome, "slogan": slogan}])
                    conn.update(worksheet="Config", data=df_novo_conf)
                    st.success("Configurações atualizadas!"); st.rerun()
                except:
                    st.error("Erro: Verifique se a aba 'Config' existe na sua planilha.")

if __name__ == "__main__":
    main()
