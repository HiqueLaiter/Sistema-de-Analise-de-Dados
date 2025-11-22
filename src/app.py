import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, date
import plotly.express as px

# Importando nossos módulos
from . import crud, database, analyzer, models 
# Garantindo que as tabelas existam no DB
models.Base.metadata.create_all(bind=database.engine) 

# --- Função de Conexão com DB (usa a função get_db de database.py) ---
@st.cache_resource
def get_db_session():
    """Cacheia a conexão com o banco de dados para reutilização."""
    return database.SessionLocal()


# --- 2. BARRA LATERAL (ENTRADA DE DADOS) ---
st.sidebar.title("➕ Adicionar Transação")

# Obtém categorias para o formulário
db: Session = database.get_db()
categories = crud.get_categories(db)
category_names = {c.name: c.id for c in categories}
category_list = list(category_names.keys())

# Form para nova transação
with st.sidebar.form("new_transaction_form", clear_on_submit=True):
    # Dica: Permite criar categorias padrões se o DB estiver vazio!
    if not category_list:
        st.warning("Nenhuma categoria encontrada. Crie algumas padrões (Ex: Salário, Moradia).")
        st.form_submit_button("Criar Categorias Padrões", on_click=lambda: crud.create_category(db, "Salário"))
    
    amount = st.number_input("Valor (Positivo para Entrada, Negativo para Saída)", value=0.0, step=10.0)
    description = st.text_input("Descrição da Transação")
    
    # Mapeia o nome da categoria selecionada para o ID
    selected_category_name = st.selectbox("Categoria", category_list)
    category_id = category_names.get(selected_category_name)
    
    transaction_date = st.date_input("Data", value=datetime.now())

    submitted = st.form_submit_button("Salvar Transação")

    if submitted and category_id:
        try:
            # Cria o objeto Pydantic para validação
            new_transaction = models.TransactionCreate(
                amount=amount,
                description=description,
                category_id=category_id,
                date=datetime.combine(transaction_date, datetime.min.time()) # Combina data/hora
            )
            # Chama a função CRUD
            crud.create_transaction(db, transaction=new_transaction)
            st.success("Transação salva com sucesso! 🎉")
            # Recarregar a página para atualizar o dashboard
            st.rerun() 
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")


def main_app():
    st.title("💸 Sistema de Análise Financeira Proativa")

    # --- 1. LEITURA E PREPARAÇÃO DE DADOS ---
    db: Session = database.get_db()
    
    # Puxa os dados como DataFrame
    try:
        df = crud.get_transactions_dataframe(db)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}. Verifique a conexão com o PostgreSQL.")
        df = pd.DataFrame() # Cria um DF vazio para evitar quebra

    if df.empty:
        st.info("Nenhum dado encontrado. Use a barra lateral para adicionar sua primeira transação.")
        return # Para a execução se não houver dados
        
    # --- 2. CÁLCULOS PRINCIPAIS ---
    
    # Obtém o DataFrame de saldo mensal
    balance_df = analyzer.calculate_monthly_balance(df)
    
    # Calcula as médias históricas para alertas
    category_averages = analyzer.calculate_category_averages(df)
    
    # Gera insights e alertas
    insights = analyzer.generate_insights(df, category_averages)

    # --- 3. METRICAS CHAVE (O ORGANIZADOR) ---
    st.header("Métricas do Mês Atual")
    
    # Encontra os totais do mês atual
    current_month_data = balance_df.iloc[-1] if not balance_df.empty else {'Income': 0, 'Expense': 0, 'Balance': 0}
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Total (Mês)", f"R$ {current_month_data['Balance']:.2f}")
    col2.metric("Total de Entradas", f"R$ {current_month_data['Income']:.2f}")
    col3.metric("Total de Saídas", f"R$ {current_month_data['Expense']:.2f}")
    
    st.markdown("---")
    
    # --- 4. ALERTA E INSIGHTS (O REQUISITO PROATIVO) ---
    st.header("Análise Proativa e Insights")
    
    if insights:
        for insight in insights:
            # Usa um expander para o alerta principal
            if "ALERTA" in insight["type"]:
                st.error(insight["message"]) # Alerta Vermelho
            else:
                st.success(insight["message"]) # Mensagem de Sucesso
    else:
        st.info("Nenhum alerta ou sucesso detectado neste mês. Os gastos estão na média.")
    
    st.markdown("---")

    # --- 5. VISUALIZAÇÕES GRÁFICAS (O REQUISITO VISUAL) ---
    st.header("Visualizações Históricas")
    
    # Gráfico 1: Saldo Mensal (Linha)
    fig_balance = px.line(
        balance_df, 
        x=balance_df.apply(lambda row: f"{row['Year']}-{row['Month']:02d}", axis=1), 
        y="Balance", 
        title="Evolução do Saldo Mensal",
        labels={'x': 'Mês', 'Balance': 'Saldo (R$)'}
    )
    st.plotly_chart(fig_balance, use_container_width=True)
    
    # Gráfico 2: Distribuição de Despesas por Categoria (Pizza)
    expense_categories = df[df['amount'] < 0].groupby('category_name')['amount'].sum().abs().reset_index()
    fig_pie = px.pie(
        expense_categories, 
        values='amount', 
        names='category_name', 
        title='Distribuição de Despesas por Categoria'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # --- 6. VISUALIZAÇÃO DE DADOS BRUTOS ---
    with st.expander("Ver Transações Recentes"):
        st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True)

# Chamada principal da aplicação
if __name__ == '__main__':
    main_app()