import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. Configuração de Estilo PJ GOLD (Foco em Autoridade e Precisão)
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

# 2. Conexão com Google Sheets (Garantia de que nada se perde)
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados(aba):
    try:
        df = conn.read(worksheet=aba, ttl=0)
        return df if df is not None else pd.DataFrame()
    except:
        return pd.DataFrame()

# 3. Gerador de PDF com Dados Completos
def gerar_pdf(dados, info):
    pdf = FPDF()
    pdf.add_page()
    # Cabeçalho Gold
    pdf.set_fill_color(10, 10, 10); pdf.rect(0, 0, 210, 55, 'F')
    pdf.set_y(15); pdf.set_font("Arial", 'B', 22); pdf.set_text_color(255, 215, 0)
    pdf.cell(0, 10, str(info.get('nome_studio', 'PJ GOLD')).upper(), ln=True, align='C')
    
    # Detalhes do Orçamento
    pdf.set_y(65); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"ORÇAMENTO: {dados['n'].upper()}", ln=True)
    pdf.set_font("Arial", '', 11)
    conteudo = (
        f"Serviço: {dados['s']}\n"
        f"WhatsApp: {dados['t']}\n"
        f"Valor Total: R$ {dados['v']:,.2f}\n"
        f"Prazo de Entrega: {dados['prz']}\n"
        f"Forma de Pagamento: {dados['pgt']}\n"
        f"Observações: {dados['obs']}"
    )
    pdf.multi_cell(0, 8, conteudo)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 4. Interface Principal
def main():
    aplicar_estilo()
    df_p = ler_dados("Página1")
    df_c = ler_dados("Config")
    
    # Busca configurações gravadas
    info = df_c.iloc[0].to_dict() if not df_c.empty else {"nome_studio": "PJ GOLD"}
    
    st.sidebar.title(f"⚜️ {info.get('nome_studio', 'PJ GOLD')}")
    menu = st.sidebar.radio("Navegar", ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"])

    if menu == "Painel":
        st.title(f"📊 Painel Financeiro")
        # Cálculo dinâmico baseado no que está salvo na planilha
        valor_caixa = pd.to_numeric(df_p['valor'], errors='coerce').sum() if not df_p.empty else 0.0
        
        c1, c2 = st.columns(2)
        c1.metric("Dinheiro em Caixa", f"R$ {valor_caixa:,.2f}")
        c2.metric("Dinheiro a Receber", "R$ 0.00")
        st.write("---")
        if not df_p.empty:
            st.write("Últimas Movimentações:")
            st.dataframe(df_p.tail(5), use_container_width=True)

    elif menu == "Novo Job":
        st.title("➕ Novo Orçamento")
        with st.form("f_job"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Nome do Cliente")
            tel = c2.text_input("WhatsApp")
            
            c3, c4 = st.columns(2)
            v = c3.number_input("Valor do Serviço", min_value=0.0)
            prz = c4.text_input("Prazo de Entrega (Ex: 5 dias úteis)")
            
            pgt = st.text_input("Forma de Pagamento (Ex: 50% entrada + 50% entrega)")
            ser = st.text_area("Descrição do Serviço")
            obs = st.text_area("Observações Adicionais")
            
            if st.form_submit_button("SALVAR NO SISTEMA E GERAR PDF"):
                if n and v > 0:
                    try:
                        novo_reg = pd.DataFrame([{
                            "id": len(df_p)+1, "cliente": n, "telefone": tel, "servico": ser, 
                            "valor": v, "prazo": prz, "pagamento": pgt, "obs": obs, 
                            "data": datetime.now().strftime('%d/%m/%Y')
                        }])
                        df_final = pd.concat([df_p, novo_reg], ignore_index=True)
                        conn.update(worksheet="Página1", data=df_final)
                        st.success("✅ Orçamento gravado na planilha com sucesso!")
                        st.session_state['orc_atual'] = {"n":n,"t":tel,"s":ser,"v":v,"prz":prz,"pgt":pgt,"obs":obs}
                    except:
                        st.error("Erro ao gravar. Certifique-se que o acesso no Google Sheets está como 'Editor'.")
                else:
                    st.warning("Preencha o nome do cliente e o valor.")

        if 'orc_atual' in st.session_state:
            dados = st.session_state['orc_atual']
            pdf_arq = gerar_pdf(dados, info)
            st.download_button("📩 BAIXAR ORÇAMENTO (PDF)", pdf_arq, f"Orc_{dados['n']}.pdf")

    elif menu == "Gestão de Projetos":
        st.title("📋 Histórico de Orçamentos")
        if not df_p.empty:
            st.dataframe(df_p, use_container_width=True)
        else:
            st.info("Nenhum orçamento cadastrado ainda.")

    elif menu == "Configurações":
        st.title("⚙️ Configurações da PJ Studio")
        with st.form("f_conf"):
            nome = st.text_input("Nome do Studio", info.get('nome_studio', ''))
            slogan = st.text_input("Slogan", info.get('slogan', ''))
            zap = st.text_input("WhatsApp de Contato", info.get('contato', ''))
            mail = st.text_input("E-mail", info.get('email', ''))
            end = st.text_area("Endereço Completo", info.get('endereco', ''))
            if st.form_submit_button("ATUALIZAR DADOS DA EMPRESA"):
                try:
                    df_conf_nova = pd.DataFrame([{"nome_studio":nome, "slogan":slogan, "contato":zap, "email":mail, "endereco":end}])
                    conn.update(worksheet="Config", data=df_conf_nova)
                    st.success("✅ Dados atualizados!"); st.rerun()
                except:
                    st.error("Erro ao salvar configurações.")

if __name__ == "__main__":
    main()
