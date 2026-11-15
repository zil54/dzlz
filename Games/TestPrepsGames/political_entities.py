from dataclasses import dataclass


@dataclass(frozen=True)
class PoliticalEntityCapital:
    entity: str
    capital: str
    description: str


UK_CONSTITUENT_COUNTRY_CAPITALS = [
    PoliticalEntityCapital("England", "London", "UK constituent country"),
    PoliticalEntityCapital("Scotland", "Edinburgh", "UK constituent country"),
    PoliticalEntityCapital("Wales", "Cardiff", "UK constituent country"),
    PoliticalEntityCapital("Northern Ireland", "Belfast", "UK constituent country"),
]
