from app.repositories.lead_repository import create_lead
from app.validators.lead_validator import validate_lead


class DuplicateLeadError(Exception):
    """Заявка с таким номером уже существует."""


def submit_lead(payload: dict) -> str:
    """
    Проверяет и сохраняет заявку.

    Возвращает сообщение об успехе.
    Выбрасывает LeadValidationError при ошибке валидации.
    Выбрасывает DuplicateLeadError при дубликате.
    """
    lead = validate_lead(payload)

    saved = create_lead(lead)

    if not saved:
        raise DuplicateLeadError(
            "Мы уже получили заявку с этого номера. "
            "Скоро вам позвоним."
        )

    return "Спасибо! Ваша заявка отправлена."