import pytest

from bloom_arc.observability import create_lemma_callback


def test_lemma_is_disabled_when_both_credentials_are_absent(monkeypatch) -> None:
    monkeypatch.delenv("LEMMA_API_KEY", raising=False)
    monkeypatch.delenv("LEMMA_PROJECT_ID", raising=False)

    assert create_lemma_callback() is None


def test_lemma_rejects_partial_configuration(monkeypatch) -> None:
    monkeypatch.setenv("LEMMA_API_KEY", "lma_test")
    monkeypatch.delenv("LEMMA_PROJECT_ID", raising=False)

    with pytest.raises(ValueError, match="LEMMA_PROJECT_ID"):
        create_lemma_callback()
