import flet as ft

def create_appearance(page):
    theme_mode_map = {
        ft.ThemeMode.LIGHT: "light",
        ft.ThemeMode.DARK: "dark",
        ft.ThemeMode.SYSTEM: "system",
    }

    current_theme = theme_mode_map.get(page.theme_mode, "system")
    selected_theme = {"value": current_theme}
    
    def theme_changed(e):
        selected_theme["value"] = e.control.value
    
    def apply_theme(e):
        theme = selected_theme["value"]
        
        if theme == "light":
            page.theme_mode = ft.ThemeMode.LIGHT
        elif theme == "dark":
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.SYSTEM
        
        page.update()
        print(f"Theme applied: {theme}")

    return ft.Container(
        ft.Column([
            ft.Text("Appearance", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("Customize how the app looks and feels"),
            ft.Divider(height=2, color=ft.Colors.BLACK),
            ft.Text("Theme",weight=ft.FontWeight.BOLD),
            ft.RadioGroup(
                ft.Row(
                    [
                        ft.Radio(value="light", label="Light"),
                        ft.Radio(value="dark", label="Dark"),
                        ft.Radio(value="system", label="System"),
                    ],
                ),
                value=current_theme,
                on_change=theme_changed
            ),
            ft.Text("Font size",weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                value="Medium",
                options=[
                    ft.dropdown.Option("Small"),
                    ft.dropdown.Option("Medium"),
                    ft.dropdown.Option("Large"),
                ],
                width=200
            ),
            ft.Text("Font family",weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                value="Arial",
                options=[
                    ft.dropdown.Option("Arial"),
                    ft.dropdown.Option("Roboto"),
                    ft.dropdown.Option("Georgia"),
                    ft.dropdown.Option("Courier New"),
                    ft.dropdown.Option("Times New Roman"),
                    ft.dropdown.Option("Verdana"),
                    ft.dropdown.Option("Tahoma"),
                ],
                menu_height=200,
                width=200
            ),
            ft.Container(
                ft.ElevatedButton("Apply",on_click=apply_theme),
                alignment=ft.alignment.center
            )
        ]),
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left
    )