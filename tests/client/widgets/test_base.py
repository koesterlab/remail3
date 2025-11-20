"""Unit tests for RemailComponent base class."""

from abc import ABC

import flet as ft
import pytest

from remail.client.widgets.base import RemailComponent


class TestRemailComponent:
    """Test suite for RemailComponent abstract base class."""

    def test_remail_component_is_abstract(self):
        """Test that RemailComponent is an abstract base class."""

        assert issubclass(RemailComponent, ABC)

    def test_remail_component_inherits_from_control(self):
        """Test that RemailComponent inherits from ft.Control."""

        assert issubclass(RemailComponent, ft.Control)

    def test_cannot_instantiate_remail_component_directly(self):
        """Test that RemailComponent cannot be instantiated directly."""

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            RemailComponent()

    def test_build_method_is_abstract(self):
        """Test that build method is abstract."""

        assert "build" in RemailComponent.__abstractmethods__


class ConcreteComponent(RemailComponent):
    """Concrete implementation of RemailComponent for testing."""

    def build(self) -> ft.Control:
        return ft.Text("Test Component")


class TestConcreteRemailComponent:
    """Test suite for concrete implementations of RemailComponent."""

    def test_concrete_component_can_be_instantiated(self):
        """Test that a concrete implementation can be instantiated."""

        component = ConcreteComponent()

        assert isinstance(component, RemailComponent)
        assert isinstance(component, ft.Control)

    def test_concrete_component_build_returns_control(self):
        """Test that build method returns a Control."""

        component = ConcreteComponent()
        result = component.build()

        assert isinstance(result, ft.Control)

    def test_concrete_component_is_control(self):
        """Test that concrete component has Control functionality."""

        component = ConcreteComponent()

        assert hasattr(component, "visible")
        assert hasattr(component, "disabled")


class IncompleteComponent(RemailComponent):
    """Incomplete implementation missing build method."""

    pass


class TestIncompleteRemailComponent:
    """Test suite for incomplete implementations."""

    def test_incomplete_component_cannot_be_instantiated(self):
        """Test that implementation without build method cannot be instantiated."""

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteComponent()


class ComponentWithWrongBuildSignature(RemailComponent):
    """Implementation with incorrect build signature."""

    def build(self):
        return ft.Text("Wrong Signature")


class TestComponentBuildSignature:
    """Test suite for build method signature requirements."""

    def test_component_with_wrong_signature_still_instantiates(self):
        """Test that wrong signature still allows instantiation (Python doesn't enforce return types at runtime)."""

        component = ComponentWithWrongBuildSignature()

        assert isinstance(component, RemailComponent)


class MultipleControlComponent(RemailComponent):
    """Component that builds a container with multiple controls."""

    def build(self) -> ft.Control:
        return ft.Column(
            controls=[
                ft.Text("Header"),
                ft.Text("Content"),
                ft.Text("Footer"),
            ]
        )


class TestComplexRemailComponent:
    """Test suite for more complex component implementations."""

    def test_component_can_return_container(self):
        """Test that build can return a container with multiple controls."""

        component = MultipleControlComponent()
        result = component.build()

        assert isinstance(result, ft.Column)
        assert len(result.controls) == 3

    def test_component_controls_are_text_widgets(self):
        """Test that the container contains the expected controls."""

        component = MultipleControlComponent()
        result = component.build()

        assert all(isinstance(ctrl, ft.Text) for ctrl in result.controls)
        assert result.controls[0].value == "Header"
        assert result.controls[1].value == "Content"
        assert result.controls[2].value == "Footer"


class StatefulComponent(RemailComponent):
    """Component with internal state for testing."""

    def __init__(self):
        super().__init__()
        self.counter = 0

    def build(self) -> ft.Control:
        return ft.Text(f"Counter: {self.counter}")

    def increment(self):
        self.counter += 1


class TestStatefulRemailComponent:
    """Test suite for stateful components."""

    def test_component_can_have_state(self):
        """Test that component can maintain internal state."""

        component = StatefulComponent()

        assert component.counter == 0

    def test_component_state_can_be_modified(self):
        """Test that component state can be modified."""

        component = StatefulComponent()
        component.increment()

        assert component.counter == 1

    def test_component_build_reflects_state(self):
        """Test that build method can access component state."""

        component = StatefulComponent()
        component.counter = 5
        result = component.build()

        assert isinstance(result, ft.Text)
        assert result.value == "Counter: 5"

    def test_multiple_component_instances_independent(self):
        """Test that multiple component instances have independent state."""

        component1 = StatefulComponent()
        component2 = StatefulComponent()

        component1.increment()
        component1.increment()

        assert component1.counter == 2
        assert component2.counter == 0
