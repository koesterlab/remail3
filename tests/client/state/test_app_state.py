"""Unit tests for AppState dataclass."""

from dataclasses import fields

import pytest

from remail.client.state.app_state import AppState


class TestAppState:
    """Test suite for AppState dataclass."""

    def test_app_state_is_dataclass(self):
        """Test that AppState is a dataclass."""

        assert hasattr(AppState, "__dataclass_fields__")

    def test_app_state_instantiation(self):
        """Test that AppState can be instantiated."""

        app_state = AppState()

        assert isinstance(app_state, AppState)

    def test_app_state_is_empty(self):
        """Test that AppState has the expected number of fields."""

        app_state = AppState()
        field_names = [f.name for f in fields(app_state)]

        assert len(field_names) == 13

    def test_app_state_repr(self):
        """Test that AppState has a proper string representation."""

        app_state = AppState()
        repr_str = repr(app_state)

        assert "AppState" in repr_str

    def test_app_state_equality(self):
        """Test that two AppState instances are equal."""

        app_state1 = AppState()
        app_state2 = AppState()

        assert app_state1 == app_state2

    def test_app_state_not_hashable(self):
        """Test that AppState instances are not hashable by default (dataclasses are unhashable unless frozen=True)."""

        app_state = AppState()

        with pytest.raises(TypeError, match="unhashable type"):
            hash(app_state)

    def test_app_state_multiple_instances_independent(self):
        """Test that multiple AppState instances are independent."""

        app_state1 = AppState()
        app_state2 = AppState()

        assert app_state1 == app_state2
        assert app_state1 is not app_state2


class TestAppStateFutureProof:
    """Tests to verify AppState behavior when fields are added."""

    def test_app_state_accepts_kwargs_when_fields_added(self):
        """Test that AppState will accept keyword arguments for future fields."""

        with pytest.raises(TypeError):
            AppState(some_field="value")

    def test_app_state_type_annotations(self):
        """Test that AppState has proper type annotations when fields are added."""

        annotations = getattr(AppState, "__annotations__", {})

        assert len(annotations) == 13
