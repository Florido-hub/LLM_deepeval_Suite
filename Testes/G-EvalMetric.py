import json
from pathlib import Path

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from chatbot_config.chatbot import perguntar
from juiz import obter_juiz

JUIZ_MODEL = obter_juiz()

BASE_DIR = Path(__file__).parent
dataset = json.loads(
    (BASE_DIR / "dataset\\golden_dataset.json")
    .read_text(encoding="utf-8")
)

for caso in dataset:
    resposta = perguntar(caso["input"])

    teste = LLMTestCase(input=caso["input"], actual_output=resposta)
    metrica = GEval(
        name="Conformidade de Claims",
        criteria=caso["criterio_esperado"],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],
        threshold=0.8,
        model=JUIZ_MODEL,
    )
    metrica.measure(teste)
    status = "PASSOU" if metrica.is_successful() else "FALHOU"
    print(f"\n{status} — score: {metrica.score:.2f} (threshold 0.8)")
    print(f"Motivo do juiz: {metrica.reason}")