derivacaoVariaveis = {
    ('PDV', 'bool'): ['DV', 'PDV′'],
    ('PDV', 'int'): ['DV', 'PDV′'],
    ('PDV′', 'semicolon'): ['semicolon', 'DV', 'PDV′'],
    ('PDV′', '$'): [],
    ('DV', 'bool'): ['T', 'LI'],
    ('DV', 'int'): ['T', 'LI'],
    ('DV', '$'): [],
    ('T', 'bool'): ['bool'],
    ('T', 'int'): ['int'],
    ('T', 'identifier'): ['sinc'],
    ('T', 'procedure'): ['sinc'],
    ('T', 'right_parenteses'): ['sinc'],
    ('T', 'left_parenteses'): ['sinc'],
    ('T', 'variable'): ['sinc'],
    ('T', 'colon'): ['sinc'],
    ('T', 'semicolon'): ['sinc'],
    ('T', 'comma'): ['sinc'],
    ('T', '$'): ['sinc'],
    ('LI', 'identifier'): ['I', 'LI′'],
    ('LI', 'semicolon'): ['sinc'],
    ('LI', 'comma'): ['sinc'],
    ('LI', '$'): ['sinc'],
    ('LI′', 'semicolon'): [],
    ('LI′', 'comma'): ['comma','identifier', 'LI′'],
    ('LI′', '$'): [],
    ('PDS', 'procedure'): ['DP', 'semicolon', 'PDS'],
    ('PDS', '$'): [],
    ('DP', 'procedure'): ['procedure', 'I', 'PF_opt', 'semicolon', 'B'],
    ('DP', 'semicolon'): ['sinc'],
    ('DP', '$'): ['sinc'],
    ('PF_opt', 'right_parenteses'): ['PF'],
    ('PF_opt', '$'): [],
    ('PF', 'right_parenteses'): ['right_parenteses', 'SPF_list', 'left_parenteses'],
    ('PF', 'semicolon'): ['sinc'],
    ('SPF_list', 'identifier'): ['SPF', 'SPF_list′'],
    ('SPF_list', 'right_parenteses'): ['SPF', 'SPF_list′'],
    ('SPF_list', 'semicolon'): ['SPF', 'SPF_list′'],
    ('SPF_list′', 'right_parenteses'): [],
    ('SPF_list′', 'semicolon'): ['SPF', 'SPF_list′'],
    ('SPF_list′', '$'): [],
    ('SPF', 'identifier'): ['LI', 'colon', 'I'],
    ('SPF', 'variable'): ['variable', 'LI', 'colon', 'I'],
    ('I', 'identifier'): ['identifier'],
    ('I', 'right_parenteses'): ['sinc'],
    ('I', 'left_parenteses'): ['sinc'],
    ('I', 'colon'): ['sinc'],
    ('I', 'semicolon'): ['sinc'],
    ('I', 'comma'): ['sinc'],
    ('I', '$'): ['sinc']
}

derivacaoVariaveis.update({
    # <programa> ::= program <identificador> ; <bloco> .
    ('PG', 'program'):    ['program',    'I', 'semicolon', 'B', 'dot'],

    # <bloco> ::= <parte_de_declarações_de_variáveis> <parte_de_declarações_de_subrotinas> <comando_composto>
    ('B',  'begin'):      ['PDV',        'PDS',      'C'],

    # <comando_composto> ::= begin <comando> <comando_composto′> end
    ('C',  'begin'):      ['begin',      'CM',       "C′", 'end'],
    ("C′", 'semicolon'):  ['semicolon',  'CM',       "C′"],
    ("C′", 'end'):        [],

    # (Opcional: <comando> e <comando′> se ainda não estiverem no dicionário)
    ('CM', 'identifier'): ['I',           "CM′"],
    ('CM', 'if'):         ['COND1'],
    ('CM', 'while'):      ['REP1'],
    ('CM', 'begin'):      ['C'],
    ("CM′",'semicolon'):  [],      # ε
    # …e assim por diante conforme suas abreviações internas
})

def get_table():
    """
    Retorna a tabela de derivação.
    """
    return derivacaoVariaveis