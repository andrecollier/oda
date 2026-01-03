"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Kassal.app API
    kassal_api_key: str = Field(..., env="KASSAL_API_KEY")
    kassal_base_url: str = Field(
        default="https://kassal.app/api/v1", env="KASSAL_BASE_URL"
    )

    # Oda.no credentials
    oda_email: str = Field(..., env="ODA_EMAIL")
    oda_password: str = Field(..., env="ODA_PASSWORD")

    # Browser settings
    headless_browser: bool = Field(default=False, env="HEADLESS_BROWSER")

    # Database
    database_url: str = Field(
        default="sqlite:///./data/meal_planner.db", env="DATABASE_URL"
    )

    # Meal planning preferences
    default_meal_days: int = Field(default=5, env="DEFAULT_MEAL_DAYS")
    protein_goal_per_meal: float = Field(default=30.0, env="PROTEIN_GOAL_PER_MEAL")
    child_friendly_mode: bool = Field(default=True, env="CHILD_FRIENDLY_MODE")
    meal_prep_mode: bool = Field(default=True, env="MEAL_PREP_MODE")

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
