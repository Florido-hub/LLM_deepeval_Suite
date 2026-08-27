import json
from pathlib import Path
import pytest
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from chatbot_config.chatbot import perguntar
from juiz import obter_juiz

JUIZ_MODEL = obter_juiz()

BASE_DIR = Path(__file__).parent
dataset = ((BASE_DIR / "dataset" / "golden_dataset.json")
                   .read_text(encoding="utf-8"))

@pytest.mark.parametrize("caso", dataset, ids=[c.get("id", str(i)) for i, c in enumerate(dataset)])
def test_faithfulness(caso):
    resposta = perguntar(caso["input"])

    teste = LLMTestCase(
        input=caso["input"],
        actual_output=resposta,
        retrieval_context=caso.get("retrieval_context", [])
    )
    metric = FaithfulnessMetric(
        threshold=0.8,
        model=JUIZ_MODEL
    )

    assert_test(test_case=teste, metrics=[metric])