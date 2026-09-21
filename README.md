# 📄 Leitor de Contratos em Python

Projeto desenvolvido em Python para auxiliar na análise de contratos em PDF, identificando automaticamente valores, formas de remuneração e condições de pagamento.

O objetivo é reduzir o tempo necessário para localizar informações financeiras em contratos extensos, utilizando análise contextual e regras de validação para evitar falsos positivos.

## 🚀 Funcionalidades

- Leitura automática de arquivos PDF
- Identificação de valores monetários
- Análise do contexto em que cada valor aparece
- Identificação de aluguel e remuneração mensal
- Detecção de cronogramas de pagamento
- Identificação de tabelas de preços
- Tratamento de valores unitários e valores totais
- Proteção contra falsos positivos, como multas, garantias, seguros e bônus
- Classificação do resultado por nível de confiança
- Indicação de revisão manual quando não há evidência suficiente
- Testes de regressão para validar alterações no código

## 🛠️ Tecnologias utilizadas

- Python
- PyMuPDF
- Expressões Regulares (Regex)

## 📁 Estrutura do projeto

```text
Leitor_Contratos/
├── leitor_contratos.py
├── teste_regressao.py
├── requirements.txt
├── README.md
└── .gitignore
```

Os contratos utilizados durante o desenvolvimento não são disponibilizados no repositório por conterem informações corporativas.

## ⚙️ Instalação

Clone o repositório e instale as dependências:

```bash
pip install -r requirements.txt
```

## ▶️ Como utilizar

Crie uma pasta chamada:

```text
contratos
```

Coloque os arquivos PDF que deseja analisar dentro dela.

Depois execute:

```bash
python leitor_contratos.py
```

O programa analisará os documentos e apresentará os valores e formas de remuneração encontrados.

## 🧪 Testes

O projeto possui testes de regressão utilizados durante o desenvolvimento para verificar se novas regras não alteram comportamentos já validados.

```bash
python teste_regressao.py
```

## ⚠️ Observação

O sistema utiliza regras heurísticas e análise contextual.

Resultados classificados como **REVISAR** devem passar por conferência manual. A ferramenta foi desenvolvida para auxiliar a análise documental, e não para substituir a validação humana.