tokens = {
    'program': r'\bprogram\b',
    'procedure': r'\bprocedure\b',
    'start_command': r'\bbegin\b',
    'end_command': r'\bend\b',
    'true': r'\btrue\b',
    'false': r'\bfalse\b',
    # 'read': r'\bread\b',  # REMOVIDO - 'read' será classificado como 'identifier'
    # 'write': r'\bwrite\b', # REMOVIDO - 'write' será classificado como 'identifier'
    'conditional': r'\bif\b',
    'execute_conditional': r'\bthen\b',
    'variable': r'\bvar\b',
    'otherwise_conditional': r'\belse\b',
    'loop': r'\bwhile\b',
    'execute_loop': r'\bdo\b',
    'not': r'\bnot\b',
    'and': r'\band\b',
    'or': r'\bor\b',
    'assignment_operator': r':=',
    'equals': r'=',
    'not_equals': r'<>',
    'lt': r'<',
    'lte': r'<=',
    'gt': r'>',
    'gte': r'>=',
    'plus': r'\+',
    'minus': r'-',
    'multiply': r'\*',
    'divide': r'\bdiv\b',  # Garante que 'div' é o token 'divide'
    'int': r'\bint\b',
    'boolean': r'\bboolean\b',
    'real': r'[0-9]+\.[0-9]+',
    # 'identifier' deve vir depois das palavras-chave para correta priorização
    'identifier': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', 
    'integer': r'\b[0-9]+\b',
    'right_parenteses': r'\(',
    'left_parenteses': r'\)',
    'comma': r'\,',
    'semicolon': r'\;',
    'colon': r'\:',
    'dot': r'\.',
    'comment_line': r'//.*?(?=\n|$)',
    'comment_block': r'\{.*?\}'
}

def obter_tokens():
    return tokens