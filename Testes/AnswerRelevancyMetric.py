from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

from chatbot_config.chatbot import perguntar
from juiz import obter_juiz

JUIZ_MODEL = obter_juiz()

DATA_SET = [
    {
        "input": "Tenho pele oleosa e preciso de hidratação. Qual produto você recomenda?",
        "actual_output": (
            "O chatbot deve recomendar um produto compatível "
            "com pele oleosa e com a necessidade de hidratação, "
            "seguindo a tabela de decisão."
        ),
        "retrieval_context": [
            "Gel Hidratante Oil-Free — indicado para pele oleosa — R$ 65,00"
        ]
    }
]

for caso in DATA_SET:

    resposta = perguntar(caso.get("input"))

    teste = LLMTestCase(
        input=caso.get("input"),
        actual_output=resposta,
        retrieval_context=caso.get("retrieval_context"),
    )

    metrica = AnswerRelevancyMetric(threshold=0.7, model=JUIZ_MODEL)

    metrica.measure(teste)

    status = "PASSOU" if metrica.is_successful() else "FALHOU"
    print(f"{status} — score: {metrica.score:.2f} (threshold 0.7)")
    print(f"Motivo do juiz: {metrica.reason}")

