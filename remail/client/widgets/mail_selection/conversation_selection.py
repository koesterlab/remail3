import asyncio
import datetime
import logging
import re

import flet as ft
from flet import Control

from remail.client.state.main_app_state import MainAppState, MainAppStateProperties
from remail.client.widgets.mail_selection.action import Action
from remail.client.widgets.mail_selection.action_preview import ActionPreview
from remail.client.widgets.mail_selection.contact_preview import ContactPreview
from remail.client.widgets.mail_selection.conversation_preview import ConversationPreview
from remail.client.widgets.mail_selection.group_preview import GroupPreview
from remail.controllers.dtos.conversations import ConversationDTO
from remail.utils.timer import Timer

_logger = logging.getLogger(__name__)

"""
Subwidget of selectionBar to choose between different contacts (+groups) and actions
"""


class ConversationSelection(ft.Container):
    def __init__(self, state: MainAppState):
        self.state = state
        self.inner_content = ft.Column(spacing=0)
        self.elements: dict[int, tuple[ConversationDTO, Control]] = {}
        self.active_search_cache = None
        state.register_observer(MainAppStateProperties.SEARCH_TERM, self._on_search_change)
        state.register_observer(MainAppStateProperties.DISPLAYED_MAILS, self._on_search_change)
        super().__init__(
            alignment=ft.Alignment.TOP_CENTER,
            expand=True,
            content=ft.Column(  # outer: align content to top, middle: scroll, inner: enumeration of elements
                scroll=ft.ScrollMode.AUTO,
                alignment=ft.MainAxisAlignment.START,
                spacing=0,
                controls=[self.inner_content],
            ),
        )

    def _on_search_change(self, _):
        search = self.state.get(MainAppStateProperties.SEARCH_TERM)
        if not search or search == "":
            content = self.state.get(MainAppStateProperties.DISPLAYED_MAILS)
        else:
            if search == self.active_search_cache:
                return  # same search -> no change needed
            self.active_search_cache = search
            content: list[ConversationDTO | Action] = self.state.get_active_email_account().search(
                search
            )
            # special search actions: #todo: more
            if re.match(
                r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]", search
            ):  # option "mail hinzufügen
                content.insert(
                    0,
                    Action(
                        search + " zu Kontakten hinzufügen",
                        "Als neuen Kontakt erstellen",
                        lambda: None,  # todo
                        ft.Colors.SECONDARY,
                        ft.Icons.ADD,
                    ),
                )
                content.insert(
                    0,
                    Action(
                        "Nachricht an " + search,
                        "Neuer Chat",
                        lambda: None,  # todo
                        ft.Colors.PRIMARY,
                        ft.Icons.MAIL,
                    ),
                )

        async def u():
            await self.set_content(content)

        self.page.run_task(u)

    async def set_content(self, content: list[ConversationDTO | Action]):
        t = Timer()
        _logger.info("Rendering %d conversation(s) in UI...", len(content))

        # sort
        def compute_order_value(elem: ConversationDTO | Action):
            time = datetime.datetime.min
            if isinstance(elem, Action):
                category = "C"
            else:
                if len(elem.threads) <= 0:
                    time = datetime.datetime.min
                else:
                    time = max([t.last_message_datetime for t in elem.threads])
                if elem.is_favorite:
                    category = "B"
                elif sum(t.unread_count for t in elem.threads) > 0:
                    category = "AB"
                else:
                    category = "A"
            return category, time

        content.sort(key=compute_order_value, reverse=True)

        # check if it is the initial call, then skip check for existing elements
        updating = not len(self.elements) <= 0
        element_list = []
        counter = 0
        update_bound = 2
        for elem in content:
            if updating and not isinstance(elem, Action):
                stored = self.elements.get(elem.id, None)
                if stored is not None:
                    stored_dto, stored_widget = stored
                    if stored_dto == elem:  # DTO unchanged – reuse widget
                        element_list.append(stored_widget)
                        continue
                    # DTO changed (new mail, read-state, …) – drop stale widget
                    del self.elements[elem.id]
            counter += 1
            element_list.append(self.create_list_item(elem))
            if counter == update_bound:  # showing the list after every
                self.inner_content.controls = element_list
                self.update()
                await asyncio.sleep(0.000001)
                update_bound <<= 1  # updates after 2,4,8,16,32,... elements

        self.inner_content.controls = element_list
        self.update()

        _logger.info("UI render done: %d widget(s) shown. (%s)", len(element_list), t.elapsed())

    def create_list_item(self, elem: Action | ConversationDTO):
        if isinstance(elem, Action):
            item: ActionPreview | ConversationPreview = ActionPreview(elem)
        elif len(elem.contacts) == 1:
            item = ContactPreview(self.state, elem)
            self.elements[elem.id] = (elem, item)
        else:
            item = GroupPreview(self.state, elem)
            self.elements[elem.id] = (elem, item)

        return item
