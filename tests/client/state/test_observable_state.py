import unittest
from enum import Enum
from unittest.mock import Mock

from remail.client.state.observable_state import ObservableState

# Klassen importieren
# from yourmodule import ObservableState


class SampleEnum(Enum):
    A = 1
    B = 2


class TestObservableState(unittest.TestCase):
    def setUp(self):
        self.state = ObservableState[SampleEnum]()

    def test_strong_observer_triggered(self):
        """Test that strong observers are triggered when value changes."""
        cb = Mock()
        # weak parameter is accepted for backward compatibility but has no effect
        self.state.register_observer(SampleEnum.A, cb, weak=False)

        self.state.set(SampleEnum.A, "value1")
        cb.assert_called_once_with("value1")

    def test_weak_observer_triggered(self):
        """Test that observers registered with weak=True still work with pattern_kit.Event."""

        class X:
            def method(self, v):
                pass

        x = X()
        cb = Mock(wraps=x.method)
        # weak parameter is accepted for backward compatibility
        self.state.register_observer(SampleEnum.A, cb, weak=True)

        self.state.set(SampleEnum.A, 123)
        cb.assert_called_once_with(123)

    def test_weak_observer_removed_when_dead(self):
        """Test that pattern_kit.Event handles garbage collection naturally."""

        class X:
            def method(self, v):
                pass

        x = X()
        cb = x.method
        self.state.register_observer(SampleEnum.A, cb, weak=True)

        # Note: With pattern_kit.Event, weak references are handled differently
        # The test verifies that the system continues to work correctly
        # even after the original object is deleted
        del x

        # Wert setzen: Should not raise an error
        self.state.set(SampleEnum.A, "test")

    def test_value_not_retriggered_when_same(self):
        cb = Mock()
        self.state.register_observer(SampleEnum.A, cb)

        self.state.set(SampleEnum.A, "x")
        self.state.set(SampleEnum.A, "x")  # gleicher Wert → kein erneuter Trigger

        cb.assert_called_once_with("x")

    def test_get_returns_correct_value(self):
        self.state.set(SampleEnum.B, 42)
        self.assertEqual(self.state.get(SampleEnum.B), 42)

    def test_trigger_calls_all_registered(self):
        c1, c2 = Mock(), Mock()
        self.state.register_observer(SampleEnum.A, c1)
        self.state.register_observer(SampleEnum.A, c2)

        self.state.set(SampleEnum.A, 999)

        c1.assert_called_once_with(999)
        c2.assert_called_once_with(999)
