import re
from alfabeto import tokens
import string

class AnaliseLexica:
    def __init__(self, tokens):
        self.table = {
            "lexema": [],
            "token": [],
            "linha": [],
            "col_ini": [],
            "col_fin": [],
            "erro": {
                "erro": [],
                "linha": [],
                "col_ini": [],
                "col_fin": []
            }
        }
        self.tokens = tokens
        self.pattern = self.create_regex_pattern()

    def get_line_number(self, text, pos):
        return text[:pos].count('\n') + 1

    def create_regex_pattern(self):
        token_patterns = []
        for token_name, regex in self.tokens.items():
            token_patterns.append(f'(?P<{token_name}>{regex})')
        combined_regex = '|'.join(token_patterns)
        return re.compile(combined_regex, re.DOTALL | re.MULTILINE)

    def tokenize(self, text):
        resultados = []
        posicao_absoluta = 0
        linha_atual = 1
        coluna_inicial_linha_anterior = 0

        while posicao_absoluta < len(text):
            match = re.search(self.pattern, text[posicao_absoluta:])
            if match:
                for token_name, value in match.groupdict().items():
                    if value is not None:
                        start_abs = posicao_absoluta + match.start()
                        end_abs = posicao_absoluta + match.end()

                        linha_inicial = text[:start_abs].count('\n') + 1
                        coluna_inicial = start_abs - (text.rfind('\n', 0, start_abs) + 1) if text.rfind('\n', 0, start_abs) != -1 else start_abs + 1

                        linha_final = text[:end_abs].count('\n') + 1
                        coluna_final = end_abs - (text.rfind('\n', 0, end_abs) + 1) if text.rfind('\n', 0, end_abs) != -1 else end_abs

                        self.table["lexema"].append(value)
                        self.table["token"].append(token_name)
                        self.table["linha"].append(linha_inicial)
                        self.table["col_ini"].append(coluna_inicial)
                        self.table["col_fin"].append(coluna_final)
                        posicao_absoluta = end_abs
                        break
            else:
                break

    def verify_error(self, text):
        covered = set()
        for i in range(len(self.table["lexema"])):
            start_abs = 0
            for j in range(i):
                match = re.search(self.pattern, text[start_abs:])
                if match:
                    for token_name, value in match.groupdict().items():
                        if value is not None:
                            start_abs += match.start()
                            break
                    start_abs += len(self.table["lexema"][j])
                else:
                    break

            match = re.search(self.pattern, text[start_abs:])
            if match:
                lexema = self.table["lexema"][i]
                start = start_abs + match.start()
                end = start + len(lexema)
                for k in range(start, end):
                    covered.add(k)

        for i, char in enumerate(text):
            if i not in covered and not char.isspace():
                linha = self.get_line_number(text, i)
                col_ini = i - (text.rfind('\n', 0, i) + 1) if text.rfind('\n', 0, i) != -1 else i + 1
                self.table["erro"]["erro"].append(f"Caractere inválido: '{char}'")
                self.table["erro"]["linha"].append(linha)
                self.table["erro"]["col_ini"].append(col_ini)
                self.table["erro"]["col_fin"].append(col_ini)

    def remove_empty_lines(self, text):
        return re.sub(r'^\s*$', '', text, flags=re.MULTILINE)

    def create_table(self, text):
        cleaned = self.remove_empty_lines(text)
        self.tokenize(cleaned)
        self.verify_error(cleaned)
