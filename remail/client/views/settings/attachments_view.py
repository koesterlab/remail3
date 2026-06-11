import datetime
from dataclasses import dataclass, field

import flet as ft
from sqlmodel import Session, select

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


@dataclass
class AttachmentGroup:
    filename: str
    thread_title: str
    sender_name: str
    sender_email: str
    versions: list[AttachmentVersion] = field(default_factory=list)


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

        def build_group(group: AttachmentGroup) -> ft.Container:
            latest = group.versions[0] if group.versions else None
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
                            f"Latest from {latest.sender_name} <{latest.sender_email}>"
                            if latest
                            else "",
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.HISTORY, size=16),
                                        ft.Text(format_date(version.sent_at), width=130, size=12),
                                        ft.Text(
                                            f"{version.sender_name} <{version.sender_email}>",
                                            size=12,
                                            expand=True,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                    spacing=8,
                                )
                                for version in group.versions
                            ],
                            spacing=4,
                        ),
                    ],
                    spacing=8,
                ),
            )

        def apply_filter(_=None) -> None:
            term = (search.value or "").strip().casefold()
            filtered = [
                group
                for group in groups
                if not term
                or term in group.filename.casefold()
                or term in group.sender_name.casefold()
                or term in group.sender_email.casefold()
                or any(
                    term in version.sender_name.casefold()
                    or term in version.sender_email.casefold()
                    for version in group.versions
                )
            ]

            if filtered:
                results.controls = [build_group(group) for group in filtered]
            else:
                results.controls = [
                    ft.Container(
                        ft.Text("No attachments found", color=ft.Colors.ON_SURFACE_VARIANT),
                        padding=12,
                    )
                ]
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
                    ft.Text("Attachments", size=18, weight=ft.FontWeight.BOLD),
                    search,
                    results,
                ],
                spacing=12,
                expand=True,
            ),
        )

    @session
    def _load_attachment_groups(self, session: Session) -> list[AttachmentGroup]:
        grouped: dict[tuple[int, str], AttachmentGroup] = {}
        attachments = session.exec(select(Attachment)).all()

        for attachment in attachments:
            email = attachment.email
            thread = email.thread
            sender = email.sender
            filename = attachment.filename
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

        return sorted(
            grouped.values(),
            key=lambda group: group.versions[0].sent_at or datetime.datetime.min,
            reverse=True,
        )
