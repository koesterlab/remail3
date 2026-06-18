import datetime
import inspect
import mimetypes
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import flet as ft
from sqlmodel import Session, select
from werkzeug.utils import secure_filename

from remail.controllers.dtos import SettingsDTO
from remail.models import Attachment
from remail.utils.session_management import session

from .settings_sub_view import SettingsSubView


@dataclass
class AttachmentVersion:
    filename: str
    sender_name: str
    sender_email: str
    thread_title: str
    sent_at: datetime.datetime | None
    file_path: str
    file_size: int
    file_type: str


@dataclass
class AttachmentGroup:
    filename: str
    thread_title: str
    sender_name: str
    sender_email: str
    versions: list[AttachmentVersion] = field(default_factory=list)
    search_text: str = ""


class AttachmentsView(SettingsSubView):
    def create_page(self, settings: SettingsDTO) -> ft.Container:
        groups = self._load_attachment_groups()
        results = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        search = ft.TextField(
            label="Search attachments or contacts",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
        )

        def format_date(value: datetime.datetime | None) -> str:
            return value.strftime("%d.%m.%Y %H:%M") if value else "Unknown date"

        def format_size(value: int) -> str:
            if value <= 0:
                return "Unknown size"
            units = ["B", "KB", "MB", "GB"]
            size = float(value)
            unit = 0
            while size >= 1024 and unit < len(units) - 1:
                size /= 1024
                unit += 1
            return f"{size:.1f} {units[unit]}" if unit else f"{int(size)} {units[unit]}"

        def open_attachment(_: object, path: str) -> None:
            if not path:
                return
            if self._open_attachment_file(path):
                return
            page = self.page
            if page is not None:
                uri = Path(path).resolve().as_uri()

                async def launch_url() -> None:
                    result = page.launch_url(uri)
                    if inspect.isawaitable(result):
                        await result

                page.run_task(launch_url)

        def build_attachment_row(version: AttachmentVersion, version_number: int) -> ft.Control:
            is_image = version.file_type.startswith("image/")
            version_label = "Latest version" if version_number == 1 else f"Version {version_number}"
            return ft.Container(
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=4,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                ink=bool(version.file_path),
                on_click=lambda event, path=version.file_path: open_attachment(event, path),
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.IMAGE if is_image else ft.Icons.INSERT_DRIVE_FILE,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            size=20,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    f"{version_label}: {version.filename}",
                                    weight=ft.FontWeight.W_600,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    " | ".join(
                                        [
                                            format_date(version.sent_at),
                                            format_size(version.file_size),
                                            f"{version.sender_name} <{version.sender_email}>",
                                        ]
                                    ),
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.OPEN_IN_NEW,
                            tooltip="Open attachment",
                            disabled=not version.file_path,
                            on_click=lambda event, path=version.file_path: open_attachment(
                                event, path
                            ),
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

        def build_group(group: AttachmentGroup) -> ft.Container:
            return ft.Container(
                padding=12,
                border=ft.Border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.ATTACH_FILE, color=ft.Colors.BLUE),
                                ft.Column(
                                    [
                                        ft.Text(
                                            group.filename,
                                            weight=ft.FontWeight.BOLD,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                        ft.Text(
                                            group.thread_title,
                                            size=12,
                                            color=ft.Colors.ON_SURFACE_VARIANT,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Text(
                                    f"{len(group.versions)} version"
                                    + ("" if len(group.versions) == 1 else "s"),
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Text(
                            f"Latest from {group.sender_name} <{group.sender_email}>",
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Column(
                            [
                                build_attachment_row(version, index + 1)
                                for index, version in enumerate(group.versions)
                            ],
                            spacing=4,
                        ),
                    ],
                    spacing=8,
                ),
            )

        group_controls = [(group, build_group(group)) for group in groups]
        empty_results = ft.Container(
            ft.Text("No attachments found", color=ft.Colors.ON_SURFACE_VARIANT),
            padding=12,
        )

        def apply_filter(_=None) -> None:
            term = (search.value or "").strip().casefold()
            filtered = [
                control
                for group, control in group_controls
                if not term or term in group.search_text
            ]

            if filtered:
                results.controls = filtered
            else:
                results.controls = [empty_results]
            try:
                results.update()
            except RuntimeError:
                pass

        search.on_change = apply_filter
        apply_filter()

        return ft.Container(
            padding=20,
            expand=True,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Attachments", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                f"{sum(len(group.versions) for group in groups)} files",
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    search,
                    results,
                ],
                spacing=12,
                expand=True,
            ),
        )

    @staticmethod
    def _attachment_path(attachment: Attachment) -> str:
        email = attachment.email
        message_id = secure_filename(email.message_id or "").replace(".", "_")
        name, ext = os.path.splitext(attachment.filename)
        safe_name = secure_filename((name.replace(".", "")[:50] + ext).strip())
        path = os.path.abspath(
            os.path.join("remail", "database", "attachments", message_id, safe_name)
        )
        return path if os.path.exists(path) else ""

    @staticmethod
    def _open_attachment_file(path: str) -> bool:
        if not os.path.exists(path):
            return False
        try:
            if os.name == "nt":
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            return True
        except OSError:
            return False

    @staticmethod
    def _attachment_search_text(group: AttachmentGroup) -> str:
        values = [
            group.filename,
            group.thread_title,
            group.sender_name,
            group.sender_email,
        ]
        for version in group.versions:
            values.extend(
                [
                    version.filename,
                    version.sender_name,
                    version.sender_email,
                    version.thread_title,
                    version.file_type,
                ]
            )
        return " ".join(values).casefold()

    @session
    def _load_attachment_groups(self, session: Session) -> list[AttachmentGroup]:
        grouped: dict[tuple[int, str], AttachmentGroup] = {}
        attachments = session.exec(select(Attachment)).all()

        for attachment in attachments:
            email = attachment.email
            sender = email.sender
            thread = email.thread
            filename = attachment.filename
            path = self._attachment_path(attachment)
            key = (thread.id if thread and thread.id is not None else -1, filename.casefold())
            version = AttachmentVersion(
                filename=filename,
                sender_name=(
                    sender.name or f"{sender.first_name or ''} {sender.last_name or ''}"
                ).strip()
                or sender.email_address,
                sender_email=sender.email_address,
                thread_title=thread.title if thread else "No thread",
                sent_at=email.sent_at,
                file_path=path,
                file_size=os.path.getsize(path) if path else 0,
                file_type=mimetypes.guess_type(filename)[0] or "application/octet-stream",
            )

            if key not in grouped:
                grouped[key] = AttachmentGroup(
                    filename=filename,
                    thread_title=version.thread_title,
                    sender_name=version.sender_name,
                    sender_email=version.sender_email,
                )
            grouped[key].versions.append(version)

        for group in grouped.values():
            group.versions.sort(
                key=lambda item: item.sent_at or datetime.datetime.min, reverse=True
            )
            latest = group.versions[0]
            group.sender_name = latest.sender_name
            group.sender_email = latest.sender_email
            group.search_text = self._attachment_search_text(group)

        return sorted(
            grouped.values(),
            key=lambda group: group.versions[0].sent_at or datetime.datetime.min,
            reverse=True,
        )
