from tabelas import get_table

class Grammar:
    def __init__(self):
        self.nonterminals = [
            'PDV', 'PDV′', 'DV', 'T', 'LI', 'LI′',
            'PDS', 'DP', 'PF_opt', 'PF', 'SPF_list', 'SPF_list′', 'SPF', 'I'
        ]
        self.terminals = [
            'boolean', 'int', 'identifier', 'procedure',
            'right_parenteses', 'left_parenteses', 'variable',
            'colon', 'semicolon', 'comma', '$'
        ]
        self.start_symbol = 'PDV'
        self.epsilon = 'ε'
        self.parse_table = get_table()
    
    
    def get_production(self, nonterminal: str, terminal: str):
        return self.parse_table.get((nonterminal, terminal))
    
    def is_terminal(self, symbol: str) -> bool:
        if symbol is None or symbol == self.epsilon or symbol == '':
            return False
        return symbol not in self.nonterminals

class ParseError(Exception):
    def __init__(self, message: str, position: int = None, expected=None, found: str = None, 
                 stack_top: str = None, input_line: str = None):
        super().__init__(message)
        self.position = position
        self.expected = expected
        self.found = found
        self.stack_top = stack_top
        self.input_line = input_line

class Parser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.stack = []
    
    def parse(self, tokens: list) -> bool:
        tokens = list(tokens)
        if not tokens or tokens[-1] != '$':
            tokens.append('$')
        self.stack = ['$']
        self.stack.append(self.grammar.start_symbol)
        index = 0
        input_line_str = " ".join(tokens)
        
        while self.stack:
            top = self.stack.pop()
            current_token = tokens[index] if index < len(tokens) else None
            
            if top == '$':
                if current_token == '$':
                    return True
                else:
                    message = f"Erro: entrada não consumida completamente. Restante: {tokens[index:]}."
                    raise ParseError(message, position=index, expected='fim da entrada', 
                                     found=current_token, stack_top=top, input_line=input_line_str)
            
            if self.grammar.is_terminal(top):
                if top == current_token:
                    index += 1
                    continue
                else:
                    message = (f"Erro de sintaxe na posição {index}: "
                               f"esperado token '{top}', mas encontrado '{current_token}'.")
                    raise ParseError(message, position=index, expected=top, 
                                     found=current_token, stack_top=top, input_line=input_line_str)
            
            else:
                production = self.grammar.get_production(top, current_token)
                if production is None:
                    expected_tokens = [term for (nt, term), prod in self.grammar.parse_table.items() if nt == top and term]
                    expected_list_str = ", ".join(f"'{tok}'" for tok in expected_tokens)
                    message = (f"Erro de sintaxe na posição {index}: "
                               f"No contexto de <{top}>, token inesperado '{current_token}'. "
                               f"Esperado um dos: {expected_list_str}.")
                    raise ParseError(message, position=index, expected=expected_tokens, 
                                     found=current_token, stack_top=top, input_line=input_line_str)
                for symbol in reversed(production):
                    if symbol == '' or symbol == self.grammar.epsilon:
                        continue
                    self.stack.append(symbol)

                continue
        
        if index < len(tokens):
            message = f"Erro: tokens restantes após análise: {tokens[index:]}."
            raise ParseError(message, position=index, expected=None, found=None, 
                             stack_top=None, input_line=input_line_str)
        return True
