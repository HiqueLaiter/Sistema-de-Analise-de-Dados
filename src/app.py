import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime
import plotly.express as px
from src import crud, database, analyzer, models 

# Garantindo que as tabelas existam no DB
models.Base.metadata.create_all(bind=database.engine) 

# --- FUNÇÃO CACHEADA DE LEITURA DE DADOS ---
@st.cache_data(ttl=600) # Cache os dados por 10 minutos (600s), a menos que seja invalidado
def fetch_data_to_df(_db_session: Session) -> pd.DataFrame:
    """Busca todas as transações e retorna um DataFrame. Esta função será cacheada."""
    return crud.get_transactions_dataframe(_db_session)

# Esta função apenas retorna a fábrica de sessões
@st.cache_resource
def get_db_session_factory():
    return database.SessionLocal

def main_app():
    st.set_page_config(
        page_title="Finanças Proativa", # Nome na aba do navegador
        page_icon="💸",                 # Ícone na aba 
        layout="wide"                   
    )
    
    # --- OBTÉM UMA NOVA SESSÃO DO BANCO A CADA RERUN ---
    db: Session = database.get_db()


    # --- BARRA LATERAL (MUDANÇA: TODA A LÓGICA AGORA ESTÁ AQUI DENTRO) ---
    st.sidebar.title("Menu de Operações")
    
    # Obtém categorias (AGORA FICA DENTRO DO main_app)
    categories = crud.get_categories(db)
    category_names = {c.name: c.id for c in categories}
    category_list = list(category_names.keys())

    # ==========================================
    # 1. IMPORTADOR DE CSV 
    # ==========================================
    st.sidebar.header("📂 Importar Dados (CSV)")
    uploaded_file = st.sidebar.file_uploader("Selecione seu arquivo CSV", type=["csv"])

    if uploaded_file is not None:
        if st.sidebar.button("Processar Importação"):
            try:
                csv_df = pd.read_csv(uploaded_file)
                required_cols = ['Date', 'Transaction Description', 'Category', 'Amount', 'Type']
                
                if not all(col in csv_df.columns for col in required_cols):
                    st.sidebar.error(f"O CSV precisa ter as colunas: {', '.join(required_cols)}")
                else:
                    count_new_cats = 0
                    count_trans = 0
                    processing_status = st.sidebar.empty()
                    processing_status.info("Processando... Por favor, aguarde.")

                    for index, row in csv_df.iterrows():
                        # A. TRATAMENTO DA CATEGORIA
                        cat_name = str(row['Category']).strip()
                        category_obj = crud.get_category_by_name(db, cat_name)
                        if not category_obj:
                            category_obj = crud.create_category(db, cat_name)
                            count_new_cats += 1
                        
                        # B. TRATAMENTO DO VALOR (Sinal Negativo/Positivo)
                        raw_amount = float(row['Amount'])
                        trans_type = str(row['Type']).strip().lower() 
                        
                        if 'expense' in trans_type: 
                            final_amount = -abs(raw_amount)
                        else:
                            final_amount = abs(raw_amount)

                        # C. TRATAMENTO DA DATA
                        trans_date = pd.to_datetime(row['Date']).to_pydatetime()
                        
                        # D. SALVAR NO BANCO
                        new_trans = models.TransactionCreate(
                            amount=final_amount,
                            description=str(row['Transaction Description']),
                            category_id=category_obj.id,
                            date=trans_date
                        )
                        crud.create_transaction(db, new_trans)
                        count_trans += 1
                        
                    processing_status.empty() 
                    st.sidebar.success(f"Sucesso! {count_trans} transações importadas.")
                    if count_new_cats > 0:
                        st.sidebar.info(f"{count_new_cats} novas categorias criadas.")
                    
                    # --- LIMPEZA DE CACHE APÓS INSERÇÃO ---
                    fetch_data_to_df.clear() # NOVO: Limpa o cache para que a próxima leitura seja fresca
                    st.rerun() 
                        
            except Exception as e:
                st.sidebar.error(f"Erro ao processar: Verifique formato do CSV e conexão. Erro: {e}")

    st.sidebar.markdown("---")
    
    # ==========================================
    # 2. FORMULÁRIO MANUAL 
    # ==========================================
    st.sidebar.header("➕ Nova Transação")
    
    with st.sidebar.form("new_transaction_form", clear_on_submit=True):
        if not category_list:
            st.warning("Nenhuma categoria encontrada. Crie uma padrão abaixo.")
            st.form_submit_button("Criar Categoria Padrão", on_click=lambda: crud.create_category(db, "Salário"))
        
        amount = st.number_input("Valor (Entrada (+), Saída (-))", value=0.0, step=10.0)
        description = st.text_input("Descrição da Transação")
        
        selected_category_name = st.selectbox("Categoria", category_list)
        category_id = category_names.get(selected_category_name)
        
        transaction_date = st.date_input("Data", value=datetime.now().date())
    
        submitted = st.form_submit_button("Salvar Transação")

        if submitted and category_id:
            try:
                # 1. Cria o objeto da transação
                new_transaction = models.TransactionCreate(
                    amount=amount,
                    description=description,
                    category_id=category_id,
                    date=datetime.combine(transaction_date, datetime.min.time())
                )
                
                # 2. Salva no Banco de Dados (Isso envia para o Azure SQL)
                crud.create_transaction(db, transaction=new_transaction)
                
                # 3. MENSAGEM DE SUCESSO
                st.success("Transação salva com sucesso! 🎉")

                # Limpa o cache da função que busca os dados. 
                # Isso obriga o Streamlit a ir no banco buscar TUDO de novo (antigos + novos)
                fetch_data_to_df.clear() 
                
                # Recarrega a página imediatamente para atualizar os gráficos
                st.rerun() 
                
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

    # --- INÍCIO DO DASHBOARD ---
    st.title("💸 Sistema de Análise Financeira")

    # 1. LEITURA E PREPARAÇÃO DE DADOS (USANDO A FUNÇÃO CACHEADA)
    # Garante que a função só é executada se o cache for limpo ou expirar
    try:
        # Troca para o underscore na chamada:
        df = fetch_data_to_df(db) # Corrigido para passar 'db' como '_db_session'
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}. Verifique a conexão com o PostgreSQL.")
        df = pd.DataFrame() 

    if df.empty:
        st.info("Nenhum dado encontrado. Use a barra lateral para adicionar dados.")
        return 
        
    balance_df = analyzer.calculate_monthly_balance(df)
    category_averages = analyzer.calculate_category_averages(df)
    insights = analyzer.generate_insights(df, category_averages)

    # ... (Métricas, Alertas, Gráficos e Tabela de Dados Brutos) ...
    
    # METRICAS CHAVE
    st.header("Métricas do Mês Atual")
    current_month_data = balance_df.iloc[-1] if not balance_df.empty else {'Income': 0, 'Expense': 0, 'Balance': 0}
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Total (Mês)", f"R$ {current_month_data['Balance']:.2f}")
    col2.metric("Total de Entradas", f"R$ {current_month_data['Income']:.2f}")
    col3.metric("Total de Saídas", f"R$ {current_month_data['Expense']:.2f}")
    st.markdown("---")
    
    # ALERTA E INSIGHTS
    st.header("Análise Proativa e Insights")
    if insights:
        for insight in insights:
            if "ALERTA" in insight["type"]:
                st.error(insight["message"]) 
            else:
                st.success(insight["message"]) 
    else:
        st.info("Nenhum alerta ou sucesso detectado neste mês. Os gastos estão na média.")
    st.markdown("---")

    # VISUALIZAÇÕES GRÁFICAS
    st.header("Visualizações Históricas")
    
    fig_balance = px.line(
        balance_df, 
        x=balance_df.apply(lambda row: f"{row['Year'].astype(int)}-{row['Month'].astype(int):02d}", axis=1), 
        y="Balance", 
        title="Evolução do Saldo Mensal",
        labels={'x': 'Mês', 'Balance': 'Saldo (R$)'}
    )
    st.plotly_chart(fig_balance, use_container_width=True)
    
    fig_pie = px.pie(
        df[df['amount'] < 0].groupby('category_name')['amount'].sum().abs().reset_index(), 
        values='amount', 
        names='category_name', 
        title='Distribuição de Despesas por Categoria'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # VISUALIZAÇÃO DE DADOS BRUTOS
    with st.expander("Ver Transações Recentes"):
        st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True)

# Chamada principal da aplicação
if __name__ == '__main__':
    main_app()