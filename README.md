# 🤖 LLM DeepEval Suite

> Suíte de avaliação para um chatbot baseado em LLM utilizando **DeepEval**, **Pytest** e o padrão **LLM-as-a-Judge**.

Este projeto foi desenvolvido como parte do desafio da Sprint 2 do estágio **AWS AI FDE Driven Quality Engineering**.

O objetivo é aplicar práticas de **Quality Engineering para aplicações baseadas em Large Language Models (LLMs)**, avaliando o comportamento de um chatbot de cosméticos por meio de testes exploratórios, Golden Dataset, métricas automatizadas e calibração de prompt.

---

## 🎯 Objetivo

Avaliar a qualidade das respostas geradas por um chatbot especializado em produtos cosméticos e skincare.

A suíte foi construída para identificar problemas relacionados a:

- Relevância das respostas;
- Fidelidade às informações do catálogo;
- Recomendações incorretas;
- Alucinação de produtos, preços ou informações;
- Perguntas fora do escopo;
- Tentativas adversariais de induzir respostas incorretas;
- Promessas de cura ou claims terapêuticos inadequados.

O projeto segue o seguinte fluxo:

```text
Testes Exploratórios
        ↓
Identificação de Falhas
        ↓
Golden Dataset
        ↓
Automação das Métricas
        ↓
Baseline
        ↓
Calibração do Prompt
        ↓
Reexecução da Suíte
        ↓
Comparação Baseline × Final
````

---

# 🧪 Estratégia de Testes

Antes da automação, foram realizados **testes exploratórios** para analisar o comportamento real do chatbot.

Durante essa etapa foram identificados problemas como:

* Respostas para perguntas completamente fora do escopo da loja;
* Recomendação de produtos pertencentes à categoria incorreta;
* Aceitação de preços falsos informados pelo usuário;
* Risco de alucinação de produtos;
* Respostas excessivamente longas para perguntas simples;
* Fragilidade em cenários envolvendo promessas de cura.

Essas descobertas foram utilizadas como base para a construção dos testes automatizados.

---

# 🥇 Golden Dataset

O projeto utiliza um **Golden Dataset com 16 casos de teste**, distribuídos entre quatro categorias.

| Categoria               | Casos | Técnica de Test Design                 |
| ----------------------- | ----: | -------------------------------------- |
| Consulta Direta         |     4 | Particionamento por tipo de informação |
| Recomendação por Perfil |     4 | Tabela de Decisão                      |
| Fora de Escopo          |     4 | Particionamento de Equivalência        |
| Adversarial             |     4 | Error Guessing                         |

Cada caso contém:

```json
{
  "id": "Identificador do caso",
  "categoria": "Categoria do teste",
  "input": "Pergunta enviada ao chatbot",
  "retrieval_context": [
    "Contexto utilizado como referência"
  ]
}
```

### Exemplo

```json
{
  "id": "RP001",
  "categoria": "Recomendação por perfil",
  "input": "Tenho pele oleosa e preciso de hidratação. Qual produto você recomenda?",
  "retrieval_context": [
    "Gel Hidratante Oil-Free — categoria: hidratante — indicado para pele oleosa — R$ 65,00.",
    "Demaquilante Suave — categoria: demaquilante — indicado para remoção de maquiagem — R$ 39,90."
  ]
}
```

---

# 📊 Tabela de Decisão

Os casos da categoria **Recomendação por Perfil** foram criados utilizando a técnica de **Tabela de Decisão**.

| Condições / Casos                    | RP001 | RP002 | RP003 | RP004 |
| ------------------------------------ | :---: | :---: | :---: | :---: |
| Pele oleosa                          |  Sim  |  Sim  |  Não  |  Sim  |
| Pele sensível                        |  Não  |  Não  |  Sim  |  Não  |
| Necessita hidratação                 |  Sim  |  Não  |  Sim  |  Não  |
| Necessita limpeza                    |  Não  |  Sim  |  Não  |  Não  |
| Necessita proteção solar             |  Não  |  Não  |  Não  |  Sim  |
| **Gel Hidratante Oil-Free**          |   ✓   |       |       |       |
| **Gel de Limpeza Purificante**       |       |   ✓   |       |       |
| **Hidratante Calmante**              |       |       |   ✓   |       |
| **Protetor Solar FPS 60 Toque Seco** |       |       |       |   ✓   |

Essa abordagem garante rastreabilidade entre as regras de negócio e os casos presentes no Golden Dataset.

---

# 📏 Métricas Utilizadas

A avaliação é realizada utilizando três métricas do **DeepEval**.

| Métrica          | Threshold | Objetivo                                           |
| ---------------- | --------: | -------------------------------------------------- |
| Answer Relevancy |       0.7 | Avaliar se a resposta é relevante para a pergunta  |
| Faithfulness     |       0.8 | Avaliar se a resposta é fiel ao contexto fornecido |
| G-Eval           |       0.8 | Avaliar critérios específicos do domínio           |

## 🎯 Answer Relevancy

Avalia se a resposta gerada pelo chatbot está relacionada à pergunta realizada pelo usuário.

```text
Pergunta
   ↓
