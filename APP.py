import flet as ft
from analisador_lexico import analisador_lexico
import os
import re
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
    # Cria o texto inicial com cada linha formatada como "n| <conteúdo>"
    lines_with_numbers = [f"{i+1}| {line}" for i, line in enumerate(initial_content)]
    initial_text = "\n".join(lines_with_numbers)
    
    text_field = ft.TextField(
        value=initial_text,
        multiline=True,
        expand=True,
        border=ft.InputBorder.NONE,
        content_padding=ft.padding.all(5),
        height=500,
        text_size=12,
        # Sempre que o texto mudar, reprocessa a formatação
        on_change=lambda e: update_line_numbers()
    )
    
    def update_line_numbers():
        """
        Reinsere o número correto no início de cada linha.
        Se houver mais de uma linha e alguma estiver "vazia" (ou seja, só com o prefixo),
        essa linha será removida (permitindo que o usuário use o backspace para apagá-la).
        """
        # Divide o conteúdo atual em linhas
        raw_lines = text_field.value.split("\n")
        # Remove qualquer prefixo existente em cada linha
        content_lines = [re.sub(r"^\d+\|\s*", "", line) for line in raw_lines]
        
        # Se houver mais de uma linha e alguma estiver vazia, consideramos que o usuário deseja apagá-la
        if len(content_lines) > 1:
            content_lines = [line for line in content_lines if line != ""]
        
        # Reconstroi cada linha com seu número atualizado
        new_lines = [f"{i+1}| {line}" for i, line in enumerate(content_lines)]
        new_text = "\n".join(new_lines)
        
        # Atualiza o TextField somente se houver alteração para evitar loops
        if new_text != text_field.value:
            text_field.value = new_text
            text_field.update()
    
    def get_content_without_numbers():
        """
        Retorna o conteúdo do editor sem os números de linha.
        """
        lines = text_field.value.split("\n")
        return [re.sub(r"^\d+\|\s*", "", line) for line in lines]
    
    def set_content(new_content):
        """
        Define o conteúdo do editor, formatando cada linha com o número correspondente.
        """
        lines_with_numbers = [f"{i+1}| {line}" for i, line in enumerate(new_content)]
        text_field.value = "\n".join(lines_with_numbers)
        text_field.update()
    
    page.get_editor_content = get_content_without_numbers
    page.set_editor_content = set_content
    
    return text_field

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