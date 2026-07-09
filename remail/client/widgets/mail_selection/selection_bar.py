import logging

import flet as ft

from remail.client.state.main_app_state import MainAppState, MainAppStateProperties
from remail.client.widgets.mail_selection.conversation_selection import ConversationSelection
from remail.client.widgets.mail_selection.search_header import SearchHeader
from remail.client.widgets.mail_selection.thread_selection import ThreadSelection
from remail.controllers.dtos.conversations import ConversationDTO
from remail.utils.timer import Timer

_logger = logging.getLogger(__name__)

"""
Overall Widget to combine searchbar and selection widgets
Switches with scroll animation between conversations and threads
"""


class SelectionBar(ft.Container):
    def __init__(self, state: MainAppState):
        # subwidgets
        self.topic_selection = ThreadSelection(state)
        self.conversation_selection = ConversationSelection(state)
        self.main_content = ft.Column(
        controls=[SearchHeader(state), self.conversation_selection],     
            expand=True,
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            offset=ft.Offset(0, 0),
        )
        self.topic_selection.offset = ft.Offset(1, 0)
        self.topic_selection.animate_offset = 140
        self.main_content.animate_offset = 140
        self.__state = state
        self.topic_selection_active = False

        state.register_observer(
            MainAppStateProperties.ACTIVE_CONVERSATION, self._on_selected_conversation_change
        )
        super().__init__(
            bgcolor=ft.Colors.SURFACE,
            content=ft.Stack(controls=[self.main_content, self.topic_selection], expand=True),
            expand=False,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

    def _on_selected_conversation_change(self, conversation: ConversationDTO) -> None:
        t = Timer()
        if conversation:
            if not self.topic_selection_active:  # slide_in_animation
                self.topic_selection.offset = ft.Offset(0, 0)
                self.main_content.offset = ft.Offset(-1, 0)
                self.topic_selection_active = True
        else:
            if self.topic_selection_active:  # slide out animation
                self.topic_selection.offset = ft.Offset(1, 0)
                self.main_content.offset = ft.Offset(0, 0)
                self.topic_selection_active = False
        try:
            _logger.info("SelectionBar: calling update()...")
            self.topic_selection.update()
            self.main_content.update()
            _logger.info("SelectionBar: update() done. (%s)", t.elapsed())
        except RuntimeError:
            pass
