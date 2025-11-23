import pandas as pd
from typing import Dict, Any, List
from datetime import datetime

def calculate_monthly_balance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula o saldo (Entradas e Saídas) agrupado por Mês/Ano.
    
    Args:
        df: DataFrame de transações com colunas 'date' e 'amount'.
        
    Returns:
        DataFrame com colunas 'Year', 'Month', 'Income' (Entradas), 
        'Expense' (Saídas) e 'Balance' (Saldo).
    """
    # 1. Cria colunas de tempo
    df['Year'] = df['date'].dt.year
    df['Month'] = df['date'].dt.month
    
    # 2. Divide em Entradas (amount > 0) e Saídas (amount < 0)
    income_df = df[df['amount'] > 0]
    expense_df = df[df['amount'] < 0]
    
    # 3. Agrupa as Entradas por mês/ano
    monthly_income = income_df.groupby(['Year', 'Month'])['amount'].sum().reset_index()
    monthly_income.rename(columns={'amount': 'Income'}, inplace=True)
    
    # 4. Agrupa as Saídas (usamos o valor absoluto para facilitar a exibição)
    monthly_expense = expense_df.groupby(['Year', 'Month'])['amount'].sum().reset_index()
    monthly_expense['amount'] = monthly_expense['amount'].abs() # Valor positivo para Despesa
    monthly_expense.rename(columns={'amount': 'Expense'}, inplace=True)
    
    # 5. Combina as tabelas
    balance_df = pd.merge(monthly_income, monthly_expense, on=['Year', 'Month'], how='outer').fillna(0)
    
    # 6. Calcula o Saldo
    balance_df['Balance'] = balance_df['Income'] - balance_df['Expense']
    
    return balance_df.sort_values(['Year', 'Month'])


def calculate_category_averages(df: pd.DataFrame, months_to_compare: int = 3) -> Dict[str, Any]:
    """
    Calcula a média de gastos por categoria nos últimos N meses para fins de alerta.
    
    Args:
        df: DataFrame de transações.
        months_to_compare: Número de meses para calcular a média histórica.
        
    Returns:
        Um dicionário mapeando o nome da categoria para sua média de gasto mensal.
    """
    
    # 1. Foca apenas nas despesas (amount < 0) e usa o valor absoluto
    expense_df = df[df['amount'] < 0].copy()
    expense_df['amount'] = expense_df['amount'].abs()
    
    # 2. Define o limite de tempo para a média (exclui o mês atual)
    today = datetime.now()
    # Define o início do mês anterior
    end_date_avg = today.replace(day=1) - pd.Timedelta(days=1) 
    
    # Se não houver dados suficientes, ajusta a data de início
    if not expense_df.empty:
        start_date_avg = end_date_avg - pd.DateOffset(months=months_to_compare)
        
        # 3. Filtra os dados históricos para o cálculo da média
        historical_df = expense_df[
            (expense_df['date'] >= start_date_avg) & (expense_df['date'] <= end_date_avg)
        ]
        
        # 4. Agrupa por mês/ano e categoria
        monthly_category_expense = historical_df.groupby([
            historical_df['date'].dt.to_period('M'), 'category_name'
        ])['amount'].sum().reset_index()
        
        # 5. Calcula a média mensal de gasto por categoria no período
        category_averages = monthly_category_expense.groupby('category_name')['amount'].mean().to_dict()
        
        return category_averages

    return {} # Retorna vazio se o DataFrame estiver vazio

def generate_insights(df: pd.DataFrame, category_averages: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Gera insights e alertas para o mês atual.
    
    Args:
        df: DataFrame de transações.
        category_averages: Médias históricas calculadas.
    """
    insights = []
    
    # Filtra os dados do mês atual
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_df = df[df['date'] >= current_month_start]
    
    # Total de gasto por categoria no mês atual
    current_expenses = current_month_df[current_month_df['amount'] < 0]
    current_expenses['amount'] = current_expenses['amount'].abs()
    current_totals = current_expenses.groupby('category_name')['amount'].sum().to_dict()
    
    for category, current_total in current_totals.items():
        historical_avg = category_averages.get(category)
        
        if historical_avg is not None and historical_avg > 0:
            if current_total > historical_avg * 1.20: # Alerta se 20% acima da média
                diff_percent = (current_total / historical_avg - 1) * 100
                insights.append({
                    "type": "ALERTA 🚨",
                    "message": f"Seu gasto em **{category}** ({current_total:.2f}) está **{diff_percent:.0f}% ACIMA** da média histórica ({historical_avg:.2f}). Atenção!"
                })
            elif current_total < historical_avg * 0.80:
                 diff_percent = (1 - current_total / historical_avg) * 100
                 insights.append({
                    "type": "SUCESSO 🎉",
                    "message": f"Parabéns! Seu gasto em **{category}** ({current_total:.2f}) está **{diff_percent:.0f}% ABAIXO** da média histórica. Continue assim!"
                })
        
    return insights


