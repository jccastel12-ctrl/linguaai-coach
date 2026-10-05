from httpx import AsyncClient

BASE = "/api/v1/translate"


async def test_translation_requires_authentication(client: AsyncClient) -> None:
    response = await client.post(
        BASE,
        json={"text": "Hola", "source_language": "es", "target_language": "en"},
    )
    assert response.status_code == 401


async def test_translate_spanish_to_english_demo_phrase(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.post(
        BASE,
        headers=auth_headers,
        json={"text": "Necesito ayuda", "source_language": "es", "target_language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["translated_text"] == "I need help"
    assert body["provider"] == "rule_based"
    assert body["source_language"] == "es"
    assert body["target_language"] == "en"


async def test_translate_english_to_serbian_demo_phrase(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.post(
        BASE,
        headers=auth_headers,
        json={"text": "Thank you", "source_language": "en", "target_language": "sr"},
    )
    assert response.status_code == 200
    assert response.json()["translated_text"] == "Hvala"


async def test_translate_name_pattern(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post(
        BASE,
        headers=auth_headers,
        json={"text": "Me llamo Ana", "source_language": "es", "target_language": "sr"},
    )
    assert response.status_code == 200
    assert response.json()["translated_text"] == "Zovem se Ana"


async def test_translation_rejects_same_language(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post(
        BASE,
        headers=auth_headers,
        json={"text": "Hola", "source_language": "es", "target_language": "es"},
    )
    assert response.status_code == 422


async def test_demo_provider_is_honest_about_unsupported_free_text(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.post(
        BASE,
        headers=auth_headers,
        json={
            "text": "Esta frase deliberadamente no está en el catálogo local de prueba",
            "source_language": "es",
            "target_language": "en",
        },
    )
    assert response.status_code == 422
    assert "AI_PROVIDER=openai_compatible" in response.json()["detail"]
