# import weakref
# from collections.abc import Callable
# from typing import Any, Union
# from uuid import uuid4
#
# from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
# from remail.enums.email_folders import EmailFolders
#
#
# class MainAppState:
#     def __init__(self) -> None:
#
#
#         self.__search_term: str | None = None
#         self.__search_term_listeners: dict[str, weakref.WeakMethod | Callable] = {}
#
#         self.__active_folder: EmailFolders | None = None
#         self.__active_folder_listeners: dict[str, weakref.WeakMethod | Callable] = {}
#
#         self.__displayed: list[ConversationDTO] = []
#         self.__displayed_listeners: dict[str, weakref.WeakMethod | Callable] = {}
#
#         self.__active_thread: ThreadPreviewDTO | None = None
#         self.__active_thread_listeners: dict[str, weakref.WeakMethod | Callable] = {}
#
#     # ---------------- Selection ----------------
#
#
#
#     # ---------------- Search Term ----------------
#
#     @property
#     def search_term(self) -> str:
#         return self.__search_term if self.__search_term else ""
#
#     def set_search_term(self, term: str) -> None:
#         if self.__search_term != term:
#             self.__search_term = term
#             self.__cleanup_weak_listeners(self.__search_term_listeners)
#             for callback_ref in self.__search_term_listeners.values():
#                 callback = self.__unwrap_weak(callback_ref)
#                 if callback:
#                     callback(term)
#
#     def listen_search_term(self, callback: Callable[[str], None]) -> str:
#         token = str(uuid4())
#         self.__search_term_listeners[token] = self.__wrap_weak(callback)
#         return token
#
#     def remove_search_term_listener(self, token: str) -> None:
#         self.__search_term_listeners.pop(token, None)
#
#     # ---------------- Active Folder ----------------
#
#     @property
#     def active_folder(self) -> EmailFolders | None:
#         return self.__active_folder
#
#     def set_active_folder(self, folder: "EmailFolders") -> None:
#         if self.__active_folder != folder:
#             self.__active_folder = folder
#             self.__cleanup_weak_listeners(self.__active_folder_listeners)
#             for callback_ref in self.__active_folder_listeners.values():
#                 callback = self.__unwrap_weak(callback_ref)
#                 if callback:
#                     callback(folder)
#
#     def listen_active_folder(self, callback: Callable[["EmailFolders"], None]) -> str:
#         token = str(uuid4())
#         self.__active_folder_listeners[token] = self.__wrap_weak(callback)
#         return token
#
#     def remove_active_folder_listener(self, token: str) -> None:
#         self.__active_folder_listeners.pop(token, None)
#
#     # ---------------- Displayed Conversations ----------------
#
#     @property
#     def displayed(self) -> list[ConversationDTO]:
#         return self.__displayed
#
#     def set_displayed(self, conversations: list[ConversationDTO]) -> None:
#         self.__displayed = conversations
#         self.__cleanup_weak_listeners(self.__displayed_listeners)
#         for callback_ref in self.__displayed_listeners.values():
#             callback = self.__unwrap_weak(callback_ref)
#             if callback:
#                 callback(conversations)
#
#     def listen_displayed(self, callback: Callable[[list["ConversationDTO"]], None]) -> str:
#         token = str(uuid4())
#         self.__displayed_listeners[token] = self.__wrap_weak(callback)
#         return token
#
#     def remove_displayed_listener(self, token: str) -> None:
#         self.__displayed_listeners.pop(token, None)
#
#     # ---------------- Active Thread ----------------
#
#     @property
#     def active_thread(self) -> ThreadPreviewDTO | None:
#         return self.__active_thread
#
#     def set_active_thread(self, thread: ThreadPreviewDTO | None) -> None:
#         self.__active_thread = thread
#         self.__cleanup_weak_listeners(self.__active_thread_listeners)
#         for callback_ref in self.__active_thread_listeners.values():
#             callback = self.__unwrap_weak(callback_ref)
#             if callback:
#                 callback(thread)
#
#     def listen_active_thread(self, callback: Callable[[ThreadPreviewDTO | None], None]) -> str:
#         token = str(uuid4())
#         self.__active_thread_listeners[token] = self.__wrap_weak(callback)
#         return token
#
#     def remove_active_thread_listener(self, token: str) -> None:
#         self.__active_thread_listeners.pop(token, None)
#
#     # ---------------- Helpers ----------------
#
#     def __wrap_weak(self, callback) -> Any:
#         """Wrapped method if bound, else return callable as-is"""
#         try:
#             # gebundene Methode
#             return weakref.WeakMethod(callback)
#         except TypeError:
#             # normale Funktion
#             return callback
#
#     def __unwrap_weak(self, callback_ref) -> Any:
#         if isinstance(callback_ref, weakref.WeakMethod):
#             return callback_ref()
#         return callback_ref
#
#     def __cleanup_weak_listeners(self, listeners_dict) -> Any:
#         """Remove dead weakrefs"""
#         dead_tokens = [t for t, ref in listeners_dict.items() if self.__unwrap_weak(ref) is None]
#         for t in dead_tokens:
#             listeners_dict.pop(t)
