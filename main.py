import flet as ft
import httpx
import asyncio

async def main(page: ft.Page):
    page.title = "Way VPN"
    page.background_color = "#0B0B0E"
    page.theme_mode = ft.ThemeMode.DARK
    
    # Состояние приложения
    is_connected = False
    selected_file_path = None
    server_ip = "https://194.87.82.136:2053/BaDwafiFKsYBKp4XwK/"  # Твой IP сервера

    # Поля ввода (Использованы label и чистый родной prefix_text из справочника)
    key_input = ft.TextField(
        label="Ваш VLESS-ключ", 
        border_color="#242438", 
        focused_border_color="#00D2FF"
    )
    phone_input = ft.TextField(
        label="Номер телефона (для оплаты)", 
        prefix_text="+", 
        border_color="#242438", 
        focused_border_color="#00D2FF"
    )
    
    # Текст статуса и иконка щита (Использована константа ft.icons.SHIELD)
    status_text = ft.Text("ОТКЛЮЧЕНО", size=24, color="red", weight=ft.FontWeight.BOLD)
    shield_icon = ft.Icon(name=ft.icons.SHIELD, color="#00D2FF", size=100)

    # Системное окно уведомлений (AlertDialog)
    def show_alert(text):
        def close_dialog(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Уведомление", color="#00D2FF"),
            content=ft.Text(text),
            actions=[ft.TextButton(text="OK", on_click=close_dialog)]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    # Логика кнопки Подключить
    def toggle_vpn(e):
        nonlocal is_connected
        if not key_input.value.strip():
            show_alert("Сначала вставьте ваш VLESS-ключ доступа!")
            return
        is_connected = not is_connected
        if is_connected:
            status_text.value = "ПОДКЛЮЧЕНО"
            status_text.color = "green"
            connect_btn.text = "ОТКЛЮЧИТЬ"
            connect_btn.bgcolor = "red"
        else:
            status_text.value = "ОТКЛЮЧЕНО"
            status_text.color = "red"
            connect_btn.text = "ПОДКЛЮЧИТЬ"
            connect_btn.bgcolor = "#00D2FF"
        page.update()

    connect_btn = ft.ElevatedButton(
        text="ПОДКЛЮЧИТЬ",
        bgcolor="#00D2FF",
        color="black",
        width=250,
        height=60,
        on_click=toggle_vpn
    )

    # Логика выбора файла чека
    def on_file_result(e: ft.FilePickerResultEvent):
        nonlocal selected_file_path
        if e.files and len(e.files) > 0:
            selected_file_path = e.files[0].path
            file_btn.text = "Чек выбран ✓"
            file_btn.disabled = True
            page.update()
            show_alert("Чек успешно прикреплен!")

    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    file_btn = ft.OutlinedButton(
        text="Выбрать скриншот чека из галереи",
        icon=ft.icons.ATTACH_FILE,
        width=400,
        on_click=lambda _: file_picker.pick_files(allow_multiple=False)
    )

    # Опрос сервера (Поллинг)
    async def check_activation_loop(phone):
        while True:
            await asyncio.sleep(3)
            try:
                async with httpx.AsyncClient() as client:
                    res = await client.get(f"http://{server_ip}:8000/api/check/{phone}")
                    if res.status_code == 200:
                        data = res.json()
                        if data.get("status") == "approved":
                            key_input.value = data.get("key", "")
                            show_alert("🚀 ДОСТУП АКТИВИРОВАН! Нажмите ПОДКЛЮЧИТЬ!")
                            tabs.selected_index = 0
                            main_container.content = main_layout
                            page.update()
                            break
                        elif data.get("status") == "declined":
                            show_alert("❌ Чек отклонен администратором. Свяжитесь с Магомедом.")
                            break
            except Exception:
                pass

    # Отправка чека
    async def send_payment(e):
        if not phone_input.value.strip():
            show_alert("Введите номер телефона!")
            return
        if not selected_file_path:
            show_alert("Пожалуйста, выберите скриншот чека!")
            return
        
        show_alert("Чек отправлен! Ожидайте проверку...")
        asyncio.create_task(check_activation_loop(phone_input.value.strip()))

    send_btn = ft.ElevatedButton(
        text="ОТПРАВИТЬ НА ПРОВЕРКУ",
        bgcolor="#00D2FF",
        color="black",
        width=400,
        height=50,
        on_click=send_payment
    )

    # Главный экран VPN
    main_layout = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            shield_icon,
            ft.Text("WAY VPN", size=32, weight=ft.FontWeight.BOLD, color="#00D2FF"),
            ft.Text("Статус соединения:", color="white"),
            status_text,
            ft.Container(height=20),
            key_input,
            ft.Container(height=20),
            connect_btn
        ]
    )

    # Экран оплаты подписки
    buy_layout = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Icon(name=ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED, color="#00D2FF", size=80),
            ft.Text("Активация подписки", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Стоимость: 249 рублей / месяц", color="white"),
            ft.Container(
                content=ft.Text(
                    "Переведите 249₽ по номеру телефона:\n+7 (964) 073-05-51\n\nПосле оплаты прикрепите скриншот чека ниже.",
                    text_align=ft.TextAlign.CENTER
                ),
                bgcolor="#16161F",
                padding=16,
                border_radius=10
            ),
            phone_input,
            ft.Container(height=10),
            file_btn,
            ft.Container(height=20),
            send_btn
        ]
    )

    def on_tab_change(e):
        if e.control.selected_index == 0:
            main_container.content = main_layout
        else:
            main_container.content = buy_layout
        page.update()

    # Нижнее меню (NavigationBarDestination заменён на NavigationDestination согласно справочнику)
    tabs = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.VPN_LOCK, label="VPN"),
            ft.NavigationDestination(icon=ft.icons.SHOPPING_BAG, label="Купить подписку"),
        ],
        on_change=on_tab_change,
        bgcolor="#16161F"
    )

    main_container = ft.Container(content=main_layout, expand=True, padding=20)
    
    page.add(main_container)
    page.navigation_bar = tabs
    page.update()

ft.run(main)
