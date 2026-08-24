from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.models import OllamaModel

JUIZ_MODEL = OllamaModel(
    model="llama3.1:latest",
    base_url="http://localhost:11434"
)

metric = FaithfulnessMetric(threshold=0.7, model=JUIZ_MODEL)


test_case = LLMTestCase(
    input="Qual a capital do Brasil?",
    actual_output="Brasilia",
    retrieval_context=["Atualmente é Brasilia a capital do Brasil"]
)

metric.measure(test_case)
print("SCORE:",metric.score)