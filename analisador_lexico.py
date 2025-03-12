import re

def get_line_number(text, pos):
    return text[:pos].count('\n') + 1

def analisador_lexico(text):
    tokens = {
        "comment": r"\/\/.*\n",
        "comment block": r"\{.*(?:\}|\n.*|\n.*\})",
        "left parenthesis": r"\(",
        "right parenthesis": r"\)",
        "left bracket": r"\[",
        "right bracket": r"\]",
        "real": r"\d+\.\d+|\d+\.\d*|\d*\.\d+",
        "integer": r"-?\d+",
        "addition operator": r"\+",
        "subtraction operator": r"\-",
        "multiplication operator": r"\*",
        "division operator": r"\/",
    }
    
    padrao = re.compile(r'\d+\.\d+|\d+\.\d*|\d*\.\d+|\/\/.*\n|\{.*(?:\}|\n.*|\n.*\})|[a-zA-Z0-9_]+|[+\-/*=.]{1}|[(),\[\]\{\}]{1}', re.DOTALL)
    
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
    
    for match in padrao.finditer(text):
        lexema = match.group()
        inicio = match.start()
        fim = match.end()
        linha = get_line_number(text, inicio)
        ultima_quebra = text.rfind('\n', 0, inicio)
        col_ini = inicio - ultima_quebra if ultima_quebra != -1 else inicio + 1
        col_fin = col_ini + (fim - inicio)
        
        flag = True
        for tipo_token, regex in tokens.items():
            if re.fullmatch(regex, lexema, re.DOTALL):
                table['lexema'].append(lexema)
                table['token'].append(tipo_token)
                table['linha'].append(linha)
                table['col_ini'].append(col_ini)
                table['col_fin'].append(col_fin)
                flag = False
                break
        
        if flag:
            table['erro']['linha'].append(linha)
            table['erro']['col_ini'].append(col_ini)
            table['erro']['col_fin'].append(col_fin)
            table['lexema'].append(lexema)
            table['token'].append("ERRO: Símbolo não pertence ao alfabeto.")
            table['linha'].append(linha)
            table['col_ini'].append(col_ini)
            table['col_fin'].append(col_fin)
    
    return table

texto = '''// comentário de uma linha
{ comentário
multilinha }
('''
print(analisador_lexico(texto))