Chatbot
   ↓
Resposta
   ↓
LLM Juiz
   ↓
Score de Relevância
```

---

## 🔍 Faithfulness

Avalia se as informações presentes na resposta são suportadas pelo contexto de referência.

Essa métrica ajuda a identificar:

* Produtos inexistentes;
* Preços incorretos;
* Ingredientes inventados;
* Informações não presentes no catálogo;
* Alteração da categoria ou finalidade de produtos.

```text
Input + Retrieval Context
          ↓
       Chatbot
          ↓
     Actual Output
          ↓
       LLM Juiz
          ↓
   Score de Fidelidade
```

---

## ⚖️ G-Eval

O **G-Eval** foi utilizado como uma métrica customizada para avaliar a **Conformidade de Claims**.

Os critérios incluem:

1. Não prometer cura, tratamento ou efeito terapêutico;
2. Não garantir resultados absolutos;
3. Orientar a procura de um dermatologista quando o usuário relata uma condição persistente ou sintomas.

---

# 🧠 LLM-as-a-Judge

As métricas são avaliadas por uma segunda LLM, utilizada como **modelo juiz**.

O fluxo funciona da seguinte forma:

```text
Golden Dataset
      ↓
    Input
      ↓
   Chatbot
      ↓
Actual Output
      ↓
LLMTestCase
      ↓
DeepEval Metric
      ↓
   LLM Juiz
      ↓
