class MEPACodeGenerator:
    def __init__(self, symbol_tables):
        self.symbol_tables = symbol_tables
        self.code = []
        self.current_scope = "global"
        self.var_address_map = {}
        self.label_counter = 0
        self.code_address = 0
        self.scope_stack = ["global"]
        self.var_counter = 0
        self.operator_precedence = {
            'or': 1,
            'and': 2,
            'equals': 3, 'not_equals': 3,
            'lt': 4, 'gt': 4, 'lte': 4, 'gte': 4,
            'plus': 5, 'minus': 5,
            'multiply': 6, 'divide': 6,
            'not': 7
        }
        
    def _new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def _get_var_address(self, var_name):
        # Busca hierárquica: escopo atual -> global
        current_scopes = reversed(self.scope_stack)
        
        for scope_name in current_scopes:
            if scope_name in self.symbol_tables:
                for entry in self.symbol_tables[scope_name]:
                    if entry['Lexema'] == var_name:
                        return entry.get('Endereco', 0)
        
        # Se não encontrado, retorna 0 (endereço padrão)
        return 0
    
    def _enter_scope(self, scope_name):
        self.scope_stack.append(scope_name)
        self.current_scope = scope_name
    
    def _exit_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
    
    def _parse_expression(self, tokens, lexemas, start_index):
        # Define a lista de operadores binários
        binary_operators = {
            'plus': 'SOMA',
            'minus': 'SUBT',
            'multiply': 'MULT',
            'divide': 'DIVI',
            'lt': 'CMME',
            'gt': 'CMMA',
            'equals': 'CMIG',
            'not_equals': 'CMDG',
            'lte': 'CMEG',
            'gte': 'CMAG',
            'and': 'CONJ',
            'or': 'DISJ'
        }
        
        unary_operators = {
            'not': 'NEGA',
            'minus': 'INVR'
        }
        
        i = start_index
        stack = []
        
        while i < len(tokens) and tokens[i] not in (')', ';', 'then', 'do', 'else'):
            token = tokens[i]
            lexema = lexemas[i]
            
            # Identificador (variável)
            if token == 'identifier':
                address = self._get_var_address(lexema)
                self.code.append(('CRVL', address))
                self.code_address += 1
                stack.append('var')
            
            # Constante numérica
            elif token in ('integer', 'real'):
                value = int(lexema) if token == 'integer' else float(lexema)
                self.code.append(('CRCT', value))
                self.code_address += 1
                stack.append('const')
            
            # Valor booleano
            elif token in ('true', 'false'):
                value = 1 if token == 'true' else 0
                self.code.append(('CRCT', value))
                self.code_address += 1
                stack.append('const')
            
            # Operador unário
            elif token in unary_operators and (i == start_index or tokens[i-1] in ['(', '=', ','] + list(binary_operators.keys())):
                op_token = token
                i += 1
                
                # Processa o próximo elemento após o operador unário
                if i < len(tokens):
                    if tokens[i] == 'identifier':
                        address = self._get_var_address(lexemas[i])
                        self.code.append(('CRVL', address))
                        self.code_address += 1
                    elif tokens[i] in ('integer', 'real'):
                        value = int(lexemas[i]) if tokens[i] == 'integer' else float(lexemas[i])
                        self.code.append(('CRCT', value))
                        self.code_address += 1
                
                # Aplica operador unário
                self.code.append((unary_operators[op_token],))
                self.code_address += 1
            
            # Operador binário
            elif token in binary_operators:
                # Operações matemáticas exigem dois operandos na pilha
                if len(stack) >= 2:
                    self.code.append((binary_operators[token],))
                    self.code_address += 1
                    stack.pop()  # Remove um operando da pilha
                else:
                    # Trata caso de erro (operador sem operandos suficientes)
                    pass
            
            # Parênteses
            elif token == 'right_parenteses':
                # Abertura de parênteses - não precisa fazer nada especial
                pass
            elif token == 'left_parenteses':
                # Fechamento será tratado pela condição de saída
                pass
            
            i += 1
        
        return i
        
        # Processa a expressão (versão simplificada)
        for token, lexema in expr_tokens:
            if token == 'identifier':
                address = self._get_var_address(lexema)
                self.code.append(('CRVL', address))
                self.code_address += 1
            elif token == 'integer':
                self.code.append(('CRCT', int(lexema)))
                self.code_address += 1
            elif token == 'plus':
                self.code.append(('SOMA',))
                self.code_address += 1
            elif token == 'minus':
                self.code.append(('SUBT',))
                self.code_address += 1
            elif token == 'multiply':
                self.code.append(('MULT',))
                self.code_address += 1
            elif token == 'divide':
                self.code.append(('DIVI',))
                self.code_address += 1
            elif token == 'lt':
                self.code.append(('CMME',))
                self.code_address += 1
            elif token == 'gt':
                self.code.append(('CMMA',))
                self.code_address += 1
        
        return i  # Retorna o índice após a expressão
    
    def _parse_block(self, tokens, lexemas, start_index):
        i = start_index
        depth = 0
        if tokens[i] == 'start_command':  # 'begin'
            depth += 1
            i += 1
        
        while i < len(tokens) and depth > 0:
            token = tokens[i]
            lexema = lexemas[i]
            
            # Verifica fim de bloco
            if token == 'end_command':  # 'end'
                depth -= 1
                if depth == 0:
                    i += 1
                    break
            
            # Processa comandos dentro do bloco
            if token == 'identifier':
                # Atribuição
                if i+1 < len(tokens) and tokens[i+1] == 'assignment_operator':
                    var_name = lexema
                    i += 2  # Pula identificador e :=
                    i = self._parse_expression(tokens, lexemas, i)
                    address = self._get_var_address(var_name)
                    self.code.append(('ARMZ', address))
                    self.code_address += 1
                # Chamada de procedimento
                elif lexema == 'write':
                    i += 2  # Pula 'write('
                    while tokens[i] != 'right_parenteses':
                        if tokens[i] == 'identifier':
                            address = self._get_var_address(lexemas[i])
                            self.code.append(('CRVL', address))
                            self.code.append(('IMPR',))
                            self.code_address += 2
                        i += 1
                    self.code.append(('IMPE',))
                    self.code_address += 1
            # Comando if
            elif token == 'conditional':  # 'if'
                i += 1  # Pula 'if'
                i = self._parse_expression(tokens, lexemas, i)
                
                false_label = self._new_label()
                end_label = self._new_label()
                
                self.code.append(('DSVF', false_label))
                self.code_address += 1
                
                # Processa 'then'
                if tokens[i] == 'execute_conditional':  # 'then'
                    i += 1
                
                # Processa bloco then
                i = self._parse_block(tokens, lexemas, i)
                
                self.code.append(('DSVS', end_label))
                self.code_address += 1
                self.code.append((false_label + ':',))
                self.code_address += 1
                
                # Processa 'else' se existir
                if i < len(tokens) and tokens[i] == 'otherwise_conditional':  # 'else'
                    i += 1
                    i = self._parse_block(tokens, lexemas, i)
                
                self.code.append((end_label + ':',))
                self.code_address += 1
                continue
            
            # Comando while
            elif token == 'loop':  # 'while'
                start_label = self._new_label()
                end_label = self._new_label()
                
                self.code.append((start_label + ':',))
                self.code_address += 1
                
                i += 1  # Pula 'while'
                i = self._parse_expression(tokens, lexemas, i)
                
                self.code.append(('DSVF', end_label))
                self.code_address += 1
                
                # Processa 'do'
                if tokens[i] == 'execute_loop':  # 'do'
                    i += 1
                
                # Processa bloco do
                i = self._parse_block(tokens, lexemas, i)
                
                self.code.append(('DSVS', start_label))
                self.code_address += 1
                self.code.append((end_label + ':',))
                self.code_address += 1
                continue
            
            i += 1
        
        return i
    
    def generate(self, token_table):
        tokens = token_table['token']
        lexemas = token_table['lexema']
        linhas = token_table['linha']
        
        # Início do programa
        self.code.append(('INPP',))
        self.code_address += 1
        
        # Aloca memória para variáveis globais
        if 'global' in self.symbol_tables:
            global_vars = [v for v in self.symbol_tables['global'] if v['Categoria'] == 'variavel']
            if global_vars:
                self.code.append(('AMEM', len(global_vars)))
                self.code_address += 1
                
                # Mapeia endereços das variáveis
                for idx, var in enumerate(global_vars):
                    self.var_address_map[var['Lexema']] = idx
                    # Atualiza tabela de símbolos
                    for scope in self.symbol_tables.values():
                        for entry in scope:
                            if entry['Lexema'] == var['Lexema']:
                                entry['Endereco'] = idx
        
        # Processa tokens
        i = 0
        while i < len(tokens):
            token = tokens[i]
            lexema = lexemas[i]
            
            # Declaração de procedimento
            if token == 'procedure':
                proc_name = lexemas[i+1]
                self._enter_scope(proc_name)
                
                # Aloca memória para parâmetros/variáveis locais
                if proc_name in self.symbol_tables:
                    local_vars = [v for v in self.symbol_tables[proc_name] 
                                 if v['Categoria'] in ('variavel', 'parametro')]
                    if local_vars:
                        self.code.append(('AMEM', len(local_vars)))
                        self.code_address += 1
                        
                        # Mapeia endereços
                        base_address = len(self.var_address_map)
                        for idx, var in enumerate(local_vars):
                            address = base_address + idx
                            self.var_address_map[var['Lexema']] = address
                            # Atualiza tabela de símbolos
                            for entry in self.symbol_tables[proc_name]:
                                if entry['Lexema'] == var['Lexema']:
                                    entry['Endereco'] = address
                
                i += 2  # Pula 'procedure' e nome
            
            # Início de bloco principal
            elif token == 'start_command':  # 'begin'
                i = self._parse_block(tokens, lexemas, i)
                continue
            
            # Fim de procedimento
            elif token == 'end_command' and self.current_scope != "global":
                # Desaloca memória
                if self.current_scope in self.symbol_tables:
                    local_vars = [v for v in self.symbol_tables[self.current_scope] 
                                 if v['Categoria'] in ('variavel', 'parametro')]
                    if local_vars:
                        self.code.append(('DMEM', len(local_vars)))
                        self.code_address += 1
                
                self._exit_scope()
            
            i += 1
        
        # Fim do programa
        self.code.append(('PARA',))
        return self.code