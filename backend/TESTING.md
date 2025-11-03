# Запуск тестов для 001-seamless-telegram-auth

Тесты написаны в **test-first** подходе (TDD): они FAIL до реализации.

## Быстрый старт

### 1. Установить зависимости через `uv`

```bash
cd SOSenki
uv sync --group dev
```

Если `uv` не установлен, установите его:

```bash
brew install uv
```

### 2. Запустить контрактные тесты (должны FAIL)

```bash
uv run --group dev python -m pytest backend/tests/contract/test_miniapp_auth_contract.py -v
```

Ожидаемый результат: все тесты **FAIL** с `pytest.fail()` — это нормально и желательно в test-first.

### 3. Запустить модульные тесты (должны FAIL)

```bash
uv run --group dev python -m pytest backend/tests/unit/test_initdata_validation.py -v
```

Ожидаемый результат: все тесты **FAIL** с `pytest.fail()`.

### 4. Запустить все тесты

```bash
uv run --group dev python -m pytest backend/tests/ -v
```

## Структура тестов

```text
backend/
├── tests/
│   ├── conftest.py              # Fixtures (test_telegram_id, test_init_data)
│   ├── contract/
│   │   └── test_miniapp_auth_contract.py   # Контрактные тесты для /miniapp/auth
│   ├── unit/
│   │   └── test_initdata_validation.py     # Модульные тесты для валидации initData
│   └── integration/             # (Будут добавлены для integration test-first)
└── app/                         # (Реализация будет добавлена после тестов)
```

## Описание тестов

### Контрактные тесты (`test_miniapp_auth_contract.py`)

Проверяют соответствие endpoint'а OpenAPI контракту:

- `test_miniapp_auth_endpoint_exists` — endpoint `POST /miniapp/auth` существует и отвечает 200/401
- `test_miniapp_auth_linked_user_response_schema` — связанный пользователь получает `linked: true`
- `test_miniapp_auth_unlinked_user_response_schema` — несвязанный пользователь получает форму запроса
- `test_miniapp_auth_invalid_initdata_returns_401` — невалидные данные возвращают 401

### Модульные тесты (`test_initdata_validation.py`)

Проверяют криптографическую верификацию initData:

- `test_verify_initdata_signature_valid` — корректная HMAC-SHA256 подпись проходит
- `test_verify_initdata_signature_invalid` — поддельная подпись отклоняется
- `test_initdata_timestamp_fresh` — свежий timestamp (< 120 сек) принимается
- `test_initdata_timestamp_expired` — старый timestamp отклоняется
- `test_extract_telegram_id_from_valid_initdata` — Telegram ID корректно извлекается
- `test_initdata_missing_required_fields` — отсутствие полей отклоняется

## Следующие шаги (для /specify.implement)

После того как тесты созданы и FAIL, разработчик может запустить:

```bash
/specify.implement
```

`/specify.implement` должен:

1. Прочитать контрактные тесты
2. Создать заглушки маршрутов/сервисов (`backend/app/services/telegram_auth_service.py`, `backend/app/api/routes/miniapp.py`)
3. Постепенно реализовать логику для прохождения тестов

## Запуск в CI

Добавьте в `.github/workflows/`:

```yaml
- name: Install dependencies
  run: |
    uv sync --group dev

- name: Run tests
  run: |
    uv run --group dev python -m pytest backend/tests/ -v --tb=short
```

## Конфигурация pytest

Параметры в `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["backend/tests"]
markers = [
    "unit: unit tests (fast, no I/O)",
    "contract: contract/API tests",
    "integration: integration tests (slow, with I/O)",
]
```

Запуск по категориям:

```bash
uv run --group dev python -m pytest -m unit          # Только unit тесты
uv run --group dev python -m pytest -m contract      # Только контрактные тесты
uv run --group dev python -m pytest -m integration   # Только интеграционные тесты
```
