class SyntacticAnalyzer:
    def __init__(self, parsing_table, follow_sets):
        self.table = parsing_table
        self.follow_sets = follow_sets
        known_non_terminals_from_table = {key[0] for key in self.table.keys()}
        known_non_terminals_from_follow = set(self.follow_sets.keys())
        self.non_terminals = known_non_terminals_from_table.union(known_non_terminals_from_follow)
        
        self.errors = []
        self.stack = []
        self.tokens = []
        self.index = 0

    def _get_follow_set(self, non_terminal):
        """Retorna o conjunto FOLLOW para um não-terminal ou um conjunto vazio se não definido."""
        return self.follow_sets.get(non_terminal, set())

    def parse(self, token_table):
        processed_tokens = []
        if not token_table or not token_table.get('token'):
            self.errors.append("Erro: Tabela de tokens de entrada inválida ou vazia.")
            return self.errors
            
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
                if stack_top != '$': 
                    self.errors.append(f"Erro: Fim inesperado do arquivo. Esperando por '{stack_top}' ou estrutura relacionada.")
                break 
                
            current_token = self.tokens[self.index]

            if stack_top in self.non_terminals:
                self._handle_non_terminal(stack_top, current_token)
            else:
                self._handle_terminal(stack_top, current_token)

        if self.stack and self.stack[-1] == '$' and self.tokens[self.index]['type'] == '$':
            pass
        elif not self.errors: 
            if self.stack and self.stack[-1] != '$':
                 self.errors.append(f"Erro: Fim inesperado do arquivo. Estrutura incompleta na pilha: {self.stack}")
            elif self.tokens[self.index]['type'] != '$':
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
        elif rule is False:
            self.stack.pop() 
        else:
            error_msg = f"Erro na linha {current_token['line']}: Token inesperado '{current_token['type']}' ('{current_token['value']}') durante a análise da estrutura '{stack_top}'."
            expected_tokens_from_table = [tk for (nt, tk), rl in self.table.items() if nt == stack_top and rl is not None]
            if expected_tokens_from_table:
                error_msg += f" Esperava-se um de: {', '.join(sorted(list(set(expected_tokens_from_table))))}."
            self.errors.append(error_msg)
            
            follow_set_for_stack_top = self._get_follow_set(stack_top)
            
            can_sync_on_current = current_token['type'] in follow_set_for_stack_top

            if can_sync_on_current:
                if self.stack and self.stack[-1] == stack_top:
                    self.stack.pop()
            else:
                self.index += 1 
                while self.index < len(self.tokens) and \
                      self.tokens[self.index]['type'] != '$' and \
                      self.tokens[self.index]['type'] not in follow_set_for_stack_top:
                    self.index += 1
                
                if self.stack and self.stack[-1] == stack_top:
                    self.stack.pop()