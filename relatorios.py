import pandas as pd
from weasyprint import HTML
from pypdf import PdfReader, PdfWriter
import io

def gerar_pdf_funcionarios(df):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{
                size: A4;
                margin: 50mm 20mm 20mm 20mm;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #333;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
            }}
            th, td {{
                border: 1px solid #444;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: rgba(220, 225, 230, 0.9);
            }}
        </style>
    </head>
    <body>
        {df.to_html(index=False)}
    </body>
    </html>
    """
    
    tabela_pdf_bytes = HTML(string=html).write_pdf()
    
    reader_tabela = PdfReader(io.BytesIO(tabela_pdf_bytes))
    writer = PdfWriter()
    
    for pagina_tabela in reader_tabela.pages:
        reader_fundo = PdfReader("Melhoras.pdf")
        pagina_fundo = reader_fundo.pages[0]
        
        pagina_fundo.merge_page(pagina_tabela)
        writer.add_page(pagina_fundo)
        
    saida = io.BytesIO()
    writer.write(saida)
    return saida.getvalue()

def gerar_pdf_entregas(df):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{
                size: A4 landscape; /* Aqui garantimos a folha deitada */
                margin: 15mm;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #333;
            }}
            .cabecalho {{
                text-align: center;
                padding-bottom: 10px;
                margin-bottom: 20px;
                border-bottom: 2px solid #2c3e50;
            }}
            .cabecalho h2 {{
                margin: 0;
                color: #2c3e50;
                text-transform: uppercase;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 11px; 
            }}
            th, td {{
                border: 1px solid #777;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #34495e;
                color: white; 
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="cabecalho">
            <h2>Relatório de Entregas -     Safe + Control</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Histórico completo de entregas registradas</p>
        </div>
        
        {df.to_html(index=False)}
        
    </body>
    </html>
    """
    
    return HTML(string=html).write_pdf()

def gerar_pdf_validade(df):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{
                size: A4 landscape;
                margin: 15mm;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #2c3e50;
            }}
            .cabecalho {{
                text-align: center;
                padding-bottom: 10px;
                margin-bottom: 20px;
                border-bottom: 2px solid #2c3e50; 
            }}
            .cabecalho h2 {{
                margin: 0;
                color: #2c3e50;
                text-transform: uppercase;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 11px; 
            }}
            th, td {{
                border: 1px solid #777;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #34495e; 
                color: white; 
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="cabecalho">
            <h2>Controle de Validade - Lotes de EPI</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Controle prazos e vencimentos (NR-06)</p>
        </div>
        
        {df.to_html(index=False)}
        
    </body>
    </html>
    """

    return HTML(string=html).write_pdf()

def gerar_pdf_previsao(df):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{
                size: A4 portrait; /* Retrato (em pé) já é suficiente aqui */
                margin: 15mm;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #2c3e50;
            }}
            .cabecalho {{
                text-align: center;
                padding-bottom: 10px;
                margin-bottom: 20px;
                border-bottom: 2px solid #2c3e50; /* Linha verde */
            }}
            .cabecalho h2 {{
                margin: 0;
                color: #2c3e50;
                text-transform: uppercase;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 11px; 
            }}
            th, td {{
                border: 1px solid #777;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #2c3e50; /* Verde combinando com o st.success */
                color: white; 
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="cabecalho">
            <h2>Cronograma de Substituição de EPIs</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Previsão de trocas para os próximos 180 dias</p>
        </div>
        
        {df.to_html(index=False)}
        
    </body>
    </html>
    """
    
    return HTML(string=html).write_pdf()