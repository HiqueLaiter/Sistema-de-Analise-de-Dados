# 💸 Sistema de Análise Financeira Proativa

![Azure App Service](https://img.shields.io/badge/Azure-App%20Service-blue?logo=microsoftazure)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)

## 👥 Equipe
* **Henrique Pedrosa Laiter** — 22008543 — henrique.pl1@puccampinas.edu.br
* **Maria Eduarda Reis Machado** — 22001129 — maria.erm@puccampinas.edu.br

---

## 📝 Descrição Geral
O projeto de **Análise Financeira** tem como objetivo desenvolver um sistema em nuvem capaz de coletar, processar e analisar dados financeiros, identificando padrões de gastos e gerando alertas automáticos quando há despesas acima da média. 

Motivado pela dificuldade de muitas pessoas em controlar suas finanças de forma inteligente, o sistema utiliza uma **arquitetura _cloud-native_ baseada em containers Docker, hospedada no Microsoft Azure App Service (Linux) e com persistência de dados no Azure SQL Database**. A aplicação foi desenvolvida em **Python** utilizando o framework **Streamlit** para visualização interativa e **Pandas** para processamento de dados.

A solução propõe aplicar conceitos de **computação em nuvem, DevOps (CI/CD) e análise de dados** para transformar informações financeiras em *insights* práticos que auxiliem na tomada de decisões e no planejamento financeiro pessoal.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.11
* **Front-end & Análise:** Streamlit, Pandas, Plotly
* **Banco de Dados:** Azure SQL Database (PaaS)
* **Containerização:** Docker e Docker Hub
* **Infraestrutura em Nuvem:** Azure App Service (Web App for Containers)
* **Automação (CI/CD):** GitHub Actions
* **Conectividade:** Driver ODBC 17 para SQL Server

---

## 📊 DataSet
* **Fonte dos Dados:** [Personal Finance Data - Kaggle](https://www.kaggle.com/datasets/ramyapintchy/personal-finance-data)
* **Volume de Dados:** Arquivo CSV com cerca de 1500 registros de transações.
* **Estrutura:** O sistema processa colunas de `Date`, `Amount`, `Type` (Income/Expense) e `Category`.
* **Licenciamento:** Dataset aberto (disponibilizado pelo Kaggle).

---

## 🏗️ Arquitetura da Solução

A solução segue uma arquitetura PaaS (*Platform as a Service*) para garantir escalabilidade e facilidade de gestão.

<img width="1920" height="1080" alt="Arquitetura Cloud" src="https://github.com/user-attachments/assets/03153baf-b764-4ca3-9922-09bc68211e68" />

**Fluxo de Dados:**
1.  **Desenvolvimento:** O código é versionado no GitHub.
2.  **CI/CD:** O **GitHub Actions** dispara automaticamente ao receber um *push*, constrói a imagem Docker (instalando drivers ODBC) e a envia para o repositório público no **Docker Hub**.
3.  **Implantação:** O **Azure App Service** puxa a nova imagem do Docker Hub e atualiza a aplicação.
4.  **Execução:** A aplicação Python conecta-se ao **Azure SQL Database** para persistir transações e consultar históricos para gerar gráficos e alertas.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
* Docker e Docker Compose instalados.
* Git instalado.

### 1. Clonar o Repositório
```bash
git clone [https://github.com/SEU_USUARIO/SEU_REPO.git](https://github.com/HiqueLaiter/Sistema-de-Analise-de-Dados.git)
cd SEU_REPO
```

2.  Crie um arquivo `.env` na raiz com as credenciais do banco (ou use o padrão para testes locais):
    ```ini
    DB_HOST=nome-do-server
    DB_NAME=finance_db
    DB_USER=usuario
    DB_PASSWORD=senha
    ```

3.  Execute com Docker Compose:
    ```bash
    docker compose up --build
    ```

4.  Acesse o painel: `http://localhost:8501`

---

## 💻 Demonstração

> **Link da Aplicação em Produção:** [(https://app-fin-proa-final.azurewebsites.net/]

---

## 📚 Referências
* [Documentação do Streamlit](https://docs.streamlit.io/)
* [Microsoft Azure App Service](https://azure.microsoft.com/en-us/products/app-service/)
* [Docker Documentation](https://docs.docker.com/)
* [SQLAlchemy com Azure SQL](https://learn.microsoft.com/en-us/azure/azure-sql/database/connect-query-python)