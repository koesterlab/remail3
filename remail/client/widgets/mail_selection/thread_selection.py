import datetime
import logging
from typing import Any

import flet as ft

from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
from remail.utils.timer import Timer

from ...state.main_app_state import MainAppState, MainAppStateProperties
from .profile_picture import create_profile_picture
from .thread_preview import ThreadPreview

_logger = logging.getLogger(__name__)

"""
Subwidget of selectionBar to choose between different conversations of a contact
"""


class ThreadSelection(ft.Container):
    def __init__(self, state: MainAppState):
        self.conversation: ConversationDTO | None = None
        self.slided_in: bool = False
        self._state: MainAppState = state
        self._content = ft.Column(spacing=0)
        self._image = ft.Container(width=40, height=40)
        self._primary_text = ft.Text("", weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
        self._secondary_text = ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
        self._thread_offset = 50  # Track how many threads are currently shown

        state.register_observer(MainAppStateProperties.ACTIVE_CONVERSATION, self.set_content)

        super().__init__(
            ft.Column(
                controls=[
                    # header
                    ft.Container(
                        padding=ft.Padding.only(left=0, right=5, top=5, bottom=10),
                        content=ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_BACK,
                                    on_click=lambda _: state.set(
                                        MainAppStateProperties.ACTIVE_CONVERSATION, None
                                    ),
                                    icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                    icon_size=30,
                                ),
                                self._image,
                                ft.Container(
                                    ft.Column(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[self._primary_text, self._secondary_text],
                                        spacing=6,
                                    ),
                                    height=50,
                                ),
                            ],
                            spacing=7,
                        ),
                        border=ft.Border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY)),
                    ),
                    # thread_list
                    ft.Container(
                        alignment=ft.Alignment.TOP_CENTER,
                        expand=True,
                        content=ft.Column(
                            scroll=ft.ScrollMode.AUTO,
                            alignment=ft.MainAxisAlignment.START,
                            spacing=0,
                            controls=[self._content],
                        ),
                    ),
                ]
            )
        )

        ### Add Thread dialog ###
        thread_created = False

        def on_blur_new_thread(e: Any):
            if not thread_created:
                self.add_thread_field.value = ""
                self.add_thread_field.update()

        def on_submit_new_thread(e: Any):
            nonlocal thread_created
            thread_created = True
            thread = ThreadPreviewDTO(
                -1, self.add_thread_field.value, 0, 0, "", datetime.datetime.now()
            )
            if not self.conversation:
                return  # just for mypy
            self.conversation.threads.append(thread)  # only in the frontend, until message is sent
            self._state.set(MainAppStateProperties.ACTIVE_THREAD_CONVERSATION, self.conversation)
            self._state.set(MainAppStateProperties.ACTIVE_THREAD, thread)

        self.add_thread_field = ft.TextField(
            on_submit=on_submit_new_thread,
            on_blur=on_blur_new_thread,
            color=ft.Colors.ON_SURFACE_VARIANT,
            focused_color=ft.Colors.ON_SURFACE,
            focused_border_color=ft.Colors.TRANSPARENT,
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.TRANSPARENT,
            dense=True,
            expand=True,
            text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
            border_radius=ft.BorderRadius.all(20),
            prefix_icon=ft.Icons.ADD,
            hint_text="add Topic",
        )

        self.add_thread_btn = ft.Container(self.add_thread_field, padding=ft.Padding.only(top=5))

    def set_content(self, content: ConversationDTO):
        if not content:
            return
        t = Timer()
        self._image.content = create_profile_picture(content)
        self.conversation = content
        # Reset the offset when a new conversation is selected
        self._thread_offset = 50

        if len(content.contacts) == 1:
            contact = content.contacts[0]
            self._primary_text.value = content.get_member_string(extended=True)
            self._secondary_text.value = contact.email
        else:
            self._primary_text.value = (
                content.custom_name if content.custom_name else content.get_member_string()
            )
            self._secondary_text.value = str(len(content.contacts)) + " Members"

        # Sort threads by unread count so unread threads appear first
        # Only show the first 50 threads to avoid UI freezing
        # A single conversation can have thousands of threads which would freeze the UI for seconds
        all_sorted_threads = sorted(content.threads, key=lambda t: t.unread_count, reverse=True)
        sorted_threads = all_sorted_threads[:50]

        def load_more_threads(_):
            # Load the next 50 threads and append them to the list
            next_threads = all_sorted_threads[self._thread_offset : self._thread_offset + 50]
            if not next_threads:
                # No more threads to load — hide the button
                load_more_btn.visible = False
                load_more_btn.update()
                return
            # Increase the offset for the next "Load more" click
            self._thread_offset += 50
            new_widgets = [
                ThreadPreview(self._state, elem, self.conversation) for elem in next_threads
            ]
            # Insert new threads before the "load more" and "add thread" buttons
            insert_pos = len(self._content.controls) - 2
            for i, w in enumerate(new_widgets):
                self._content.controls.insert(insert_pos + i, w)
            self._content.update()

        # "Load more" button shown at the bottom of the thread list
        load_more_btn = ft.Container(
            ft.TextButton(
                "Load more threads",
                icon=ft.Icons.EXPAND_MORE,
                on_click=load_more_threads,
            ),
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.all(10),
            # Hide the button if there are fewer than 50 threads total
            visible=len(all_sorted_threads) > 50,
        )

        self._content.controls = [
            ThreadPreview(self._state, elem, self.conversation) for elem in sorted_threads
        ] + [load_more_btn, self.add_thread_btn]  # type: ignore

        _logger.info(
            "ThreadSelection built %d thread widget(s). (%s)", len(sorted_threads), t.elapsed()
        )
        t2 = Timer()
        self.update()
        _logger.info("ThreadSelection.update() done. (%s)", t2.elapsed())
