from keylin.config import Settings


def test_fallback_secrets(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "supersecretresetkey")
    monkeypatch.setenv("RESET_PASSWORD_SECRET", "supersecretresetkey")
    monkeypatch.setenv("VERIFICATION_SECRET", "supersecretresetkey")

    settings = Settings()

    assert settings.JWT_SECRET == "supersecretresetkey"
    assert settings.RESET_PASSWORD_SECRET == "supersecretresetkey"
    assert settings.VERIFICATION_SECRET == "supersecretresetkey"

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
