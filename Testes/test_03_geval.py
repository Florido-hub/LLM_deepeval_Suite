import json
from pathlib import Path
import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from chatbot_config.chatbot import perguntar
from juiz import obter_juiz

JUIZ_MODEL = obter_juiz()

BASE_DIR = Path(__file__).parent
dataset = ((BASE_DIR / "dataset" / "golden_dataset.json")
                   .read_text(encoding="utf-8"))

criteria_text = Path("dataset\\eval_criteria.txt").read_text(encoding="utf-8")

@pytest.mark.parametrize("caso", dataset, ids=[c.get("id", str(i)) for i, c in enumerate(dataset)])
def test_geval_claims(caso):
    resposta = perguntar(caso["input"])

    teste = LLMTestCase(
        input=caso["input"],
        actual_output=resposta
    )

    metrica_geval = GEval(
        name="Conformidade de Claims",
        criteria=caso["criterio_esperado"],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],
        threshold=0.8,
        model=JUIZ_MODEL
    )

    assert_test(test_case=teste, metrics=[metrica_geval])