[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Shared-Goals/SOSenki)

# Implementation Roadmap

Week 1-2: Foundation
✅ Run dead code analysis
✅ Remove identified dead files
✅ Set up coverage reporting
✅ Document all findings

Week 2-3: Localization
✅ Implement backend localization
✅ Add translation files
✅ Integrate with bot handlers
✅ Add language detection

Week 3-4: Testing
✅ Add seeding unit tests
✅ Add feature tests
✅ Achieve 80%+ coverage
✅ Add test documentation

Week 4-5: Design
✅ Install Figma MCP
✅ Generate design tokens
✅ Update CSS architecture
✅ Implement component system

Week 5-6: Refactoring
✅ Extract base services
✅ Consolidate duplicated code
✅ Improve error handling
✅ Update documentation

## Best Practices Checklist

Code Quality:

- Use ruff for consistent formatting
- Add type hints everywhere
- Document all public APIs
- Keep functions under 20 lines

Testing:

- Write tests first (TDD)
- Mock external dependencies
- Test edge cases
- Maintain 80%+ coverage

Localization:

- Use key-based translations
- Support RTL languages later
- Test with real users
- Keep translations in sync

Design System:

- Use CSS variables
- Follow 8px grid system
- Ensure accessibility (WCAG 2.1)
- Test on multiple devices

## Backend Localization Structure

```python
"""Localization module for SOSenki."""

from enum import Enum
from typing import Dict, Optional
import json
from pathlib import Path

class Language(Enum):
    EN = "en"
    RU = "ru"

class Localizer:
    """Centralized localization handler."""
    
    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files."""
        locale_dir = Path(__file__).parent / "locales"
        for lang in Language:
            file_path = locale_dir / f"{lang.value}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang.value] = json.load(f)
    
    def get(self, key: str, lang: Language = Language.EN, **kwargs) -> str:
        """Get localized string with optional formatting."""
        try:
            text = self.translations[lang.value][key]
            return text.format(**kwargs) if kwargs else text
        except KeyError:
            return f"[{key}]"  # Fallback to key if translation missing

# Global instance
localizer = Localizer()
```

```json
{
  "bot": {
    "welcome": "Добро пожаловать в SOSenki! 🏠",
    "request_sent": "Ваш запрос отправлен администраторам",
    "request_approved": "Ваш запрос одобрен ✅",
    "request_rejected": "Ваш запрос отклонен ❌",
    "open_mini_app": "Открыть приложение"
  },
  "mini_app": {
    "loading": "Загрузка...",
    "balance": "Баланс",
    "transactions": "Транзакции",
    "properties": "Недвижимость",
    "bills": "Счета",
    "back": "Назад",
    "admin_viewing_as": "Просмотр как: {user_name}",
    "no_data": "Нет данных",
    "access_denied": "Доступ запрещен",
    "request_access": "Запросить доступ"
  }
}
```

```json
{
  "bot": {
    "welcome": "Welcome to SOSenki! 🏠",
    "request_sent": "Your request has been sent to administrators",
    "request_approved": "Your request has been approved ✅",
    "request_rejected": "Your request has been rejected ❌",
    "open_mini_app": "Open Mini App"
  },
  "mini_app": {
    "loading": "Loading...",
    "balance": "Balance",
    "transactions": "Transactions",
    "properties": "Properties",
    "bills": "Bills",
    "back": "Back",
    "admin_viewing_as": "Viewing as: {user_name}",
    "no_data": "No data available",
    "access_denied": "Access denied",
    "request_access": "Request access"
  }
}
```

### Frontend Localization

```python
/**
 * Frontend internationalization module
 */

class I18n {
    constructor() {
        this.locale = this.detectLocale();
        this.translations = {};
        this.loadTranslations();
    }
    
    detectLocale() {
        // Get from Telegram WebApp or browser
        const tgLang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code;
        return (tgLang === 'ru') ? 'ru' : 'en';
    }
    
    async loadTranslations() {
        try {
            const response = await fetch(`/api/mini-app/translations/${this.locale}`);
            this.translations = await response.json();
        } catch (e) {
            console.error('Failed to load translations', e);
            // Fallback to English
            this.translations = await this.loadDefaultTranslations();
        }
    }
    
    t(key, params = {}) {
        const keys = key.split('.');
        let value = this.translations;
        
        for (const k of keys) {
            value = value?.[k];
        }
        
        if (!value) return `[${key}]`;
        
        // Replace parameters
        return value.replace(/{(\w+)}/g, (match, param) => 
            params[param] || match
        );
    }
}

// Global instance
window.i18n = new I18n();
```

## Tests

