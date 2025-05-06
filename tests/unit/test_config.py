from keylin.config import Settings


def test_fallback_secrets(monkeypatch):
    monkeypatch.delenv("RESET_PASSWORD_SECRET", raising=False)
    monkeypatch.delenv("VERIFICATION_SECRET", raising=False)
    monkeypatch.setenv("JWT_SECRET", "fallback_jwt_secret")

    settings = Settings()

    assert settings.JWT_SECRET == "fallback_jwt_secret"
    assert settings.RESET_PASSWORD_SECRET == "supersecretresetkey"
    assert settings.VERIFICATION_SECRET == "supersecretverifykey"

def test_fallback_secrets_with_env_file_disabled(monkeypatch):
    # Simulate only JWT_SECRET being defined
    monkeypatch.setenv("JWT_SECRET", "only_jwt")
    monkeypatch.delenv("RESET_PASSWORD_SECRET", None)
    monkeypatch.delenv("VERIFICATION_SECRET", None)

    # Explicitly disable .env loading
    settings = Settings(_env_file=None)

    assert settings.JWT_SECRET == "only_jwt"
    assert settings.RESET_PASSWORD_SECRET == "only_jwt"
    assert settings.VERIFICATION_SECRET == "only_jwt"
