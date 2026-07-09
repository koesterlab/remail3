"""Unit tests for SettingsDTO."""

from unittest.mock import Mock

from remail.controllers.dtos.settings_dto import SettingsDTO
from remail.enums import FontFamily, FontSize, Language, ThemeMode, Timezone


class TestSettingsDTO:
    """Test suite for SettingsDTO."""

    def test_create_dto_with_all_fields(self):
        """Test creating SettingsDTO with all fields."""
        dto = SettingsDTO(
            id=1,
            theme_mode=ThemeMode.DARK.value,
            font_size=FontSize.LARGE.value,
            font_family=FontFamily.ROBOTO.value,
            language=Language.GERMAN.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=True,
            email_notifications=False,
            quiet_hours=True,
        )

        assert dto.theme_mode == ThemeMode.DARK.value
        assert dto.font_size == FontSize.LARGE.value
        assert dto.font_family == FontFamily.ROBOTO.value
        assert dto.language == Language.GERMAN.value
        assert dto.timezone == Timezone.EUROPE_BERLIN.value
        assert dto.desktop_notifications is True
        assert dto.email_notifications is False
        assert dto.quiet_hours is True

    def test_from_model_creates_dto_from_settings_model(self):
        """Test that from_model creates DTO from Settings model."""
        mock_settings = Mock()
        mock_settings.id = 1
        mock_settings.theme_mode = ThemeMode.LIGHT.value
        mock_settings.font_size = FontSize.SMALL.value
        mock_settings.font_family = FontFamily.COURIER_NEW.value
        mock_settings.language = Language.FRENCH.value
        mock_settings.timezone = Timezone.EUROPE_BERLIN.value
        mock_settings.desktop_notifications = False
        mock_settings.email_notifications = True
        mock_settings.quiet_hours = False

        dto = SettingsDTO.from_model(mock_settings)

        assert isinstance(dto, SettingsDTO)
        assert dto.theme_mode == ThemeMode.LIGHT.value
        assert dto.font_size == FontSize.SMALL.value
        assert dto.font_family == FontFamily.COURIER_NEW.value
        assert dto.language == Language.FRENCH.value
        assert dto.timezone == Timezone.EUROPE_BERLIN.value
        assert dto.desktop_notifications is False
        assert dto.email_notifications is True
        assert dto.quiet_hours is False

    def test_to_dict_returns_dictionary(self):
        """Test that to_dict returns a dictionary with all fields."""
        dto = SettingsDTO(
            id=1,
            theme_mode=ThemeMode.SYSTEM.value,
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )

        result = dto.to_dict()

        assert isinstance(result, dict)
        assert result["theme_mode"] == ThemeMode.SYSTEM.value
        assert result["font_size"] == FontSize.MEDIUM.value
        assert result["font_family"] == FontFamily.ARIAL.value
        assert result["language"] == Language.ENGLISH.value
        assert result["timezone"] == Timezone.EUROPE_BERLIN.value
        assert result["desktop_notifications"] is True
        assert result["email_notifications"] is True
        assert result["quiet_hours"] is False

    def test_dto_attributes_accessible(self):
        """Test that SettingsDTO attributes are accessible."""
        dto = SettingsDTO(
            id=1,
            theme_mode=ThemeMode.DARK.value,
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )

        # All attributes should be accessible
        assert dto.id == 1
        assert dto.theme_mode == ThemeMode.DARK.value
        assert dto.font_size == FontSize.MEDIUM.value

    def test_from_model_with_default_values(self):
        """Test from_model with default enum values."""
        mock_settings = Mock()
        mock_settings.id = 1
        mock_settings.theme_mode = "system"
        mock_settings.font_size = "medium"
        mock_settings.font_family = "arial"
        mock_settings.language = "english"
        mock_settings.timezone = "Europe/London (UTC+00:00)"
        mock_settings.desktop_notifications = True
        mock_settings.email_notifications = True
        mock_settings.quiet_hours = False

        dto = SettingsDTO.from_model(mock_settings)

        assert dto.theme_mode == "system"
        assert dto.font_size == "medium"
        assert dto.font_family == "arial"
        assert dto.language == "english"
        assert dto.timezone == "Europe/London (UTC+00:00)"

    def test_dto_equality(self):
        """Test that two DTOs with same values are equal."""
        dto1 = SettingsDTO(
            id=1,
            theme_mode=ThemeMode.DARK.value,
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )

        dto2 = SettingsDTO(
            id=1,
            theme_mode=ThemeMode.DARK.value,
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )

        assert dto1 == dto2

    def test_dto_inequality(self):
        """Test that two DTOs with different values are not equal."""
        dto1 = SettingsDTO(
            id=1,
            theme_mode=ThemeMode.DARK.value,
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )

        dto2 = SettingsDTO(
            id=1,
            theme_mode=ThemeMode.LIGHT.value,  # Different
            font_size=FontSize.MEDIUM.value,
            font_family=FontFamily.ARIAL.value,
            language=Language.ENGLISH.value,
            timezone=Timezone.EUROPE_BERLIN.value,
            desktop_notifications=True,
            email_notifications=True,
            quiet_hours=False,
        )

        assert dto1 != dto2
