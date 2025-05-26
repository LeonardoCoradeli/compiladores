class SyntacticAnalyzer:
    def __init__(self, parsing_table):
        self.table = parsing_table
        self.non_terminals = {key[0] for key in self.table.keys()}
        self.errors = []
        self.stack = []
        self.tokens = []
        self.index = 0

    def parse(self, token_table):
        processed_tokens = []
        num_tokens = len(token_table['token'])
        for i in range(num_tokens):
            processed_tokens.append({
                'type': token_table['token'][i],
                'value': token_table['lexema'][i],
                'line': token_table['linha'][i]
            })
        
        self.tokens = processed_tokens
        self.stack = ['$', 'PG'] 
        self.index = 0
        self.errors = []
        
        last_line = self.tokens[-1]['line'] if self.tokens else 1
        self.tokens.append({'type': '$', 'value': 'EOF', 'line': last_line})

        while self.stack and self.stack[-1] != '$':
            stack_top = self.stack[-1]
            if self.index >= len(self.tokens):
                self.errors.append(f"Erro: Fim inesperado do arquivo. Esperando por '{stack_top}'.")
                break
                
            current_token = self.tokens[self.index]

            if stack_top in self.non_terminals:
                self._handle_non_terminal(stack_top, current_token)
            else:
                self._handle_terminal(stack_top, current_token)

        if not self.errors and self.stack[-1] == '$' and self.tokens[self.index]['type'] != '$':
             self.errors.append(f"Erro na linha {self.tokens[self.index]['line']}: Código extra encontrado ('{self.tokens[self.index]['value']}') após o final do programa.")

        return self.errors

    def _handle_terminal(self, stack_top, current_token):
        """Processa o caso em que o topo da pilha é um terminal."""
        if stack_top == current_token['type']:
            self.stack.pop()
            self.index += 1
        else:
            error_msg = f"Erro na linha {current_token['line']}: Era esperado o token '{stack_top}', mas foi encontrado '{current_token['type']}' ('{current_token['value']}')."
            self.errors.append(error_msg)
            self.stack.pop()

    def _handle_non_terminal(self, stack_top, current_token):
        key = (stack_top, current_token['type'])
        rule = self.table.get(key)

        if rule and rule != False:
            self.stack.pop()
            if rule != ['ε']:
                for symbol in reversed(rule):
                    self.stack.append(symbol)
        else:
            error_msg = f"Erro na linha {current_token['line']}: Token inesperado '{current_token['type']}' ('{current_token['value']}') durante a análise da estrutura '{stack_top}'."
            self.errors.append(error_msg)
            while self.table.get((stack_top, self.tokens[self.index]['type'])) is None:
                self.index += 1
                if self.tokens[self.index]['type'] == '$':
                    self.stack.clear()
                    self.stack.append('$')
                    return
            if self.table.get((stack_top, self.tokens[self.index]['type'])) is False:
                self.stack.pop()
