class MEPACodeGenerator:
    def __init__(self, symbol_tables):
        self.symbol_tables = symbol_tables
        self.code = []
        self.current_scope = "global"
        self.label_counter = 0
        self.code_address = 0
        self.scope_stack = ["global"]
        
    def _new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def _get_var_address(self, var_name):
        """Busca hierárquica: escopo atual -> global"""
        for scope_name in reversed(self.scope_stack):
            if scope_name in self.symbol_tables:
                for entry in self.symbol_tables[scope_name]:
                    if entry['Lexema'] == var_name:
                        return entry.get('Endereco', 0)
        return 0
    
    def _enter_scope(self, scope_name):
        self.scope_stack.append(scope_name)
        self.current_scope = scope_name
    
    def _exit_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
    
    def _parse_simple_expression(self, tokens, lexemas, start_idx):
        """Parser simplificado para expressões básicas"""
        i = start_idx
        operand_stack = []
        operator_stack = []
        
        
        operators = {
            'multiply': ('MULT', 6),
            'divide': ('DIVI', 6), 
            'plus': ('SOMA', 5),
            'minus': ('SUBT', 5),
            'lt': ('CMME', 4),
            'gt': ('CMMA', 4),
            'lte': ('CMEG', 4),
            'gte': ('CMAG', 4),
            'equals': ('CMIG', 3),
            'not_equals': ('CMDG', 3),
            'and': ('CONJ', 2),
            'or': ('DISJ', 1)
        }
        
        def apply_operator(op_token):
            if operand_stack:
                
                if len(operand_stack) >= 2:
                    right = operand_stack.pop()
                    left = operand_stack.pop()
                    
                    for instr in left:
                        self.code.append(instr)
                        self.code_address += 1
                    for instr in right:
                        self.code.append(instr)
                        self.code_address += 1
                    
                    op_code = operators[op_token][0]
                    self.code.append((op_code,))
                    self.code_address += 1
                    
                    operand_stack.append([])
        
        while i < len(tokens):
            token = tokens[i]
            lexema = lexemas[i]
            
            
            if token in ('semicolon', 'then', 'do', 'else', 'end', 'left_parenteses', 'comma'):
                break
                
            
            if token == 'identifier':
                addr = self._get_var_address(lexema)
                operand_stack.append([('CRVL', addr)])
            elif token in ('integer', 'real'):
                value = int(lexema) if token == 'integer' else float(lexema)
                operand_stack.append([('CRCT', value)])
            elif token in ('true', 'false'):
                value = 1 if token == 'true' else 0
                operand_stack.append([('CRCT', value)])
            
            
            elif token in operators:
                
                while (operator_stack and 
                       operator_stack[-1] in operators and
                       operators[operator_stack[-1]][1] >= operators[token][1]):
                    op = operator_stack.pop()
                    apply_operator(op)
                
                operator_stack.append(token)
            
            elif token == 'right_parenteses':
                pass  
            
            i += 1
        
        
        while operator_stack:
            op = operator_stack.pop()
            apply_operator(op)
        
        return i
    
    def _parse_assignment(self, tokens, lexemas, start_idx):
        """Processa atribuição: var := expressão"""
        var_name = lexemas[start_idx]
        i = start_idx + 2  
        
        
        i = self._parse_simple_expression(tokens, lexemas, i)
        
        
        addr = self._get_var_address(var_name)
        self.code.append(('ARMZ', addr))
        self.code_address += 1
        
        return i
    
    def _parse_if_statement(self, tokens, lexemas, start_idx):
        """Processa comando if-then-else"""
        i = start_idx + 1  
        
        
        i = self._parse_simple_expression(tokens, lexemas, i)
        
        
        false_label = self._new_label()
        end_label = self._new_label()
        
        self.code.append(('DSVF', false_label))
        self.code_address += 1
        
        
        if i < len(tokens) and tokens[i] == 'execute_conditional':
            i += 1
        
        
        i = self._parse_statement_block(tokens, lexemas, i)
        
        
        has_else = (i < len(tokens) and tokens[i] == 'otherwise_conditional')
        
        if has_else:
            self.code.append(('DSVS', end_label))
            self.code_address += 1
        
        
        self.code.append((false_label + ':',))
        self.code_address += 1
        
        if has_else:
            i += 1  
            i = self._parse_statement_block(tokens, lexemas, i)
            self.code.append((end_label + ':',))
            self.code_address += 1
        
        return i
    
    def _parse_while_statement(self, tokens, lexemas, start_idx):
        """Processa comando while-do"""
        start_label = self._new_label()
        end_label = self._new_label()
        
        
        self.code.append((start_label + ':',))
        self.code_address += 1
        
        i = start_idx + 1  
        
        
        i = self._parse_simple_expression(tokens, lexemas, i)
        
        self.code.append(('DSVF', end_label))
        self.code_address += 1
        
        
        if i < len(tokens) and tokens[i] == 'execute_loop':
            i += 1
        
        
        i = self._parse_statement_block(tokens, lexemas, i)
        
        
        self.code.append(('DSVS', start_label))
        self.code_address += 1
        self.code.append((end_label + ':',))
        self.code_address += 1
        
        return i
    
    def _parse_procedure_call(self, tokens, lexemas, start_idx):
        """Processa chamada de procedimento"""
        proc_name = lexemas[start_idx]
        i = start_idx + 1
        
        
        if i < len(tokens) and tokens[i] == 'right_parenteses':
            i += 1  
            
            
            while i < len(tokens) and tokens[i] != 'left_parenteses':
                if tokens[i] == 'identifier':
                    addr = self._get_var_address(lexemas[i])
                    self.code.append(('CRVL', addr))
                    self.code_address += 1
                elif tokens[i] == 'comma':
                    pass  
                i += 1
            
            i += 1  
        
        
        self.code.append(('CHPR', f'PROC_{proc_name}'))
        self.code_address += 1
        
        return i
    
    def _parse_io_statement(self, tokens, lexemas, start_idx):
        """Processa comandos read/write"""
        cmd = lexemas[start_idx]
        i = start_idx + 2  
        
        if cmd == 'read':
            if tokens[i] == 'identifier':
                addr = self._get_var_address(lexemas[i])
                self.code.append(('LEIT',))
                self.code.append(('ARMZ', addr))
                self.code_address += 2
                i += 1
        elif cmd == 'write':
            i = self._parse_simple_expression(tokens, lexemas, i)
            self.code.append(('IMPR',))
            self.code_address += 1
        
        
        if i < len(tokens) and tokens[i] == 'left_parenteses':
            i += 1
        
        return i
    
    def _parse_statement_block(self, tokens, lexemas, start_idx):
        """Processa um bloco de comandos (begin...end ou comando único)"""
        i = start_idx
        
        
        if i < len(tokens) and tokens[i] == 'start_command':
            i += 1  
            
            while i < len(tokens) and tokens[i] != 'end_command':
                i = self._parse_single_statement(tokens, lexemas, i)
                
                
                if i < len(tokens) and tokens[i] == 'semicolon':
                    i += 1
            
            
            if i < len(tokens) and tokens[i] == 'end_command':
                i += 1
        else:
            
            i = self._parse_single_statement(tokens, lexemas, i)
        
        return i
    
    def _parse_single_statement(self, tokens, lexemas, start_idx):
        """Processa um comando individual"""
        if start_idx >= len(tokens):
            return start_idx
            
        token = tokens[start_idx]
        lexema = lexemas[start_idx]
        
        
        if (token == 'identifier' and 
            start_idx + 1 < len(tokens) and 
            tokens[start_idx + 1] == 'assignment_operator'):
            return self._parse_assignment(tokens, lexemas, start_idx)
        
        
        elif token == 'conditional':
            return self._parse_if_statement(tokens, lexemas, start_idx)
        
        
        elif token == 'loop':
            return self._parse_while_statement(tokens, lexemas, start_idx)
        
        
        elif lexema in ('read', 'write'):
            return self._parse_io_statement(tokens, lexemas, start_idx)
        
        
        elif token == 'identifier':
            return self._parse_procedure_call(tokens, lexemas, start_idx)
        
        
        return start_idx + 1
    
    def generate(self, token_table):
        tokens = token_table['token']
        lexemas = token_table['lexema']
        
        
        self.code.append(('INPP',))
        self.code_address += 1
        
        
        if 'global' in self.symbol_tables:
            global_vars = [v for v in self.symbol_tables['global'] if v['Categoria'] == 'variavel']
            if global_vars:
                self.code.append(('AMEM', len(global_vars)))
                self.code_address += 1
                
                
                for idx, var in enumerate(global_vars):
                    for entry in self.symbol_tables['global']:
                        if entry['Lexema'] == var['Lexema']:
                            entry['Endereco'] = idx
        
        
        i = 0
        main_start = None
        
        while i < len(tokens):
            if tokens[i] == 'procedure':
                proc_name = lexemas[i + 1]
                
                
                skip_label = self._new_label()
                self.code.append(('DSVS', skip_label))
                self.code_address += 1
                
                
                self.code.append((f'PROC_{proc_name}:',))
                self.code_address += 1
                
                self._enter_scope(proc_name)
                
                
                if proc_name in self.symbol_tables:
                    local_vars = [v for v in self.symbol_tables[proc_name] 
                                 if v['Categoria'] in ('variavel', 'parametro')]
                    if local_vars:
                        self.code.append(('AMEM', len(local_vars)))
                        self.code_address += 1
                        
                        for idx, var in enumerate(local_vars):
                            for entry in self.symbol_tables[proc_name]:
                                if entry['Lexema'] == var['Lexema']:
                                    entry['Endereco'] = idx
                
                
                i += 2
                while i < len(tokens) and tokens[i] != 'start_command':
                    i += 1
                
                
                if i < len(tokens):
                    i = self._parse_statement_block(tokens, lexemas, i)
                
                
                if proc_name in self.symbol_tables:
                    local_vars = [v for v in self.symbol_tables[proc_name] 
                                 if v['Categoria'] in ('variavel', 'parametro')]
                    if local_vars:
                        self.code.append(('DMEM', len(local_vars)))
                        self.code_address += 1
                
                self.code.append(('RTPR',))
                self.code_address += 1
                
                
                self.code.append((skip_label + ':',))
                self.code_address += 1
                
                self._exit_scope()
            
            elif tokens[i] == 'start_command' and main_start is None:
                main_start = i
                break
            
            i += 1
        
        
        if main_start is not None:
            self._parse_statement_block(tokens, lexemas, main_start)
        
        
        self.code.append(('PARA',))
        
        return self.code
    
    def print_code(self):
        """Imprime o código MEPA gerado"""
        for instruction in self.code:
            if len(instruction) == 1:
                print(instruction[0])
            else:
                print(f"{instruction[0]:<10} {instruction[1]}")