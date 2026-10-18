from dataclasses import dataclass


@dataclass(frozen=True)
class Lead:
    name: str
    phone: str
    phone_key: str
    interest: str
    comment: str

    ad_source: str

    utm_source: str
    utm_medium: str
    utm_campaign: str
    utm_content: str
    utm_term: str

    landing: str
    referrer: str