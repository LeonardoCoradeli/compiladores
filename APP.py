import flet as ft
from analisador_lexico import analisador_lexico
import os

def menu(page: ft.Page):

    def load_file(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = [line.rstrip('\n') for line in f.readlines()]
                page.set_editor_content(content)
                page.snack_bar = ft.SnackBar(ft.Text(f"✅ Arquivo {os.path.basename(file_path)} carregado!"))
            except Exception as error:
                page.snack_bar = ft.SnackBar(ft.Text(f"❌ Erro ao ler arquivo: {str(error)}"))
            page.snack_bar.open = True
            page.update()


    def save_file(e: ft.FilePickerResultEvent):
        if e.path:
            try:
                content = page.get_editor_content()
                with open(e.path, "w", encoding="utf-8") as f:
                    f.write('\n'.join(content))
                page.snack_bar = ft.SnackBar(ft.Text(f"💾 Arquivo {os.path.basename(e.path)} salvo com sucesso!"))
            except Exception as error:
                page.snack_bar = ft.SnackBar(ft.Text(f"❌ Erro ao salvar arquivo: {str(error)}"))
            page.snack_bar.open = True
            page.update()


    file_picker = ft.FilePicker(on_result=load_file)
    save_file_picker = ft.FilePicker(on_result=save_file)
    page.overlay.extend([file_picker, save_file_picker])

    def run_play_function(e):
        try:
            conteudo = page.get_editor_content()
            resultados = analisador_lexico("\n".join(conteudo))
            
            tokens = []
            for i in range(len(resultados['lexema'])):
                tokens.append({
                    'lexema': resultados['lexema'][i],
                    'token': resultados['token'][i],
                    'linha': resultados['linha'][i],
                    'col_inicial': resultados['col_ini'][i],
                    'col_final': resultados['col_fin'][i]
                })
            
            page.update_table(tokens)
            page.snack_bar = ft.SnackBar(ft.Text("✅ Análise léxica concluída com sucesso!"))
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ Erro na análise: {str(e)}"))
        
        page.snack_bar.open = True
        page.update()

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.PopupMenuButton(
                        icon=ft.Icons.SAVE,
                        tooltip="Menu de Arquivo",
                        items=[
                            ft.PopupMenuItem(
                                text="Abrir Arquivo",
                                icon=ft.Icons.FILE_OPEN,
                                on_click=lambda _: file_picker.pick_files(
                                    allowed_extensions=["txt"],
                                    allow_multiple=False
                                )
                            ),
                            ft.PopupMenuItem(
                                text="Novo Arquivo",
                                icon=ft.Icons.NOTE_ADD,
                                on_click=lambda _: page.set_editor_content([""])
                            ),
                            ft.PopupMenuItem(
                                text="Salvar Como...",
                                icon=ft.Icons.SAVE_AS,
                                on_click=lambda _: save_file_picker.save_file(
                                    allowed_extensions=["txt"],
                                    file_name="sem_nome.txt"
                                )
                            ),
                        ]
                    ),
                    
                    ft.Container(expand=True),
                    
                    ft.IconButton(
                        icon=ft.Icons.PLAY_CIRCLE_FILL_OUTLINED,
                        icon_color="green",
                        tooltip="Executar análise léxica",
                        on_click=run_play_function,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        ]
    )

