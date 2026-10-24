"""Configuration: env vars and service profiles. No secrets in code."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceProfile:
    """The freelancer's constraints — the 'knowledge' in the reasoning loop."""
    services: tuple[str, ...]
    price_band_usd: tuple[int, int]
    red_flags: tuple[str, ...]
    preferred_niches: tuple[str, ...]


DEFAULT_PROFILE = ServiceProfile(
    services=("AI agents / automation", "websites", "SEO", "ad management"),
    price_band_usd=(1500, 12000),
    red_flags=("unpaid trial work", "equity-only pay", "no decision maker involved"),
    preferred_niches=("real estate", "hotels", "clinics", "restaurants", "law firms"),
)


@dataclass(frozen=True)
class Settings:
    zetaris_api_url: str = os.getenv("ZETARIS_API_URL", "")
    zetaris_id_token: str = os.getenv("ZETARIS_ID_TOKEN", "")
    zetaris_open_path: str = os.getenv("ZETARIS_OPEN_PATH", "")
    zetaris_page_path: str = os.getenv("ZETARIS_PAGE_PATH", "")
    zetaris_close_path: str = os.getenv("ZETARIS_CLOSE_PATH", "")
    zetaris_deals_table: str = os.getenv("ZETARIS_DEALS_TABLE", "deals")
    zetaris_prospects_table: str = os.getenv("ZETARIS_PROSPECTS_TABLE", "prospects")
    meterless_api_url: str = os.getenv("METERLESS_API_URL", "")
    meterless_api_key: str = os.getenv("METERLESS_API_KEY", "")
    meterless_planner_model: str = os.getenv("METERLESS_PLANNER_MODEL", "")
    meterless_fast_model: str = os.getenv("METERLESS_FAST_MODEL", "")
    jev_api_key: str = os.getenv("JEV_API_KEY", "")
    llm_provider: str = os.getenv("DEALREASONER_LLM", "local")  # local | nemotron
    escalate_below: float = float(os.getenv("DEALREASONER_ESCALATE_BELOW", "0.55"))

    @property
    def zetaris_configured(self) -> bool:
        return bool(self.zetaris_api_url and self.zetaris_id_token
                    and self.zetaris_open_path and self.zetaris_page_path
                    and self.zetaris_close_path)

    @property
    def nemotron_configured(self) -> bool:
        return bool(self.meterless_api_url and self.meterless_api_key
                    and self.meterless_planner_model)
