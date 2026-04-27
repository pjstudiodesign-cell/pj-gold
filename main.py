import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PJ GOLD PRO", layout="wide", initial_sidebar_state="collapsed")

# --- CONEXÃO BLINDADA SUPABASE ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- FUNÇÃO DE CARREGAMENTO (MOTOR LÓGICO) ---
def carregar_dados():
    res = supabase.table("projetos").select("*").order("created_at", desc=True).execute()
    return res.data

# --- INTERFACE DE GESTÃO E EDIÇÃO (PRESERVADA) ---
st.title("📑 GESTÃO E EDIÇÃO")

dados = carregar_dados()
if dados:
    df = pd.DataFrame(dados)
    projeto_nomes = df['nome_projeto'].tolist()
    escolha = st.selectbox("Selecione o Projeto para Editar", [""] + projeto_nomes)

    if escolha:
        proj_edit = df[df['nome_projeto'] == escolha].iloc[0]
        
        with st.form("form_edicao"):
            col1, col2 = st.columns(2)
            with col1:
                nome_p = st.text_input("Nome do Projeto", proj_edit['nome_projeto'])
                cliente = st.text_input("Nome do Cliente", proj_edit['cliente'])
                cpf = st.text_input("CPF/CNPJ", proj_edit.get('cpf_cnpj', ''))
            with col2:
                zap = st.text_input("WhatsApp", proj_edit.get('whatsapp_cliente', ''))
                prazo = st.text_input("Prazo de Entrega", proj_edit.get('prazo', ''))
                valor = st.number_input("Valor Total", value=float(proj_edit['valor_total']))

            end = st.text_input("Endereço do Cliente Completo", proj_edit.get('endereco_cliente', ''))
            exig = st.text_input("Exigências do Cliente", proj_edit.get('exigencias', ''))
            desc = st.text_area("Descrição do Serviço", proj_edit['descricacao'])

            st.write("---")
            st.subheader("Controle de Pagamentos (50/50)")
            c1, c2, c3 = st.columns(3)
            with c1:
                st_total = st.selectbox("VALOR TOTAL", ["Pendente", "Recebido"], index=0 if proj_edit['status_total'] == "Pendente" else 1)
            with c2:
                st_ent = st.selectbox("ENTRADA (50%)", ["Pendente", "Recebido"], index=0 if proj_edit['status_entrada'] == "Pendente" else 1)
            with c3:
                st_fin = st.selectbox("FINAL (50%)", ["Pendente", "Recebido"], index=0 if proj_edit['status_final'] == "Pendente" else 1)

            if st.form_submit_button("✅ ATUALIZAR MOTOR"):
                supabase.table("projetos").update({
                    "nome_projeto": nome_p, "cliente": cliente, "cpf_cnpj": cpf,
                    "whatsapp_cliente": zap, "prazo": prazo, "valor_total": valor,
                    "endereco_cliente": end, "exigencias": exig, "descricacao": desc,
                    "status_total": st_total, "status_entrada": st_ent, "status_final": st_fin
                }).eq("id", proj_edit['id']).execute()
                st.success("Dados atualizados com sucesso!")
                st.rerun()

# --- OS BOTOES DE PDF CONTINUAM AQUI, MAS COM A LÓGICA ANTIGA PARA NÃO TRAVAR ---
st.info("O sistema de PDF está em modo de segurança. Use o código acima para restaurar o acesso.")
