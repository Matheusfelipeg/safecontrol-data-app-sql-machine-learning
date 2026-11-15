import pyodbc as db


dados_conexao = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-N760CU0\MSS_2025;"
    "Database=ControleEPI;"
    "Trusted_Connection=yes;"  
)

conexao = db.connect(dados_conexao)
print("Conexão bem-sucedida!")

cursor = conexao.cursor()
