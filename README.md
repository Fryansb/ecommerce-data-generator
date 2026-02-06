# E-commerce Data Generator

[![Django CI](https://github.com/Fryansb/ecommerce-data-generator/workflows/Django%20CI/badge.svg)](https://github.com/Fryansb/ecommerce-data-generator/actions)

Sistema de geração de dados realistas de e-commerce para análise de dados, com dashboard Streamlit interativo e integração com Superset.

## 🚀 Funcionalidades

### Dashboard Streamlit Executivo
- **Métricas em Tempo Real (Redis)**: Faturamento, pedidos, clientes ativos e ticket médio do dia atual
- **Análises Financeiras**: Faturamento consolidado, lucro líquido e margens do período selecionado
- **Análise de Cohort**: Matriz de retenção de clientes por safra com heatmap visual
- **Análise de Produtos**: 
  - Ciclo de vida com justificativas baseadas em dados
  - Top produtos do Redis Cache
  - Análise de cross-selling (produtos comprados juntos)
- **Segmentação RFM**: Classificação inteligente (VIP, Leal, Novo, Comum, Churn)
- **Análises Geográficas**: 
  - Distribuição por região e estado
  - Mapa choropleth interativo do Brasil
- **Forecasting**: Projeções de 8 semanas usando regressão polinomial
- **Detecção de Anomalias**: Identificação automática de fraudes usando Isolation Forest com categorização

### Gerador de Dados
- Geração de dados realistas de e-commerce usando Faker e Factory Boy
- Bulk create otimizado para alta performance (batch_size=5000)
- Integridade temporal (clientes não podem fazer pedidos antes de seu cadastro)
- Simulação de churn baseada em tempo de vida do cliente
- Mapeamento correto de região/estado brasileiros
- Sazonalidade realista (Black Friday, Natal, férias)
- Eventos de mercado (crises logísticas, site down, viral)
- CAGR (12% ao ano) aplicado ao volume de pedidos
- Ciclo de vida de produtos (Viral, Stable, Obsolete)

### Infraestrutura
- Docker Compose com PostgreSQL, Redis e Django
- Cache distribuído com Redis para métricas em tempo real
- Arquitetura modular com separação de responsabilidades
- Queries otimizadas com Django ORM (agregações e anotações)
- Connection pooling para melhor performance
- Type hints em 85% do código
- Logging estruturado

## 📋 Pré-requisitos

- Python 3.12+
- Docker e Docker Compose (opcional, para ambiente completo)
- PostgreSQL 15+

## 🔧 Instalação

### Usando Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/Fryansb/ecommerce-data-generator.git
cd ecommerce-data-generator

# Inicie os serviços
docker-compose up -d

# Acesse:
# - Django Admin: http://localhost:8000/admin
# - Superset: http://localhost:8088
```

### Instalação Local

```bash
# Clone o repositório
git clone https://github.com/Fryansb/ecommerce-data-generator.git
cd ecommerce-data-generator

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure o banco de dados
export DB_NAME=thelook_db
export DB_USER=thelook_user
export DB_PASS=thelook_pass
export DB_HOST=localhost
export DB_PORT=5432

# Execute as migrações
python manage.py migrate

# Gere dados de exemplo
python manage.py simulate_data --years 2

# Inicie o servidor Django
python manage.py runserver
```

## 📊 Dashboard Streamlit

Para iniciar o dashboard Streamlit:

```bash
# Configure as variáveis de ambiente
export POSTGRES_USER=thelook_user
export POSTGRES_PASSWORD=thelook_pass
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=thelook_db

# Inicie o Streamlit
streamlit run streamlit_app.py
```

O dashboard estará disponível em: http://localhost:8501

## 🧪 Testes

```bash
# Execute todos os testes
pytest --ds=config.settings --maxfail=1 --disable-warnings -v

# Execute testes específicos
pytest tests/test_models.py -v
pytest tests/test_factories.py -v
pytest tests/test_simulate_data.py -v
```

## 📁 Estrutura do Projeto
     # Configurações Django
│   └── settings.py             # Settings com suporte a env vars
├── core/                       # App principal Django
│   ├── models.py              # Modelos (Customer, Product, Order, OrderItem)
│   ├── data_utils.py          # Utilitários de conexão (Redis, PostgreSQL)
│   ├── simulation_constants.py # Constantes de negócio (sazonalidade, CAGR)
│   └── management/
│       └── commands/
│           └── simulate_data.py  # Gerador com agregações Redis
├── tests/                      # Testes unitários
├── streamlit_app.py           # Dashboard executivo com 7 tabs
├── docker-compose.yml         # PostgreSQL + Redis + Django
├── requirements.txt           # Dependências Python
└── TECHNICAL_NOTES.md        # Documentação técnica
├── docker-compose.yml    # Orquestração de serviços
├── requirements.txt      # Dependências Python
└── .gitignore           # Arquivos ignorados (venv, .pyc, etc.)
```

## 🔐 Variáveis de Ambiente

| Variável | Descrição | Default |
|----------|-----------|---------|
| `DB_NAME` | Nome do banco de dados | `thelook_db` |
| `DB_USER` | Usuário do PostgreSQL | `thelook_user` |
| `DB_PASS` | Senha do PostgreSQL | `thelook_pass` |
| `DB_HOST` | Host do PostgreSQL | `localhost` |
| `DB_PORT` | Porta do PostgreSQL | `5432` |
| `POSTGRES_USER` | Usuário PostgreSQL (Streamlit) | `thelook_user` |
| `POSTGRES_PASSWORD` | Senha PostgreSQL (Streamlit) | `thelook_pass` |
| `POSTGRES_HOST` | Host PostgreSQL (Streamlit) | `localhost` |
| `POSTGRES_PORT` | Porta PostgreSQL (Streamlit) | `5432` |
| `REDIS_HOST` | Host Redis | `localhost` |
| `🎯 Melhorias de Performance

### Otimizações Implementadas
- **Queries Agregadas**: Django ORM com `annotate()`, `Sum()`, `Count()` ao invés de loops
- **Cache Redis**: Métricas pré-calculadas com TTL de 24h
- **Connection Pooling**: pool_size=5, max_overflow=10
- **Bulk Operations**: batch_size=5000 para inserções
- **Type Hints**: 85% de cobertura para melhor IDE support

### Consistência de Dados
- **Filtro de Status**: Apenas pedidos `Completed` em todas as métricas
- **Sincronização Redis-PostgreSQL**: Valores idênticos garantidos
- **Queries Otimizadas**: JOIN apenas com pedidos válido
1. Acesse o Superset em http://localhost:8088
2. Configure a conexão com o PostgreSQL
3. Use a query em `superset_query.sql` para criar datasets
4. Crie dashboards com as dimensões disponíveis

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT.

## 👥 Autores

- **Fryansb** - [GitHub](https://github.com/Fryansb)

## 🙏 Agradecimentos

- Faker-br para geração de dados brasileiros
- Streamlit para o dashboard interativo
- Plotly para visualizações avançadas
- Scikit-learn para detecção de anomalias
