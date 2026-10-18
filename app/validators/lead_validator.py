import re

from app.models.lead import Lead


PHONE_PATTERN = re.compile(
    r"^(?:\+375|80)\s*\(?\d{2}\)?[\s-]*"
    r"\d{3}[\s-]*\d{2}[\s-]*\d{2}$"
)

PHONE_ERROR_MESSAGE = (
    "Введите белорусский номер, например "
    "+375 29 123-45-67."
)


class LeadValidationError(ValueError):
    """Ошибка проверки данных заявки."""


def _text(value: object, field_name: str, max_length: int) -> str:
    """Проверяет текстовое поле и ограничивает его длину."""
    if value is None:
        return ""

    if not isinstance(value, str):
        raise LeadValidationError(
            f"Поле «{field_name}» должно содержать текст."
        )

    value = value.strip()

    if len(value) > max_length:
        raise LeadValidationError(
            f"Поле «{field_name}» слишком длинное."
        )

    return value


def validate_lead(payload: dict) -> Lead:
    """Проверяет входные данные и создаёт модель Lead."""
    name = _text(payload.get("name"), "Имя", 100)
    phone = _text(payload.get("phone"), "Телефон", 30)
    interest = _text(payload.get("interest"), "Интерес", 100)
    comment = _text(payload.get("comment"), "Комментарий", 2000)

    if not name:
        raise LeadValidationError("Укажите ваше имя.")

    if not phone:
        raise LeadValidationError("Укажите номер телефона.")

    if not PHONE_PATTERN.fullmatch(phone):
        raise LeadValidationError(PHONE_ERROR_MESSAGE)

    if not interest:
        raise LeadValidationError("Выберите интересующий продукт.")

    digits = "".join(
        char for char in phone if char.isdigit()
    )

    phone_key = digits[-9:]

    # Поля, используемые для аналитики и определения источника заявки.
    source = _text(
        payload.get("source") or "direct_form",
        "Источник заявки",
        100,
    )

    return Lead(
        name=name,
        phone=phone,
        phone_key=phone_key,
        interest=interest,
        comment=comment,
        ad_source=source,
        utm_source=_text(payload.get("utm_source"), "utm_source", 200),
        utm_medium=_text(payload.get("utm_medium"), "utm_medium", 200),
        utm_campaign=_text(payload.get("utm_campaign"), "utm_campaign", 200),
        utm_content=_text(payload.get("utm_content"), "utm_content", 200),
        utm_term=_text(payload.get("utm_term"), "utm_term", 200),
        landing=_text(payload.get("landing"), "landing", 2000),
        referrer=_text(payload.get("referrer"), "referrer", 2000),
    )