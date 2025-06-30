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

    def _get_friendly_token_name(self, token_type):
        """Converte nomes de tokens técnicos para nomes mais amigáveis."""
        token_map = {
            'program': 'palavra-chave "program"',
            'procedure': 'palavra-chave "procedure"',
            'start_command': 'palavra-chave "begin"',
            'end_command': 'palavra-chave "end"',
            'true': 'valor booleano "true"',
            'false': 'valor booleano "false"',
            'conditional': 'palavra-chave "if"',
            'execute_conditional': 'palavra-chave "then"',
            'otherwise_conditional': 'palavra-chave "else"',
            'variable': 'palavra-chave "var"',
            'loop': 'palavra-chave "while"',
            'execute_loop': 'palavra-chave "do"',
            'not': 'operador "not"',
            'and': 'operador "and"',
            'or': 'operador "or"',
            'assignment_operator': 'operador de atribuição ":="',
            'equals': 'operador de igualdade "="',
            'not_equals': 'operador de diferença "<>"',
            'lt': 'operador "menor que" "<"',
            'lte': 'operador "menor ou igual" "<="',
            'gt': 'operador "maior que" ">"',
            'gte': 'operador "maior ou igual" ">="',
            'plus': 'operador de soma "+"',
            'minus': 'operador de subtração "-"',
            'multiply': 'operador de multiplicação "*"',
            'divide': 'operador de divisão "div"',
            'int': 'tipo "int"',
            'boolean': 'tipo "boolean"',
            'real': 'número real',
            'identifier': 'identificador',
            'integer': 'número inteiro',
            'right_parenteses': 'parêntese de abertura "("',
            'left_parenteses': 'parêntese de fechamento ")"',
            'comma': 'vírgula ","',
            'semicolon': 'ponto e vírgula ";"',
            'colon': 'dois pontos ":"',
            'dot': 'ponto final "."',
            '$': 'fim do arquivo'
        }
        return token_map.get(token_type, f'"{token_type}"')

    def _get_friendly_non_terminal_name(self, non_terminal):
        """Converte nomes de não-terminais técnicos para descrições mais amigáveis."""
        non_terminal_map = {
            'PG': 'programa principal',
            'B': 'corpo do programa',
            'VAR_DECL_PART_OPT': 'declaração de variáveis',
            'VAR_DECL_STMT': 'declaração de variável',
            'TYPE': 'tipo de dado',
            'L_ID': 'lista de identificadores',
            'D_SUB_P_OPT': 'declaração de procedimentos',
            'D_PROC': 'declaração de procedimento',
            'P_FORM_OPT': 'parâmetros formais',
            'C_COMP': 'comando composto',
            'CMD_LIST': 'lista de comandos',
            'CMD': 'comando',
            'ID_CMD': 'comando de identificador',
            'C_COND': 'comando condicional',
            'C_REP': 'comando de repetição',
            'EXP': 'expressão',
            'TERM': 'termo',
            'FAT': 'fator',
            'VAR_ACCESS': 'acesso à variável'
        }
        return non_terminal_map.get(non_terminal, non_terminal.lower().replace('_', ' '))

    def parse(self, token_table):
        processed_tokens = []
        if not token_table or not token_table.get('token'):
            self.errors.append((1, "Erro: Nenhum código foi fornecido para análise."))
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
                    current_line = self.tokens[-1]['line'] if self.tokens else 1
                    friendly_structure = self._get_friendly_non_terminal_name(stack_top)
                    self.errors.append((current_line, f"Erro: O programa terminou inesperadamente. Era esperado continuar com {friendly_structure}."))
                break 

            if self.tokens[self.index]['type'] == 'comment_block':
                self.index += 1
                continue
                
            current_token = self.tokens[self.index]

            if stack_top in self.non_terminals:
                self._handle_non_terminal(stack_top, current_token)
            else:
                self._handle_terminal(stack_top, current_token)

        if self.stack and self.stack[-1] == '$' and self.tokens[self.index]['type'] == '$':
            pass
        elif not self.errors: 
            if self.stack and self.stack[-1] != '$':
                current_line = self.tokens[-1]['line'] if self.tokens else 1
                self.errors.append((current_line, f"Erro: O programa está incompleto. Verifique se todas as estruturas foram fechadas adequadamente."))
            elif self.tokens[self.index]['type'] != '$':
                self.errors.append((self.tokens[self.index]['line'], f"Erro: Código extra encontrado após o final do programa: '{self.tokens[self.index]['value']}'."))

        return self.errors

    def _handle_terminal(self, stack_top, current_token):
        """Processa o caso em que o topo da pilha é um terminal."""
        if stack_top == current_token['type']:
            self.stack.pop()
            self.index += 1
        else:
            expected_name = self._get_friendly_token_name(stack_top)
            found_name = self._get_friendly_token_name(current_token['type'])
            error_msg = f"Erro de sintaxe: Era esperado {expected_name}, mas foi encontrado {found_name}."
            self.errors.append((current_token['line'], error_msg))
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
      
            current_structure = self._get_friendly_non_terminal_name(stack_top)
            found_token = self._get_friendly_token_name(current_token['type'])
            

            expected_tokens_from_table = [tk for (nt, tk), rl in self.table.items() 
                                        if nt == stack_top and rl is not None and rl is not False]
            
            if expected_tokens_from_table:
                expected_friendly = [self._get_friendly_token_name(token) for token in expected_tokens_from_table]
                expected_list = sorted(list(set(expected_friendly)))
                
                if len(expected_list) == 1:
                    expected_text = expected_list[0]
                elif len(expected_list) == 2:
                    expected_text = f"{expected_list[0]} ou {expected_list[1]}"
                else:
                    expected_text = f"{', '.join(expected_list[:-1])} ou {expected_list[-1]}"
                
                error_msg = f"Erro de sintaxe: Token inesperado {found_token} em {current_structure}. Era esperado {expected_text}."
            else:
                error_msg = f"Erro de sintaxe: Token inesperado {found_token} em {current_structure}."
            
            self.errors.append((current_token['line'], error_msg))
            
           
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