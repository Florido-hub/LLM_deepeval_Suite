from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

from chatbot_config.chatbot import perguntar
from juiz import obter_juiz

JUIZ_MODEL = obter_juiz()

def test_exemplo_consulta_direta():
    pergunta = "Quanto custa o Sérum de Vitamina C 10% da Luma?"
    caso = LLMTestCase(
        input=pergunta,
        actual_output=perguntar(pergunta),
        retrieval_context=[
            "Sérum de Vitamina C 10% - Luma - R$119,90"
            "Ingredientes: vitamina C, ácido ferúlico, vinamina E"
        ],
    )
    metrica_a = AnswerRelevancyMetric(threshold=0.7, model=JUIZ_MODEL)
    assert_test(caso,[metrica_a])