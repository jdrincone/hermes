from enum import Enum

class QuestionType(Enum):
    CATEGORICAL = "categorical"
    NUMERICAL = "numerical"

class FormSection(Enum):
    QUALITY = "quality"
    PRODUCTION = "production"

# Configuration for questions based on user roles
QUESTIONS_CONFIG = {
    "admin": {
        FormSection.QUALITY: [
            {
                "id": "q1",
                "text": "¿Cuál es el estado general del producto?",
                "type": QuestionType.CATEGORICAL,
                "options": ["A - Excelente", "B - Bueno", "C - Regular"],
                "required": True
            },
            {
                "id": "q2",
                "text": "¿Cuál es el nivel de calidad del acabado?",
                "type": QuestionType.NUMERICAL,
                "min_value": 1,
                "max_value": 10,
                "required": True
            }
        ],
        FormSection.PRODUCTION: [
            {
                "id": "p1",
                "text": "¿Cuál es el estado de la línea de producción?",
                "type": QuestionType.CATEGORICAL,
                "options": ["A - Óptimo", "B - Normal", "C - Requiere atención"],
                "required": True
            },
            {
                "id": "p2",
                "text": "¿Cuál es la eficiencia de producción?",
                "type": QuestionType.NUMERICAL,
                "min_value": 0,
                "max_value": 100,
                "required": True
            }
        ]
    },
    "supervisor": {
        FormSection.QUALITY: [
            {
                "id": "q1",
                "text": "¿Cuál es el estado general del producto?",
                "type": QuestionType.CATEGORICAL,
                "options": ["A - Excelente", "B - Bueno", "C - Regular"],
                "required": True
            }
        ],
        FormSection.PRODUCTION: [
            {
                "id": "p1",
                "text": "¿Cuál es el estado de la línea de producción?",
                "type": QuestionType.CATEGORICAL,
                "options": ["A - Óptimo", "B - Normal", "C - Requiere atención"],
                "required": True
            }
        ]
    },
    "operator": {
        FormSection.QUALITY: [
            {
                "id": "q1",
                "text": "¿El producto cumple con los estándares básicos?",
                "type": QuestionType.CATEGORICAL,
                "options": ["A - Sí", "B - Parcialmente", "C - No"],
                "required": True
            }
        ],
        FormSection.PRODUCTION: [
            {
                "id": "p1",
                "text": "¿La línea está funcionando correctamente?",
                "type": QuestionType.CATEGORICAL,
                "options": ["A - Sí", "B - Parcialmente", "C - No"],
                "required": True
            }
        ]
    }
} 