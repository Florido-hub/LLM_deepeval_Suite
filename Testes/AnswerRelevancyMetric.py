from pathlib import Path

from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

import json
from chatbot_config.chatbot import perguntar
from juiz import obter_juiz


BASE_DIR = Path(__file__).parent
dataset = json.loads(
    (BASE_DIR / "dataset\\golden_dataset.json")
    .read_text(encoding="utf-8")
)

JUIZ_MODEL = obter_juiz()

for caso in dataset:

    resposta = perguntar(caso["input"])

    teste = LLMTestCase(
        input=caso["input"],
        actual_output=resposta
    )

    metrica = AnswerRelevancyMetric(
        threshold=0.7,
        model=JUIZ_MODEL
    )

    metrica.measure(teste)

    status = "PASSOU" if metrica.is_successful() else "FALHOU"
    print(f"{status} — score: {metrica.score:.2f} (threshold 0.7)")
    print(f"Motivo do juiz: {metrica.reason}")