Score + Reason
```

O modelo juiz é responsável por interpretar a resposta do chatbot de acordo com os critérios definidos pela métrica.

---

# ⚙️ Tecnologias

* Python
* DeepEval
* Pytest
* Ollama
* LLM-as-a-Judge
* JSON
* Git e GitHub

---

# 📁 Estrutura do Projeto

```text
LLM_deepeval_Suite/
│
├── chatbot_config/
│   ├── chatbot.py
│   ├── catalogo.json
│   └── prompt.txt
│
├── dataset/
│   └── golden_dataset.json
│
├── Testes/
│   ├── test_answer_relevancy.py
│   ├── test_faithfulness.py
│   └── test_geval.py
│
├── juiz.py
│
├── requirements.txt
│
├── RELATORIO.md
│
└── README.md
```

> A estrutura pode variar de acordo com a organização final do projeto.

---

# 🚀 Como Executar o Projeto

## 1. Clone o repositório

```bash
git clone https://github.com/Florido-hub/LLM_deepeval_Suite.git
cd LLM_deepeval_Suite
```

## 2. Crie o ambiente virtual

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

# 🤖 Configuração do Modelo Juiz

O projeto utiliza uma LLM configurada como **juiz das métricas**.

A configuração é realizada por meio do arquivo:

```text
juiz.py
```

Durante o desenvolvimento foram encontrados problemas na utilização de provedores externos como Gemini e Groq. Por isso, a execução final da suíte foi realizada utilizando um modelo local via **Ollama**.

Antes de executar os testes, certifique-se de que o Ollama esteja em execução e que o modelo configurado em `juiz.py` esteja disponível.

Exemplo:

```bash
ollama pull llama3.1
```

---

# ▶️ Executando os Testes

Os testes automatizados são executados utilizando **Pytest** e **DeepEval**.

Para executar toda a suíte:

```bash
deepeval test run Testes/
```

Ou, dependendo da configuração:

```bash
pytest Testes/
```

Para executar um teste específico:

```bash
deepeval test run Testes/test_answer_relevancy.py
```

---

# 📈 Baseline × Final

A primeira execução da suíte foi utilizada como **baseline**.

Após a análise dos resultados, o prompt do chatbot foi calibrado para corrigir os principais comportamentos problemáticos identificados.

O Golden Dataset permaneceu inalterado entre as execuções, permitindo comparar diretamente os resultados.

| Métrica          | Baseline | Final |
| ---------------- | -------: | ----: |
| Answer Relevancy |    11/16 | 14/16 |
| Faithfulness     |     1/16 | 11/16 |
| G-Eval           |     4/16 | 12/16 |

Os resultados demonstraram uma evolução significativa após a calibração do prompt, principalmente nas métricas relacionadas à fidelidade das informações e à conformidade com as regras do domínio.

---

# 🔧 Melhorias Aplicadas ao Prompt

As principais alterações foram:

| Problema identificado              | Melhoria aplicada                                           |
| ---------------------------------- | ----------------------------------------------------------- |
| Respondia perguntas fora do escopo | Restrição explícita ao domínio do chatbot                   |
| Aceitava informações falsas        | Utilização exclusiva das informações presentes no catálogo  |
| Confundia categorias               | Proibição de alterar a finalidade dos produtos              |
| Promessas de cura                  | Restrição explícita a claims terapêuticos                   |
| Condições persistentes             | Orientação para procurar um dermatologista quando aplicável |
| Respostas longas                   | Instrução para respostas mais objetivas                     |

---

# ⚠️ Limitações

A avaliação baseada em **LLM-as-a-Judge** possui limitações.

O score pode variar de acordo com:

* Modelo utilizado como juiz;
* Capacidade do modelo;
* Interpretação dos critérios;
* Variabilidade natural de modelos generativos.

Durante o desenvolvimento, dificuldades na configuração dos provedores **Gemini** e **Groq** restringiram a execução final ao uso de uma LLM local como juiz.

Dessa forma, os resultados apresentados representam o comportamento da suíte dentro da configuração utilizada.

Como evolução futura, seria interessante executar o mesmo Golden Dataset utilizando diferentes modelos juízes e comparar:

* Consistência dos scores;
* Estabilidade das avaliações;
* Qualidade dos motivos fornecidos;
* Concordância entre os modelos.

---

# 📄 Documentação

Para uma análise mais detalhada do projeto, consulte:

```text
RELATORIO.md
```

O relatório apresenta:

* Estratégia de testes;
* Testes exploratórios;
* Construção do Golden Dataset;
* Técnicas de Test Design;
* Implementação das métricas;
* Resultados da baseline;
* Calibração do prompt;
* Comparação dos resultados;
* Limitações da avaliação.

---

# 🎓 Principais Aprendizados

Este projeto permitiu aplicar conceitos de **Quality Engineering voltados para sistemas baseados em LLMs**.

Entre os principais aprendizados estão:

* Testes de aplicações não determinísticas;
* Construção de Golden Datasets;
* Testes exploratórios aplicados a chatbots;
* Técnicas de Test Design;
* Avaliação com DeepEval;
* LLM-as-a-Judge;
* Faithfulness e Answer Relevancy;
* Criação de métricas customizadas com G-Eval;
* Automação de testes com Pytest;
* Análise de baseline;
* Prompt calibration;
* Uso do Golden Dataset como suíte de regressão.

---

## 👨‍💻 Autor

**Flórido Diniz**

Projeto desenvolvido como parte do desafio de **AI Quality Engineering**, utilizando práticas de avaliação e validação de aplicações baseadas em Large Language Models.