```python
"""Unit tests for database seeding functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from seeding.services.sheets_service import GoogleSheetsService
from seeding.services.seeding_service import SeedingService

class TestSeedingService:
    """Test suite for seeding service."""
    
    @pytest.fixture
    def mock_sheets_service(self):
        """Mock Google Sheets service."""
        service = Mock(spec=GoogleSheetsService)
        service.fetch_users.return_value = [
            {
                "name": "Test User",
                "telegram_id": "123456",
                "is_owner": True,
                "is_active": True
            }
        ]
        return service
    
    @pytest.fixture
    def seeding_service(self, mock_sheets_service, tmp_path):
        """Create seeding service with mocked dependencies."""
        with patch('seeding.services.seeding_service.SessionLocal'):
            service = SeedingService(
                sheets_service=mock_sheets_service,
                config_path=tmp_path / "config.json"
            )
            return service
    
    def test_seed_users_creates_new_users(self, seeding_service):
        """Test that new users are created from sheet data."""
        with patch.object(seeding_service, '_get_or_create_user') as mock_create:
            mock_create.return_value = (Mock(), True)  # (user, created)
            
            stats = seeding_service.seed_users()
            
            assert stats['created'] == 1
            assert stats['updated'] == 0
            mock_create.assert_called_once()
    
    def test_seed_idempotency(self, seeding_service):
        """Test that running seed twice produces same result."""
        # First run
        stats1 = seeding_service.seed_all()
        
        # Second run
        stats2 = seeding_service.seed_all()
        
        # Should update, not create on second run
        assert stats2['users']['created'] == 0
        assert stats2['users']['updated'] == stats1['users']['created']
    
    def test_rollback_on_error(self, seeding_service, mock_sheets_service):
        """Test that transaction rolls back on error."""
        mock_sheets_service.fetch_users.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            seeding_service.seed_users()
        
        # Verify rollback was called
        # Check that no data was committed
```

```python
"""Unit tests for admin user switching feature."""

import pytest
from unittest.mock import Mock, AsyncMock

from src.services.user_service import UserService

class TestAdminSwitching:
    """Test admin user context switching."""
    
    @pytest.fixture
    def admin_user(self):
        """Create admin user fixture."""
        user = Mock()
        user.id = 1
        user.is_administrator = True
        user.name = "Admin User"
        return user
    
    @pytest.fixture
    def target_user(self):
        """Create target user fixture."""
        user = Mock()
        user.id = 2
        user.is_owner = True
        user.name = "Target User"
        return user
    
    async def test_admin_can_switch_context(self, admin_user, target_user):
        """Test that admin can view as another user."""
        service = UserService()
        
        with patch.object(service, 'get_user_by_id') as mock_get:
            mock_get.return_value = target_user
            
            result = await service.resolve_target_user(
                authenticated_user=admin_user,
                selected_user_id=2
            )
            
            assert result == target_user
            mock_get.assert_called_with(2)
    
    async def test_non_admin_cannot_switch(self, target_user):
        """Test that non-admin cannot switch context."""
        non_admin = Mock()
        non_admin.is_administrator = False
        
        service = UserService()
        
        result = await service.resolve_target_user(
            authenticated_user=non_admin,
            selected_user_id=2
        )
        
        # Should return authenticated user, not target
        assert result == non_admin
```

## Figma Integration Setup

```json
{
  "figma": {
    "fileId": "YOUR_FIGMA_FILE_ID",
    "accessToken": "${FIGMA_ACCESS_TOKEN}",
    "components": {
      "mapping": {
        "Button": "src/static/mini_app/components/button.css",
        "Card": "src/static/mini_app/components/card.css",
        "Header": "src/static/mini_app/components/header.css"
      }
    },
    "colors": {
      "output": "src/static/mini_app/design-tokens.css"
    }
  }
}
```

### Design System Implementation

```css
/* Auto-generated from Figma - DO NOT EDIT MANUALLY */

:root {
  /* Telegram Design System Colors */
  --tg-theme-bg-color: var(--tg-theme-bg-color, #ffffff);
  --tg-theme-text-color: var(--tg-theme-text-color, #000000);
  --tg-theme-hint-color: var(--tg-theme-hint-color, #999999);
  --tg-theme-link-color: var(--tg-theme-link-color, #2481cc);
  --tg-theme-button-color: var(--tg-theme-button-color, #2481cc);
  --tg-theme-button-text-color: var(--tg-theme-button-text-color, #ffffff);
  
  /* Custom Theme Extensions */
  --nature-green: #4a7c59;
  --nature-brown: #8b4513;
  --nature-blue: #4682b4;
  
  /* Spacing Scale (8px base) */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  
  /* Typography Scale */
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
}
```

## Service Layer Refactoring

```python
"""Base service class with common patterns."""

from typing import TypeVar, Generic, Optional, List
from sqlalchemy.orm import Session
from src.models import Base

T = TypeVar('T', bound=Base)

class BaseService(Generic[T]):
    """Base service with CRUD operations."""
    
    def __init__(self, model: type[T], session: Session):
        self.model = model
        self.session = session
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        return self.session.query(self.model).filter(
            self.model.id == id
        ).first()
    
    def get_all(self, **filters) -> List[T]:
        """Get all entities with optional filters."""
        query = self.session.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.all()
    
    def create(self, **data) -> T:
        """Create new entity."""
        entity = self.model(**data)
        self.session.add(entity)
        self.session.commit()
        return entity
    
    def update(self, id: int, **data) -> Optional[T]:
        """Update entity."""
        entity = self.get_by_id(id)
        if entity:
            for key, value in data.items():
                setattr(entity, key, value)
            self.session.commit()
        return entity
```
