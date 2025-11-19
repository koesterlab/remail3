from abc import ABC, abstractmethod

import flet as ft


class RemailComponent(ft.Control, ABC):
    @abstractmethod
    def build(self) -> ft.Control: ...
