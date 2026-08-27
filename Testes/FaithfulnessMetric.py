import json
from pathlib import Path

from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from chatbot_config.chatbot import perguntar
from juiz import obter_juiz

JUIZ_MODEL = obter_juiz()

BASE_DIR = Path(__file__).parent
arquivo_dataset = BASE_DIR / "dataset" / "golden_dataset.json"
dataset = json.loads(arquivo_dataset.read_text(encoding="utf-8"))

for caso in dataset:
    resposta = perguntar(caso["input"])

    teste = LLMTestCase(
        input=caso["input"],
        actual_output=resposta,
        retrieval_context=caso.get("retrieval_context", []),
    )

    metrica = FaithfulnessMetric(
        threshold=0.8,
        model=JUIZ_MODEL,
        include_reason=True,
    )

    metrica.measure(teste)
    status = "PASSOU" if metrica.is_successful() else "FALHOU"
    print(f"{status} — Score: {metrica.score:.2f} (Threshold: {metrica.threshold})")
    print(f"Motivo do juiz: {metrica.reason}")