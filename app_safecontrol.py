import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import altair as alt # <-- Adicionado para o Gráfico da IA
from data import conexao
from relatorios import gerar_pdf_funcionarios, gerar_pdf_entregas, gerar_pdf_validade, gerar_pdf_previsao

# Imports do Machine Learning
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans

st.set_page_config(page_title="SafeControl · Gestão de EPI", layout="wide", page_icon="🛡️")

with st.sidebar:
    st.markdown("### 🛡️ SAFECONTROL")
    st.caption("MONITORAMENTO OPERACIONAL")
    st.markdown("---")
    
    menu = option_menu(
        menu_title=None,
        options=["Relatórios", "Cad. Funcionário", "Cad. EPI", "Reg. Entrega", "Reg. Compra", "Mapa de Risco (IA)"],
        icons=["file-earmark-text", "person-plus", "shield-check", "box-seam", "cart", "diagram-3"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#6b8caa", "font-size": "16px"},
            "nav-link": {
                "font-size": "15px", "text-align": "left", "margin": "0px", 
                "--hover-color": "#e3edf7", "color": "#6b8caa", "font-weight": "600"
            },
            "nav-link-selected": {
                "background-color": "#e3edf7", "color": "#1565c0", 
                "font-weight": "bold", "border-radius": "8px"
            },
        }
    )

