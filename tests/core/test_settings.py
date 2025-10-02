import pytest
from dynaconf import Dynaconf

from resync.core.exceptions import ConfigurationError
from resync.settings import validate_settings


@pytest.fixture
def base_config():
    """Provides a base configuration object with all required keys."""
    return Dynaconf(
        settings_files=[],
        NEO4J_URI="bolt://localhost:7687",
        NEO4J_USER="neo4j",
        NEO4J_PASSWORD="password",
        REDIS_URL="redis://localhost:6379",
        LLM_ENDPOINT="http://localhost:8001/v1",
        ADMIN_USERNAME="admin",
        ADMIN_PASSWORD="password",
        TWS_MOCK_MODE=True,  # TWS keys are not required by default
    )


def test_validate_settings_success(base_config):
    """
    Tests that validation passes when all required settings are present.
    """
    # This should not raise any exception
    validate_settings(base_config)


def test_validate_settings_fails_on_missing_key(base_config):
    """
    Tests that validation fails with a ConfigurationError if a key is missing.
    """
    del base_config.REDIS_URL  # Remove a required key

    with pytest.raises(ConfigurationError) as excinfo:
        validate_settings(base_config)

    assert "Missing or empty required settings: REDIS_URL" in str(excinfo.value)


def test_validate_settings_requires_tws_keys_when_not_mocked(base_config):
    """
    Tests that TWS-specific keys are required when TWS_MOCK_MODE is False.
    """
    base_config.TWS_MOCK_MODE = False  # TWS keys are now required

    with pytest.raises(ConfigurationError) as excinfo:
        validate_settings(base_config)

    # Check that all TWS keys are listed as missing
    assert "TWS_HOST" in str(excinfo.value)
    assert "TWS_PORT" in str(excinfo.value)
    assert "TWS_USER" in str(excinfo.value)
    assert "TWS_PASSWORD" in str(excinfo.value)


def test_validate_settings_fails_with_mocked_env(mocker):
    """
    Tests that validation fails when a required env var is mocked to be missing.
    """
    # We create a Dynaconf object that relies on an environment variable
    # We use mocker to simulate that this variable is not set.
    mocker.patch("dynaconf.base.LazySettings.get", return_value=None)

    config = Dynaconf(envvar_prefix="APP")

    with pytest.raises(ConfigurationError) as excinfo:
        validate_settings(config)

    # Check if one of the required keys is reported as missing
    assert "NEO4J_URI" in str(excinfo.value)