def table(page):
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Lexema")),
            ft.DataColumn(ft.Text("Token")),
            ft.DataColumn(ft.Text("Linha")),
            ft.DataColumn(ft.Text("Col Inicial")),
            ft.DataColumn(ft.Text("Col Final"))
        ],
        rows=[],
        visible=False
    )

    def update_table(results):
        data_table.rows.clear()
        
        for res in results:
            is_error = res['token'].lower().startswith('erro')
            
            data_table.rows.append(
                ft.DataRow(
                    color=ft.colors.RED_100 if is_error else None,
                    cells=[
                        ft.DataCell(ft.Text(res['lexema'], color=ft.colors.RED if is_error else None)),
                        ft.DataCell(ft.Text(res['token'], color=ft.colors.RED if is_error else None)),
                        ft.DataCell(ft.Text(str(res['linha']),color=ft.colors.RED if is_error else None)),
                        ft.DataCell(ft.Text(str(res['col_inicial']),color=ft.colors.RED if is_error else None)),
                        ft.DataCell(ft.Text(str(res['col_final']),color=ft.colors.RED if is_error else None)),
                    ]
                )
            )
        
        data_table.visible = True
        container.visible = True
        page.update()

    page.update_table = update_table
    
    container = ft.Container(
        visible=False,
        content=ft.Column(
            [
                ft.Text("Resultado do Analisador Léxico", size=18, weight=ft.FontWeight.BOLD),
                ft.ListView(
                    expand=True,
                    height=350,
                    controls=[data_table]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        alignment=ft.alignment.center,
        padding=10
    )
    return container

def editor(page, initial_content=None):
    initial_content = initial_content or [""]
    counter = len(initial_content)
    text_fields = []
    current_focus = 0

    def move_focus(direction):
        nonlocal current_focus
        new_index = current_focus + direction
        if 0 <= new_index < len(text_fields):
            text_fields[new_index].focus()
            current_focus = new_index
            page.update()

    def handle_keyboard(e: ft.KeyboardEvent):
        nonlocal current_focus, text_fields, counter
        if e.key == "Arrow Down":
            move_focus(1)
        elif e.key == "Arrow Up":
            move_focus(-1)
        elif e.key == "Backspace":
            if len(text_fields) > 1 and text_fields[current_focus].value == "":
                del text_fields[current_focus]
                del container.controls[current_focus]
                counter -= 1

                for i, row in enumerate(container.controls, start=1):
                    row.controls[0].content.value = str(i)
                new_focus = current_focus - 1 if current_focus > 0 else 0
                text_fields[new_focus].focus()
                current_focus = new_focus
                page.update()

    page.on_keyboard_event = handle_keyboard

    def add_row(e):
        nonlocal counter, current_focus
        counter += 1

        new_tf = ft.TextField(
            width=page.width * 0.95,
            on_submit=add_row,
            border_color=ft.colors.TRANSPARENT,
            text_size=12,
            content_padding=2,
            autofocus=True,
            dense=True,
        )

        text_fields.append(new_tf)

        new_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(f"{counter}", size=10),
                    width=page.width * 0.02,
                    alignment=ft.alignment.center,
                    padding=0,
                    margin=0,
                ),
                new_tf,
            ],
            spacing=0,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            height=25,
        )

        container.controls.append(new_row)
        current_focus = len(text_fields) - 1
        page.update()

    container = ft.Column(
        controls=[],
        spacing=0,
        tight=True,
        scroll=ft.ScrollMode.AUTO,
        height=500
    )

    for i, content in enumerate(initial_content, start=1):
        tf = ft.TextField(
            width=page.width * 0.95,
            border_color=ft.colors.TRANSPARENT,
            text_size=12,
            content_padding=2,
            dense=True,
            value=content
        )
        text_fields.append(tf)

        row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(f"{i}", size=10),
                    width=page.width * 0.02,
                    alignment=ft.alignment.center,
                    padding=0,
                    margin=0,
                ),
                tf,
            ],
            spacing=0,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            height=25,
        )
        container.controls.append(row)

    if text_fields:
        text_fields[-1].on_submit = add_row

    def get_content():
        return [tf.value for tf in text_fields]
    
    def set_content(new_content):
        nonlocal counter, text_fields, current_focus
        container.controls.clear()
        text_fields.clear()
        counter = len(new_content)
        current_focus = 0
        
        for i, content in enumerate(new_content, start=1):
            tf = ft.TextField(
                width=page.width * 0.95,
                border_color=ft.colors.TRANSPARENT,
                text_size=12,
                content_padding=2,
                dense=True,
                value=content
            )
            text_fields.append(tf)
            
            row = ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(f"{i}", size=10),
                        width=page.width * 0.02,
                        alignment=ft.alignment.center,
                        padding=0,
                        margin=0,
                    ),
                    tf,
                ],
                spacing=0,
                tight=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                height=25,
            )
            container.controls.append(row)

        if text_fields:
            text_fields[-1].on_submit = add_row
        page.update()

    page.set_editor_content = set_content
    page.get_editor_content = get_content

    return container

def main(page: ft.Page):
    page.title = "Compilador - Leonardo S. Coradeli e Marco V. M. Faria"
    page.window_width = 800
    page.window_height = 800

    menu_component = menu(page)
    editor_component = editor(page)
    table_component = table(page)

    page.add(
        ft.Column(
            controls=[
                menu_component,
                ft.Divider(),
                editor_component,
                ft.Divider(),
                table_component,
                ft.Text("Alfabeto: 0 a 9, real separado por ., +, -, *, /, (, ), [, ]", text_align=ft.TextAlign.CENTER),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )
    )

ft.app(target=main)