if menu == "Relatórios":
    st.title("Central de Relatórios")
    st.caption("// EXPORTAÇÃO E ANÁLISE DE DADOS")
    
    def gerar_csv(df):
        return df.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')

    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.info("👥 **Funcionários Cadastrados**\n\nVisualizar listagem completa de funcionarios ativos")
            btn1, btn2 = st.columns(2)
            try:
                df_geral = pd.read_sql("SELECT IdFuncionario,Nome,CPF,Cargo,Setor,DataAdmissao FROM Funcionarios", conexao)
                with btn1:
                    st.download_button(label="📊 Relatório CSV", data=gerar_csv(df_geral), file_name="funcionarios_geral.csv", mime="text/csv", key="btn_func_csv", use_container_width=True)
                with btn2:
                    st.download_button(label="📥 Relatório PDF", data=gerar_pdf_funcionarios(df_geral), file_name="funcionarios.pdf", mime="application/pdf", key="btn_func_pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

        with st.container(border=True):
            st.warning("📦 **Controle de Entregas**\n\nRegistros de cautela e histórico")
            btn_ent1, btn_ent2 = st.columns(2)
            try:
                query_entregas = """
                    SELECT E.IdEntrega AS Protocolo, F.Nome AS Funcionario, F.Setor AS Setor, EPI.Nome AS Equipamento, EPI.CA AS CA, L.NumeroLote AS Lote, IE.Quantidade AS Qtd, E.DataEntrega AS Data_da_Entrega, E.Observacao AS Observacao
                    FROM Entregas E
                    JOIN Funcionarios F ON E.IdFuncionario = F.IdFuncionario
                    JOIN ItensEntrega IE ON E.IdEntrega = IE.IdEntrega
                    JOIN Lotes L ON IE.IdLote = L.IdLote
                    JOIN EPIs EPI ON L.IdEPI = EPI.IdEPI
                    ORDER BY E.DataEntrega DESC
                """
                df_entregas = pd.read_sql(query_entregas, conexao)
                with btn_ent1:
                    st.download_button(label="📊 Histórico Completo (CSV)", data=gerar_csv(df_entregas), file_name="entregas.csv", mime="text/csv", key="btn_ent_csv", use_container_width=True)
                with btn_ent2:
                    st.download_button(label="📥 Relatório PDF", data=gerar_pdf_entregas(df_entregas), file_name="entregas.pdf", mime="application/pdf", key="btn_ent_pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

    with col2:
        with st.container(border=True):
            st.success("📅 **Previsão de Trocas**\n\nPróximas entregas e substituições (180 dias)")
            btn_prev1, btn_prev2 = st.columns(2)
            try:
                query_previsao = """
                    WITH UltimaEntrega AS (
                        SELECT E.IdFuncionario, L.IdEPI, MAX(E.DataEntrega) AS UltimaData
                        FROM Entregas E
                        JOIN ItensEntrega IE ON E.IdEntrega = IE.IdEntrega
                        JOIN Lotes L ON IE.IdLote = L.IdLote
                        GROUP BY E.IdFuncionario, L.IdEPI
                    )
                    SELECT F.Nome AS Funcionario, F.Setor AS Setor, EPI.Nome AS Equipamento, CONVERT(VARCHAR(10), UE.UltimaData, 103) AS Ultima_Entrega, CONVERT(VARCHAR(10), DATEADD(MONTH, EPI.ValidadeMeses, UE.UltimaData), 103) AS Previsto_Para
                    FROM Funcionarios F
                    JOIN UltimaEntrega UE ON F.IdFuncionario = UE.IdFuncionario
                    JOIN EPIs EPI ON UE.IdEPI = EPI.IdEPI
                    WHERE F.Ativo = 1 
                      AND DATEADD(MONTH, EPI.ValidadeMeses, UE.UltimaData) BETWEEN GETDATE() AND DATEADD(DAY, 180, GETDATE())
                    ORDER BY DATEADD(MONTH, EPI.ValidadeMeses, UE.UltimaData) ASC
                """
                df_previsao = pd.read_sql(query_previsao, conexao)
                with btn_prev1:
                    st.download_button(label="📥 Baixar em CSV", data=gerar_csv(df_previsao), file_name="previsao.csv", mime="text/csv", key="btn_prev_csv", use_container_width=True)
                with btn_prev2:
                    st.download_button(label="📄 Baixar em PDF", data=gerar_pdf_previsao(df_previsao), file_name="previsao.pdf", mime="application/pdf", key="btn_prev_pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

        with st.container(border=True):
            st.error("⚠️ **Validade de EPIs e Lotes**\n\nAlertas de vencimento")
            btn_val1, btn_val2 = st.columns(2)
            try:
                query_validade = """
                    SELECT EPI.Nome AS Equipamento, EPI.CA AS CA, L.NumeroLote AS Lote, L.DataValidade AS Validade, L.QuantidadeAtual AS Qtd_Estoque,
                        CASE 
                            WHEN L.DataValidade < GETDATE() THEN 'Vencido'
                            WHEN L.DataValidade BETWEEN GETDATE() AND DATEADD(DAY, 30, GETDATE()) THEN 'Vence em 30 dias'
                            ELSE 'No Prazo'
                        END AS Status_Validade
                    FROM Lotes L
                    JOIN EPIs EPI ON L.IdEPI = EPI.IdEPI
                    ORDER BY L.DataValidade ASC
                """
                df_validade = pd.read_sql(query_validade, conexao)
                with btn_val1:
                    st.download_button(label="📥 Status dos Lotes", data=gerar_csv(df_validade), file_name="validade.csv", mime="text/csv", key="btn_val_csv", use_container_width=True)
                with btn_val2:
                    st.download_button(label="📄 Baixar em PDF", data=gerar_pdf_validade(df_validade), file_name="validade.pdf", mime="application/pdf", key="btn_val_pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

elif menu == "Cad. Funcionário": 
    st.title("Cadastro de Funcionários") 
    
    try:
        df_setores = pd.read_sql("SELECT IdSetor, Nome FROM Setores", conexao)
        opcoes_setores = dict(zip(df_setores['Nome'], df_setores['IdSetor']))
    except:
        st.error("Erro ao carregar setores.")
        opcoes_setores = {} 
    
    with st.form("form_func"): 
        col1, col2 = st.columns(2) 
        nome = st.text_input("Nome Completo") 
        cpf = st.text_input("CPF", max_chars=14) 
        cargo = col1.text_input("Cargo") 
        setor_escolhido = col2.selectbox("Setor", list(opcoes_setores.keys())) 
        data_admissao = st.date_input("Data de Admissão") 
         
        if st.form_submit_button("Cadastrar Usuário"): 
            if nome.strip() == "":
                st.warning("Nome Completo é obrigatório!")
            else:
                try:
                    cursor = conexao.cursor()
                    sql = "INSERT INTO Funcionarios (Nome, CPF, Cargo, Setor, IdSetor, DataAdmissao, Ativo) VALUES (?, ?, ?, ?, ?, ?, 1)"
                    cursor.execute(sql, (nome, cpf, cargo, setor_escolhido, opcoes_setores[setor_escolhido], data_admissao))
                    conexao.commit() 
                    st.success(f"Funcionário {nome} cadastrado com sucesso!")
                except Exception as erro:
                    st.error(f"Erro ao salvar: {erro}")
                finally:
                    if 'cursor' in locals(): cursor.close()

elif menu == "Cad. EPI":
    st.title("Cadastro de EPI")
    with st.form("form_epi"):
        nome_epi = st.text_input("Nome do EPI")
        col1, col2, col3 = st.columns(3)
        ca = col1.text_input("CA")
        validade = col2.number_input("Validade (Meses)", min_value=1)
        estoque = col3.number_input("Estoque Mínimo", min_value=0)
        
        if st.form_submit_button("Cadastrar Equipamento"):
            if nome_epi.strip() == "":
                st.warning("Nome do EPI é obrigatório!")
            else:
                try:
                    cursor = conexao.cursor()
                    sql = "INSERT INTO EPIs (Nome, CA, ValidadeMeses, EstoqueMinimo) VALUES (?, ?, ?, ?)"
                    cursor.execute(sql, (nome_epi, ca, validade, estoque))
                    conexao.commit()
                    st.success(f"EPI {nome_epi} salvo no banco com sucesso!")
                except Exception as erro:
                    st.error(f"Erro ao salvar: {erro}")
                finally:
                    if 'cursor' in locals(): cursor.close()

elif menu == "Reg. Entrega":
    st.title("Cadastrar Entrega")
    
    try:
        df_func = pd.read_sql("SELECT IdFuncionario, Nome FROM Funcionarios WHERE Ativo = 1", conexao)
        opcoes_func = dict(zip(df_func['Nome'], df_func['IdFuncionario']))
        
        df_lotes = pd.read_sql("SELECT L.IdLote, L.NumeroLote + ' - ' + E.Nome AS Descricao FROM Lotes L JOIN EPIs E ON L.IdEPI = E.IdEPI WHERE L.QuantidadeAtual > 0", conexao)
        opcoes_lotes = dict(zip(df_lotes['Descricao'], df_lotes['IdLote']))
    except:
        opcoes_func, opcoes_lotes = {}, {}
    
    with st.form("form_entrega"):
        col1, col2 = st.columns(2)
        func_escolhido = col1.selectbox("Funcionário", list(opcoes_func.keys()))
        lote_escolhido = col2.selectbox("Lote do EPI Disponível", list(opcoes_lotes.keys())) 
        
        col3, col4 = st.columns(2)
        qtd = col3.number_input("Quantidade", min_value=1, step=1)
        data_entrega = col4.date_input("Data da Entrega")
        obs = st.text_area("Observação")
        
        if st.form_submit_button("Registrar Entrega"):
            if not opcoes_func or not opcoes_lotes:
                st.warning("Cadastre funcionários e garanta que existam lotes em estoque antes de realizar entregas.")
            else:
                try:
                    func_id = opcoes_func[func_escolhido]
                    lote_id = opcoes_lotes[lote_escolhido]
                    
                    cursor = conexao.cursor()
                    cursor.execute("INSERT INTO Entregas (IdFuncionario, DataEntrega, Observacao) OUTPUT INSERTED.IdEntrega VALUES (?, ?, ?);", (func_id, data_entrega, obs))
                    id_entrega_gerado = cursor.fetchone()[0]
                    
                    cursor.execute("INSERT INTO ItensEntrega (IdEntrega, IdLote, Quantidade) VALUES (?, ?, ?);", (id_entrega_gerado, lote_id, qtd))
                    cursor.execute("UPDATE Lotes SET QuantidadeAtual = QuantidadeAtual - ? WHERE IdLote = ?;", (qtd, lote_id))
                    
                    conexao.commit()
                    st.success(f"Entrega {id_entrega_gerado} registrada com sucesso e estoque atualizado!")
                except Exception as erro:
                    conexao.rollback()
                    st.error(f"Erro ao registrar a entrega: {erro}")
                finally:
                    if 'cursor' in locals(): cursor.close()

elif menu == "Reg. Compra":
    st.title("Cadastrar Compra de Lote")
    
    try:
        df_epis = pd.read_sql("SELECT IdEPI, Nome FROM EPIs", conexao)
        opcoes_epis = dict(zip(df_epis['Nome'], df_epis['IdEPI']))
    except:
        opcoes_epis = {}

    with st.form("form_compra"):
        epi_escolhido = st.selectbox("EPI Comprado", list(opcoes_epis.keys()))
        
        col1, col2 = st.columns(2)
        lote = col1.text_input("Número do Lote")
        qtd = col2.number_input("Quantidade Comprada", min_value=1)
        
        col3, col4 = st.columns(2)
        data_fab = col3.date_input("Data de Fabricação")
        data_val = col4.date_input("Data de Vencimento")
        
        if st.form_submit_button("Confirmar Compra"):
            if lote.strip() == "":
                st.warning("O Número do Lote é obrigatório!")
            elif not opcoes_epis:
                st.warning("Cadastre um EPI antes de registrar uma compra.")
            else:
                try:
                    epi_id = opcoes_epis[epi_escolhido]
                    cursor = conexao.cursor()
                    sql = """
                    INSERT INTO Lotes (IdEPI, NumeroLote, DataFabricacao, DataValidade, QuantidadeInicial, QuantidadeAtual) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(sql, (epi_id, lote, data_fab, data_val, qtd, qtd))
                    conexao.commit()
                    st.success(f"Lote {lote} registrado com sucesso. Estoque atualizado!")
                except Exception as erro:
                    st.error(f"Erro ao salvar compra: {erro}")
                finally:
                    if 'cursor' in locals(): cursor.close()

elif menu == "Mapa de Risco (IA)":
    st.title("🧠 IA para RH: Análise de Desgaste e Consumo")
    st.write("O modelo mapeia o padrão de uso dos equipamentos na fábrica e identifica colaboradores que desgastam EPIs mais rápido que a média, permitindo antecipar trocas antes que o equipamento rasgue.")

    # 1. Simulação de Dados
    dados_rh = pd.DataFrame({
        'Funcionario': ['João Carlos', 'Maria Oliveira', 'Carlos Eduardo', 'Lucas Fernandes', 'Ana Paula', 'Pedro Henrique', 'Marcos Antônio', 'Julia Martins'],
        'Setor': ['Produção', 'Manutenção', 'Logística', 'Produção', 'Qualidade', 'Seg. Trabalho', 'Logística', 'Manutenção'],
        'EPI_Mais_Trocado': ['Luva Nitrílica', 'Óculos de Visão', 'Bota de PVC', 'Luva Nitrílica', 'Avental PVC', 'Bota de PVC', 'Bota de PVC', 'Luva de Malha'],
        'Fator_Desgaste': [1.0, 1.1, 1.8, 1.0, 1.0, 0.9, 1.7, 1.1], 
        'Dias_Atraso': [0, 1, 0, 0, 0, 0, 0, 2] 
    })

    # 2. Modelo K-Means
    X = dados_rh[['Fator_Desgaste', 'Dias_Atraso']]
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    dados_rh['Cluster'] = kmeans.fit_predict(X)

    # 3. Traduzindo a IA para o RH
    def classificar_perfil(linha):
        if linha['Fator_Desgaste'] > 1.5:
            return "⚠️ Desgaste Acelerado"
        elif linha['Dias_Atraso'] > 0:
            return "⏱️ Leve Atraso"
        else:
            return "✅ Uso Padrão"

    def gerar_sugestao(linha):
        if linha['Fator_Desgaste'] > 1.5:
            return f"Antecipar troca de {linha['EPI_Mais_Trocado']} no sistema"
        elif linha['Dias_Atraso'] > 0:
            return "Notificar via supervisor para retirada"
        else:
            return "Manter cronograma normal"

    dados_rh['Perfil'] = dados_rh.apply(classificar_perfil, axis=1)
    dados_rh['Ação Recomendada'] = dados_rh.apply(gerar_sugestao, axis=1)

    # 4. Painel de Indicadores Visuais
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    qtd_padrao = len(dados_rh[dados_rh['Perfil'] == "✅ Uso Padrão"])
    qtd_acelerado = len(dados_rh[dados_rh['Perfil'] == "⚠️ Desgaste Acelerado"])
    qtd_atraso = len(dados_rh[dados_rh['Perfil'] == "⏱️ Leve Atraso"])

    col1.metric("Uso Dentro do Padrão", f"{qtd_padrao} Colaboradores", "Operação Saudável", delta_color="normal")
    col2.metric("Desgaste Acelerado", f"{qtd_acelerado} Casos", "Requer antecipação", delta_color="inverse")
    col3.metric("Entregas Pendentes", f"{qtd_atraso} Casos", "Atrasos leves (1-2 dias)", delta_color="inverse")
    
    st.divider()

    # 6. Tabela focada só no que precisa de ação
    st.subheader("📋 Mapa de Ação do RH")
    
    # Filtra para não mostrar quem está com tudo OK na tabela de alertas
    df_problemas = dados_rh[dados_rh['Perfil'] != "✅ Uso Padrão"].copy()
    
    st.dataframe(
        df_problemas[['Funcionario', 'Setor', 'EPI_Mais_Trocado', 'Perfil', 'Ação Recomendada']], 
        use_container_width=True,
        hide_index=True
    )