import re

def analisador_lexico(string):

    tokens = {
        "left parenthesis": r"\(",
        "right parenthesis": r"\)",
        "left bracket": r"\[",
        "right bracket": r"\]",
        "left brace": r"\{",
        "right brace": r"\}",
        "real": r"\d+\.\d+|\d+\.\d*|\d*\.\d+",
        "integer": r"-?\d+",
        "addition operator": r"\+",
        "subtraction operator": r"\-",
        "multiplication operator": r"\*",
        "division operator": r"\/",
        
    }
    
    #"string": r'".*?"',
    #"equality operator": r"=",
    #"identifier": r"\b[a-zA-Z][a-zA-Z0-9_]*\b"

    table = {
        "lexema": [],
        "token": [],
        "linha": [],
        "col_ini": [],
        "col_fin": [],
        "erro": {
            "linha": [],
            "col_ini": [],
            "col_fin": []
        }
    }

    linhas = string.split("\n")

    for numero_linha, linha in enumerate(linhas, start=1):

        for match in re.finditer(r'\d+\.\d+|\d+\.\d*|\d*\.\d+|[a-zA-Z0-9_]+|[+\-/*=.]{1}|[(),\[\]\{\}]{1}', linha):
            lexema = match.group()
            print(lexema)
            col_ini = match.start() + 1
            col_fin = match.end()

            flag = 1
            for tipo_token, regex in tokens.items():
                if re.fullmatch(regex, lexema):
                    table['lexema'].append(lexema)
                    table['token'].append(tipo_token)
                    table['linha'].append(numero_linha)
                    table['col_ini'].append(col_ini)
                    table['col_fin'].append(col_fin)
                    flag = 0
                    break

            if flag:
                table['erro']['linha'].append(numero_linha)
                table['erro']['col_ini'].append(col_ini)
                table['erro']['col_fin'].append(col_fin)
                table['lexema'].append(lexema)
                table['token'].append("ERRO: Simbolo não pertence ao alfabeto.")
                table['linha'].append(numero_linha)
                table['col_ini'].append(col_ini)
                table['col_fin'].append(col_fin)

    return table