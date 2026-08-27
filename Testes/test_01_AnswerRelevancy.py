import json
from pathlib import Path
import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

from chatbot_config.chatbot import perguntar
from juiz import obter_juiz

JUIZ_MODEL = obter_juiz()

caminho_json = Path(__file__).resolve().parent / "dataset" / "golden_dataset.json"
dataset = json.loads(caminho_json.read_text(encoding="utf-8"))

@pytest.mark.parametrize("caso", dataset)
def test_answer_relevancy(caso):
    resposta = perguntar(caso["input"])

    teste = LLMTestCase(
        input=caso["input"],
        actual_output=resposta
    )

    metric = AnswerRelevancyMetric(
        threshold=0.7,
        model=JUIZ_MODEL,
        include_reason=True
    )

    assert_test(test_case=teste, metrics=[metric])