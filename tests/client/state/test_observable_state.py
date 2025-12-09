import unittest
from enum import Enum
from unittest.mock import Mock

from remail.client.state.observable_state import ObservableState

# Klassen importieren
# from yourmodule import ObservableState


class TestEnum(Enum):
    A = 1
    B = 2


class TestObservableState(unittest.TestCase):
    def setUp(self):
        self.state = ObservableState[TestEnum]()

    def test_strong_observer_triggered(self):
        cb = Mock()
        self.state.register_observer(TestEnum.A, cb, weak=False)

        self.state.set(TestEnum.A, "value1")
        cb.assert_called_once_with("value1")

    def test_weak_observer_triggered(self):
        class X:
            def method(self, v):
                pass

        x = X()
        cb = Mock(wraps=x.method)
        # bound method → WeakMethod
        self.state.register_observer(TestEnum.A, cb, weak=True)

        self.state.set(TestEnum.A, 123)
        cb.assert_called_once_with(123)

    def test_weak_observer_removed_when_dead(self):
        class X:
            def method(self, v):
                pass

        x = X()
        cb = x.method
        self.state.register_observer(TestEnum.A, cb, weak=True)

        # Objekt löschen → WeakMethod sollte danach nicht mehr ausgeführt werden
        del x

        # Wert setzen: Observer existiert, aber WeakMethod ist tot → kein Fehler, kein Call
        self.state.set(TestEnum.A, "test")

        # Prüfen, dass WeakSet leergeräumt wurde
        self.assertEqual(len(self.state._weak_observers[TestEnum.A]), 0)

    def test_value_not_retriggered_when_same(self):
        cb = Mock()
        self.state.register_observer(TestEnum.A, cb)

        self.state.set(TestEnum.A, "x")
        self.state.set(TestEnum.A, "x")  # gleicher Wert → kein erneuter Trigger

        cb.assert_called_once_with("x")

    def test_get_returns_correct_value(self):
        self.state.set(TestEnum.B, 42)
        self.assertEqual(self.state.get(TestEnum.B), 42)

    def test_trigger_calls_all_registered(self):
        c1, c2 = Mock(), Mock()
        self.state.register_observer(TestEnum.A, c1)
        self.state.register_observer(TestEnum.A, c2)

        self.state.set(TestEnum.A, 999)

        c1.assert_called_once_with(999)
        c2.assert_called_once_with(999)


if __name__ == "__main__":
    unittest.main()
