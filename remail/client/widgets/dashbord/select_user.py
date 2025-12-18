from remail.client.state import MainAppState, MainAppStateProperties
import flet as ft

from remail.controllers.dtos.user_dto import UserDTO
from remail.enums import UserAccountCategory
from remail.interfaces.email.services.user_service import UserService


def create_user_selection(state: MainAppState) -> ft.Dropdown:
    def on_user_changes(user: UserDTO):
        dropdown.value = str(user.id)

    state.register_observer(MainAppStateProperties.ACTIVE_USER, on_user_changes)

    def createOption(mail: UserDTO) -> ft.Container:#
        if mail.category == UserAccountCategory.WORK:
            icon = ft.Icons.WORK_OUTLINED
        elif mail.category == UserAccountCategory.PRIVATE:
            icon = ft.Icons.PERSON_OUTLINED
        elif mail.category == UserAccountCategory.HOBBY:
            icon = ft.Icons.SPORTS_FOOTBALL_OUTLINED
        else:
            icon = ft.Icons.MAIL_OUTLINED

        return ft.Container(ft.Row([
            ft.Column([
                ft.Text(mail.name, weight=ft.FontWeight.BOLD),
                ft.Text(mail.email)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Icon(icon)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
        pass

    def on_user_selected():
        new_user = [acc for acc in all_users if str(acc.email) == dropdown.value]
        if len(new_user) != 1:
            return
        new_user = new_user[0]
        state.set(MainAppStateProperties.ACTIVE_USER, new_user)
        state.set(MainAppStateProperties.ACTIVE_THREAD, None)
        state.set(MainAppStateProperties.SEARCH_TERM, "")

    all_users = UserService.get_all_users_dto() #todo?
    initial_user: UserDTO = state.get(MainAppStateProperties.ACTIVE_USER)

    dropdown = ft.Dropdown(
        border=ft.InputBorder.UNDERLINE,
        editable=True,
        leading_icon=ft.Icons.MAIL,
        options=[ft.DropdownOption(str(acc.email), content=createOption(acc)) for acc in all_users],
        on_change=lambda _: on_user_selected(),
        value=initial_user.email
    )
    return dropdown

