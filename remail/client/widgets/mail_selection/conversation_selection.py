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
<<<<<<< HEAD
        self.current_search_limit = 10
        self.load_more_btn = ft.TextButton(
            "load more", icon=ft.Icons.ARROW_DOWNWARD, on_click=self._load_more, visible=False
        )
=======
        # Track how many conversations are currently loaded for "Load more" functionality
        self.current_offset = 0
>>>>>>> 8df506b (Add lazy loading for conversation and thread lists)
        state.register_observer(MainAppStateProperties.SEARCH_TERM, self._on_search_change)
        state.register_observer(MainAppStateProperties.DISPLAYED_MAILS, self._on_search_change)
        super().__init__(
            alignment=ft.Alignment.TOP_CENTER,
            expand=True,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                alignment=ft.MainAxisAlignment.START,
                spacing=0,
                controls=[self.inner_content, self.load_more_btn],
            ),
        )

    async def _load_more(self, e):
        self.current_search_limit += 10
        self._on_search_change(None, is_load_more=True)

    def _on_search_change(self, _, is_load_more=False):
        search = self.state.get(MainAppStateProperties.SEARCH_TERM)
        if not is_load_more and search != self.active_search_cache:
            self.current_search_limit = 10

        if not search or search == "":
            content = self.state.get(MainAppStateProperties.DISPLAYED_MAILS)
            self.load_more_btn.visible = False
        else:
            if search == self.active_search_cache and not is_load_more:
                return  # same search -> no change needed
            self.active_search_cache = search

            content: list[ConversationDTO | MessageDTO | Action] = (
                self.state.get_active_email_account().search(
                    search, requested_emails=self.current_search_limit
                )

            mail_count = sum(
                1 for item in content if isinstance(item, (ConversationDTO, MessageDTO))
            )
            if mail_count < self.current_search_limit:
                self.load_more_btn.visible = False
            else:
                self.load_more_btn.visible = True
            # special search actions: #todo: more
            if re.match(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]", search):
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

    def _on_load_more_click(self, _):
        """Called when the user clicks the 'Load more' button.
        Loads the next batch of 50 conversations and appends them to the list.
        """

        async def load_more():
            # Increase the offset by 50 to load the next batch
            self.current_offset += 50
            account = self.state.get_active_email_account()
            # Fetch the next 50 conversations from the database
            new_conversations = account.load_more_conversations(offset=self.current_offset)

            if not new_conversations:
                # No more conversations to load — hide the button
                self.load_more_btn.visible = False
                self.load_more_btn.update()
                return

            # Add new conversation widgets directly to the list without re-rendering everything
            # This prevents the list from scrolling back to the top
            new_widgets = [self.create_list_item(conv) for conv in new_conversations]

            # Insert new widgets before the "Load more" button (last item)
            insert_pos = len(self.inner_content.controls) - 1
            for i, w in enumerate(new_widgets):
                self.inner_content.controls.insert(insert_pos + i, w)

            # Also add to state so search works on new conversations too
            existing = self.state.get(MainAppStateProperties.DISPLAYED_MAILS)
            existing.extend(new_conversations)

            self.inner_content.update()

        self.page.run_task(load_more)

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

        updating = not len(self.elements) <= 0
        element_list = []
        counter = 0
        update_bound = 2
        for elem in content:
            if updating and not isinstance(elem, Action):
                stored = self.elements.get(elem.id, None)
                if stored is not None:
                    stored_dto, stored_widget = stored
                    if stored_dto == elem:
                        element_list.append(stored_widget)
                        continue
                    del self.elements[elem.id]
            counter += 1
            element_list.append(self.create_list_item(elem))
            if counter == update_bound:
                self.inner_content.controls = element_list
                self.update()
                await asyncio.sleep(0.000001)
                update_bound <<= 1

        # Add "Load more" button at the bottom of the list
        # This allows the user to load the next 50 conversations on demand
        self.load_more_btn = ft.Container(
            ft.TextButton(
                "Load more conversations",
                icon=ft.Icons.EXPAND_MORE,
                on_click=self._on_load_more_click,
            ),
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.all(10),
        )
        element_list.append(self.load_more_btn)

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
