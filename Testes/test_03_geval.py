import json
from pathlib import Path
import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from chatbot_config.chatbot import perguntar
from juiz import obter_juiz

JUIZ_MODEL = obter_juiz()

BASE_DIR = Path(__file__).resolve().parent

caminho_criteria = BASE_DIR / "dataset" / "geval_criteria.txt"
criteria_text = caminho_criteria.read_text(encoding="utf-8")

caminho_json = Path(__file__).resolve().parent / "dataset" / "golden_dataset.json"
dataset = json.loads(caminho_json.read_text(encoding="utf-8"))

@pytest.mark.parametrize("caso", dataset)
def test_geval_claims(caso):
    resposta = perguntar(caso["input"])

    teste = LLMTestCase(
        input=caso["input"],
        actual_output=resposta
    )

    metrica_geval = GEval(
        name="Conformidade de Claims",
        criteria=criteria_text,
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],
        threshold=0.8,
        model=JUIZ_MODEL
    )

    assert_test(test_case=teste, metrics=[metrica_geval])