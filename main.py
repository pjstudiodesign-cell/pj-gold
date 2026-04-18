import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_gsheets import GSheetsConnection

# 1. Configuração da Página
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

# 2. Estilo Visual PJ GOLD (Corrigido para Fundo Preto Total)
def aplicar_estilo():
    st.markdown("""
        <style>
        /* Fundo principal do App */
        .stApp { background-color: #050505; }
        
        /* Forçando o fundo PRETO no Menu Lateral (Sidebar) */
        [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
            background-color: #050505 !important;
            border-right: 1px solid #FFD700;
        }

        /* Cor dos textos e ícones no Menu Lateral */
        [data-testid="stSidebarNav"] span, [data-testid="stSidebar"] p, label, .st-emotion-cache-17l6f7f {
            color: #FFD700 !important;
            font-weight: bold !important;
        }

        /* Títulos e textos gerais */
        h1, h2, h3, p, span { color: #FFD700 !important; }

        /* Estilo dos Botões (Texto Preto para contraste no Ouro) */
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%) !important;
            color: #000000 !important;
            font-weight: 900 !important;
            border-radius: 8px !important;
            width: 100% !important;
            text-transform: uppercase;
            border: none !important;
            height: 3em !important;
        }
        
        /* Inputs e caixas de texto */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
            background-color: #1a1a1a !important;
            color: #FFD700 !important;
            border: 1px solid #333 !important;
        }

        /* Ajuste de métricas */
        [data-testid="stMetricValue"] { color: #FFD700 !important; }
        [data-testid="stMetricLabel"] { color: #ffffff !important; }
        </style>
    """, unsafe_allow_html=True)

# 3. Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados():
    try:
        # Tenta ler a planilha. Se estiver vazia ou com erro, cria um DataFrame base
        df = conn.read(ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["id", "cliente", "servico", "valor", "status_integral", "prazo", "pagamento"])
        return df
    except:
        return pd.DataFrame(columns=["id", "cliente", "servico", "valor", "status_integral", "prazo", "pagamento"])

def salvar_dados(df):
    conn.update(data=df)
    st.cache_data.clear()

# 4. Funções de PDF
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo):
    try:
        pdf = FPDF()
        pdf.add_page()
        # Cabeçalho Black/Gold
        pdf.set_fill_color(10, 10, 10); pdf.rect(0, 0, 210, 65, 'F')
        pdf.set_y(15); pdf.set_font("Arial", 'B', 24); pdf.set_text_color(255, 215, 0)
        pdf.cell(0, 15, "PJ GOLD - ELITE SERVICE", ln=True, align='C')
        
        pdf.set_y(75); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
        pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
        pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
        
        pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "1. ESCOPO DO SERVICO", ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}")
        
        pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "2. CONDICOES", ln=True)
        pdf.set_font("Arial", '', 11); pdf.cell(0, 8, f"- Prazo Estimado: {prazo}", ln=True)
        pdf.cell(0, 8, f"- Pagamento: {pgto}", ln=True)
        
        pdf.set_y(-45); pdf.set_font("Arial", 'B', 20); pdf.set_text_color(184, 134, 11)
        pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
        
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except:
        return None

# 5. Interface Principal
def main():
    aplicar_estilo()
    df = ler_dados()
    
    st.sidebar.markdown("<h2 style='color:#FFD700; text-align:center;'>⚜️ PJ GOLD</h2>", unsafe_allow_html=True)
    menu = ["Painel", "Novo Job", "Gestão de Projetos"]
    escolha = st.sidebar.radio("Navegar:", menu)

    if escolha == "Painel":
        st.title("💰 Dashboard de Elite")
        if not df.empty and 'valor' in df.columns:
            # Garantir que a coluna valor é numérica
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
            
            total_rec = df[df['status_integral'] == 'Recebido']['valor'].sum()
            total_pend = df[df['status_integral'] != 'Recebido']['valor'].sum()
            
            c1, c2 = st.columns(2)
            with c1: st.metric("Total em Caixa (Ouro)", f"R$ {total_rec:,.2f}")
            with c2: st.metric("A Receber", f"R$ {total_pend:,.2f}")
            
            st.markdown("### Histórico Recente")
            st.dataframe(df[['cliente', 'servico', 'valor', 'status_integral']].tail(5), use_container_width=True)
        else:
            st.info("Aguardando o primeiro registro na planilha...")

    elif escolha == "Novo Job":
        st.title("➕ Cadastrar Novo Contrato")
        with st.form("orc_form"):
            col1, col2 = st.columns(2)
            n = col1.text_input("Nome do Cliente")
            v = col2.number_input("Valor do Investimento", min_value=0.0, step=50.0)
            ser = st.text_area("Descrição Técnica do Serviço")
            
            col3, col4 = st.columns(2)
            prz = col3.text_input("Prazo de Entrega", "7 dias úteis")
            pag = col4.text_input("Condição de Pagamento", "50% entrada / 50% entrega")
            
            if st.form_submit_button("GERAR E SALVAR NO GOOGLE SHEETS"):
                if n and ser:
                    novo_id = len(df) + 1
                    nova_linha = pd.DataFrame([{
                        "id": novo_id, "cliente": n, "servico": ser, "valor": v, 
                        "status_integral": "Pendente", "prazo": prz, "pagamento": pag
                    }])
                    # Atualiza o DataFrame e salva na nuvem
                    df_atualizado = pd.concat([df, nova_linha], ignore_index=True)
                    salvar_dados(df_atualizado)
                    st.success("✅ Ouro Guardado! Dados salvos na planilha.")
                    st.balloons()
                else:
                    st.error("Preencha Nome e Serviço!")

    elif escolha == "Gestão de Projetos":
        st.title("📂 Controle de Fluxo")
        if not df.empty:
            for i, r in df.iterrows():
                with st.expander(f"⚜️ {r['cliente']} | R$ {r['valor']}"):
                    st.markdown(f"**Serviço:** {r['servico']}")
                    st.markdown(f"**Pagamento:** {r['pagamento']}")
                    
                    c1, c2, c3 = st.columns(3)
                    novo_status = c1.selectbox("Status Financeiro", ["Pendente", "Recebido"], 
                                             index=0 if r['status_integral'] == "Pendente" else 1, key=f"st{i}")
                    
                    if c2.button("Atualizar Status", key=f"up{i}"):
                        df.at[i, 'status_integral'] = novo_status
                        salvar_dados(df)
                        st.rerun()
                    
                    # Gerador de PDF em tempo real
                    pdf_data = gerar_pdf_orcamento(r['cliente'], r['servico'], r['valor'], r['pagamento'], r['prazo'])
                    if pdf_data:
                        c3.download_button("📩 Baixar Orçamento PDF", pdf_data, f"Orcamento_{r['cliente']}.pdf", key=f"pdf{i}")
                    
                    if st.button("🗑️ Excluir Job", key=f"del{i}"):
                        df = df.drop(i)
                        salvar_dados(df)
                        st.rerun()
        else:
            st.warning("Nenhum projeto cadastrado.")

if __name__ == "__main__":
    main()
