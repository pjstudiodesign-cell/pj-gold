import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 1. Identidade Visual Premium PJ Gold
st.set_page_config(page_title="PJ Gold System", page_icon="⚜️", layout="wide")

def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #0d0d0d; }
        h1, h2, h3 { color: #D4AF37 !important; }
        [data-testid="stSidebarNav"] span { color: #ffffff !important; font-weight: bold !important; }
        label { color: #D4AF37 !important; font-weight: bold !important; }
        .stButton>button {
            background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%) !important;
            color: #000000 !important; font-weight: 900 !important; width: 100% !important;
            border-radius: 8px !important; border: none !important; text-transform: uppercase;
        }
        section[data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #D4AF37; }
        .stMetric { background-color: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #333; }
        [data-testid="stMetricValue"] { color: #D4AF37 !important; }
        </style>
    """, unsafe_allow_html=True)

# 2. Conexão
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1PduECxYhVlp8QC5lTu2nasRQbBPGtDI8vEhs1qL6IgE"
conn = st.connection("gsheets", type=GSheetsConnection)

def buscar_dados(aba):
    try:
        return conn.read(spreadsheet=URL_PLANILHA, worksheet=aba, ttl=0).dropna(how='all')
    except:
        return pd.DataFrame()

# 3. Gerador de PDF (Com todos os campos exigidos)
def gerar_pdf(cliente, servico, valor, pgto, prazo, rev, obs, config):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(20, 20, 20); pdf.rect(0, 0, 210, 60, 'F')
        pdf.set_y(15); pdf.set_font("Arial", 'B', 22); pdf.set_text_color(212, 175, 55)
        n_marca = config['nome'].iloc[0] if not config.empty else "PJ Gold"
        pdf.cell(0, 10, n_marca, ln=True, align='C')
        pdf.set_y(70); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"CLIENTE: {str(cliente).upper()}", ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"Serviço: {servico}\nObs: {obs}")
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "CONDIÇÕES", ln=True)
        pdf.set_font("Arial", '', 11); pdf.cell(0, 7, f"Prazo: {prazo} | Revisões: {rev} | Pagamento: {pgto}", ln=True)
        pdf.set_y(-40); pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, f"TOTAL: R$ {valor:,.2f}", ln=True, align='R')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

# 4. Interface Principal
def main():
    aplicar_estilo()
    st.sidebar.title("⚜️ PJ Gold")
    menu = ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"]
    escolha = st.sidebar.radio("Navegar:", menu)
    
    df_projs = buscar_dados("Projetos")
    df_cfg = buscar_dados("Config_Empresa")

    if escolha == "Painel":
        st.title("⚜️ Painel PJ Gold")
        total_caixa = 0.0; total_pend = 0.0
        if not df_projs.empty:
            for _, r in df_projs.iterrows():
                v = pd.to_numeric(r.get('Valor', 0), errors='coerce') or 0.0
                if str(r.get('status')).strip() == 'Recebido': total_caixa += v
                else: total_pend += v
        c1, c2 = st.columns(2)
        c1.metric("Total em Caixa", f"R$ {total_caixa:,.2f}")
        c2.metric("A Receber", f"R$ {total_pend:,.2f}")
        st.dataframe(df_projs, use_container_width=True)

    elif escolha == "Novo Job":
        st.title("⚜️ Novo Orçamento")
        with st.form("orc_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            nome_c = col1.text_input("Cliente")
            zap_c = col2.text_input("WhatsApp")
            v_total = st.number_input("Valor Total", min_value=0.0, step=0.01)
            servico_desc = st.text_area("Serviço")
            obs_texto = st.text_area("Observações")
            c3, c4, c5 = st.columns(3)
            prazo_c = c3.text_input("Prazo", "10 dias úteis")
            rev_c = c4.text_input("Revisões", "2")
            pgto_c = c5.text_input("Pagamento", "50% entrada / 50% entrega")
            
            if st.form_submit_button("SALVAR NA NUVEM"):
                if nome_c and servico_desc:
                    try:
                        novo_d = pd.DataFrame([{"cliente": nome_c, "servicos": servico_desc, "Valor": v_total, "status": "Pendente", "data_inicio": datetime.now().strftime("%d/%m/%Y"), "telefone": zap_c, "prazo_salvo": prazo_c, "rev_salvo": rev_c, "pgto_salvo": pgto_c, "obs_salvo": obs_texto}])
                        res = pd.concat([df_projs, novo_d], ignore_index=True)
                        conn.update(spreadsheet=URL_PLANILHA, data=res, worksheet="Projetos")
                        st.success("✅ Salvo!"); st.rerun()
                    except:
                        st.error("Erro ao gravar. Verifique o Secrets.")

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Gestão e Financeiro")
        if df_projs.empty: st.info("Sem dados.")
        else:
            for i, r in df_projs.iterrows():
                with st.expander(f"📌 {r.get('cliente')} | R$ {float(r.get('Valor',0)):.2f}"):
                    st.write(f"**Serviço:** {r.get('servicos')}")
                    c_st, c_pdf = st.columns(2)
                    n_status = c_st.selectbox("Status", ["Pendente", "Recebido"], index=0 if r.get('status') == "Pendente" else 1, key=f"st{i}")
                    if c_st.button("Atualizar", key=f"up{i}"):
                        df_projs.at[i, 'status'] = n_status
                        conn.update(spreadsheet=URL_PLANILHA, data=df_projs, worksheet="Projetos")
                        st.success("OK!"); st.rerun()
                    
                    pdf_data = gerar_pdf(r['cliente'], r.get('servicos'), r.get('Valor'), r.get('pgto_salvo','Combinado'), r.get('prazo_salvo','Combinado'), r.get('rev_salvo','Padrão'), r.get('obs_salvo',''), df_cfg)
                    if pdf_data:
                        c_pdf.download_button("Baixar PDF", pdf_data, f"Orc_{r['cliente']}.pdf", key=f"dl{i}")

    elif escolha == "Configurações":
        st.title("⚜️ Configurações da Empresa")
        with st.form("cfg_form"):
            n_v = df_cfg['nome'].iloc[0] if not df_cfg.empty else "PJ Gold"
            s_v = df_cfg['slogam'].iloc[0] if not df_cfg.empty else ""
            c_v = df_cfg['contato'].iloc[0] if not df_cfg.empty else ""
            e_v = df_cfg['endereco'].iloc[0] if not df_cfg.empty else ""
            n_marca = st.text_input("Marca", n_v); s_marca = st.text_input("Slogan", s_v)
            c_marca = st.text_input("Zap", c_v); e_marca = st.text_area("Endereço", e_v)
            if st.form_submit_button("Salvar"):
                n_cfg = pd.DataFrame([{"nome": n_marca, "slogam": s_marca, "contato": c_marca, "endereco": e_marca}])
                conn.update(spreadsheet=URL_PLANILHA, data=n_cfg, worksheet="Config_Empresa")
                st.success("Salvo!"); st.rerun()

if __name__ == "__main__":
    main()
