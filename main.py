import streamlit as st
from fpdf import FPDF
from datetime import datetime

def gerar_pdf(dados_projeto, dados_empresa, tipo="ORÇAMENTO"):
    pdf = FPDF()
    pdf.add_page()
    
    # --- CABEÇALHO PREMIUM (PJ STUDIO DESIGN) ---
    pdf.set_fill_color(201, 161, 64)  # Tom Ouro/Dourado
    pdf.rect(0, 0, 210, 45, 'F')
    
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "PJ Studio Design", ln=True, align='C')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, f"CNPJ/CPF: {dados_empresa.get('cnpj', '')} | WhatsApp: {dados_empresa.get('whatsapp', '')}", ln=True, align='C')
    pdf.cell(0, 5, f"E-mail: {dados_empresa.get('email', '')}", ln=True, align='C')
    pdf.cell(0, 5, f"Endereço: {dados_empresa.get('endereco', '')}", ln=True, align='C')
    
    pdf.ln(20)
    pdf.set_text_color(0, 0, 0)

    if tipo == "ORÇAMENTO":
        # Título Isolado e Nome do Projeto Abaixo (Para não cortar)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "ORÇAMENTO PROFISSIONAL", ln=True, align='L')
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(201, 161, 64)
        pdf.cell(0, 10, f"PROJETO: {dados_projeto['nome_projeto']}", ln=True, align='L')
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

        # Bloco do Contratante Completo
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, "DADOS DO CONTRATANTE:", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, f"Cliente: {dados_projeto['cliente']}", ln=True)
        pdf.cell(0, 6, f"CPF/CNPJ: {dados_projeto.get('cpf_cnpj', 'Não informado')}", ln=True)
        pdf.cell(0, 6, f"WhatsApp: {dados_projeto.get('whatsapp_cliente', 'Não informado')}", ln=True)
        pdf.cell(0, 6, f"Endereço: {dados_projeto.get('endereco_cliente', 'Não informado')}", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, "DETALHES DO SERVIÇO:", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 6, f"Descrição: {dados_projeto['descricacao']}")
        pdf.multi_cell(0, 6, f"Exigências: {dados_projeto.get('exigencias', 'Nenhuma')}")
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"VALOR TOTAL: R$ {dados_projeto['valor_total']:.2f}", ln=True, align='R')

    elif tipo == "RECIBO":
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"RECIBO DE PAGAMENTO: {dados_projeto['nome_projeto']}", ln=True, align='L')
        pdf.ln(10)
        
        # Lógica de Texto do Recibo Baseada nos Status de Pagamento
        status_txt = "QUITAÇÃO INTEGRAL"
        valor_recibo = dados_projeto['valor_total']
        
        if dados_projeto.get('status_entrada') == 'Recebido' and dados_projeto.get('status_final') == 'Pendente':
            status_txt = "ENTRADA (50%)"
            valor_recibo = dados_projeto['valor_total'] / 2
        elif dados_projeto.get('status_final') == 'Recebido' and dados_projeto.get('status_total') == 'Pendente':
            status_txt = "PAGAMENTO FINAL (50%)"
            valor_recibo = dados_projeto['valor_total'] / 2

        pdf.set_font("Arial", '', 12)
        texto_recibo = (f"Declaramos para os devidos fins que recebemos de {dados_projeto['cliente']}, "
                        f"inscrito no CPF/CNPJ {dados_projeto.get('cpf_cnpj', '__________')}, a importância de "
                        f"R$ {valor_recibo:.2f} referente ao pagamento de {status_txt} do serviço de "
                        f"{dados_projeto['nome_projeto']}.")
        pdf.multi_cell(0, 8, texto_recibo)
        
        pdf.ln(20)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"VALOR RECEBIDO: R$ {valor_recibo:.2f}", ln=True, align='C', border=1)

    elif tipo == "CONTRATO":
        # INTEGRAÇÃO DO MODELO RESPEITOSO [cite: 3, 4, 5, 6]
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS", ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, f"CONTRATANTE: {dados_projeto['cliente']} | CPF/CNPJ: {dados_projeto.get('cpf_cnpj', '__________')}", ln=True)
        pdf.cell(0, 6, f"CONTRATADO: PJ Studio Design | {dados_empresa.get('email', '')} | WhatsApp: {dados_empresa.get('whatsapp', '')}", ln=True)
        
        pdf.ln(5)
        # Cláusulas do Modelo [cite: 7, 8, 9, 10, 15, 18]
        clausulas = [
            ("1. OBJETO", f"Prestação de serviços de design gráfico: {dados_projeto['nome_projeto']} ({dados_projeto['descricacao']})."),
            ("2. PRAZO", f"O prazo de entrega será de {dados_projeto.get('prazo', '__________')}, iniciando após confirmação da entrada."),
            ("3. VALOR E PAGAMENTO", f"Valor total de R$ {dados_projeto['valor_total']:.2f}, pago em 50% na contratação e 50% na entrega."),
            ("4. ALTERAÇÕES", "Inclui até 2 revisões simples. Alterações adicionais poderão ser cobradas."),
            ("5. DIREITOS DE USO", "Uso liberado após quitação total. O PJ Studio Design poderá utilizar o material em portfólio."),
            ("6. CANCELAMENTO", "Cancelamento após início do serviço não gera reembolso da entrada.")
        ]
        
        for titulo, desc in clausulas:
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 6, titulo, ln=True)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 5, desc)
            pdf.ln(2)

    # --- RODAPÉ DE ASSINATURAS E DATA ---
    pdf.ln(10)
    data_atual = datetime.now().strftime("%d/%m/%Y")
    pdf.cell(0, 10, f"Barra Mansa - RJ, {data_atual}", ln=True, align='L')
    
    pdf.ln(15)
    pdf.cell(90, 0, "", border='T')
    pdf.cell(10, 0, "", ln=False)
    pdf.cell(90, 0, "", border='T', ln=True)
    
    pdf.set_font("Arial", '', 9)
    pdf.cell(90, 5, "Assinatura do Contratante", ln=False, align='C')
    pdf.cell(10, 5, "", ln=False)
    pdf.cell(90, 5, "PJ Studio Design", ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')
