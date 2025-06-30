class MEPACodeGenerator:
    def __init__(self, symbol_tables):
        self.symbol_tables = symbol_tables
        self.code = []
        self.code_address = 0
        self.current_scope = "global"
        self.scope_stack = ["global"]
        self.label_counter = 0
        
        # Estruturas para Backpatching
        self.labels = {}
        self.backpatch_list = {}

    def _new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def _define_label(self, label):
        """Define o endereço de um rótulo e corrige todas as referências pendentes (DSVS, DSVF, CHPR)."""
        label_address = self.code_address
        self.labels[label] = label_address
        if label in self.backpatch_list:
            for instruction_address_to_patch in self.backpatch_list[label]:
                instruction = self.code[instruction_address_to_patch]
                self.code[instruction_address_to_patch] = (instruction[0], label_address)
            del self.backpatch_list[label]

    def _add_jump_instruction(self, instruction, label):
        """Adiciona uma instrução de salto/chamada com um placeholder para backpatching."""
        jump_address = self.labels.get(label)
        if jump_address is None:
            if label not in self.backpatch_list:
                self.backpatch_list[label] = []
            self.backpatch_list[label].append(self.code_address)
        
        self.code.append((instruction, jump_address))
        self.code_address += 1
    
    def _get_var_address(self, var_name):
        """Busca hierárquica por uma variável."""
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

    def _apply_operator(self, op_token, operand_stack, operators):
        """Aplica um operador aos operandos na pilha do gerador."""
        if op_token.startswith('unary_'):
            op = op_token.split('_')[1]
            if op == 'minus' and len(operand_stack) >= 1:
                right = operand_stack.pop()
                left = [('CRCT', 0)]
                for instr in left: self.code.append(instr); self.code_address += 1
                for instr in right: self.code.append(instr); self.code_address += 1
                self.code.append(('SUBT',))
                self.code_address += 1
                operand_stack.append([])
            return
        
        if len(operand_stack) >= 2:
            right = operand_stack.pop()
            left = operand_stack.pop()
            for instr in left: self.code.append(instr); self.code_address += 1
            for instr in right: self.code.append(instr); self.code_address += 1
            op_code = operators[op_token][0]
            self.code.append((op_code,))
            self.code_address += 1
            operand_stack.append([])

    def _parse_simple_expression(self, tokens, lexemas, start_idx):
        """Parser de expressões com suporte a operadores unários e parênteses."""
        i = start_idx
        operand_stack = []
        operator_stack = []
        
        operators = {
            'multiply': ('MULT', 6), 'divide': ('DIVI', 6), 'plus': ('SOMA', 5),
            'minus': ('SUBT', 5), 'lt': ('CMME', 4), 'gt': ('CMMA', 4),
            'lte': ('CMEG', 4), 'gte': ('CMAG', 4), 'equals': ('CMIG', 3),
            'not_equals': ('CMDG', 3), 'and': ('CONJ', 2), 'or': ('DISJ', 1),
            'unary_plus': ('NOOP', 7), 'unary_minus': ('NEGA', 7)
        }
        
        prev_token_is_operand = False
        while i < len(tokens):
            token = tokens[i]
            
            if token in ('semicolon', 'execute_conditional', 'execute_loop', 'otherwise_conditional', 'end_command', 'comma', 'left_parenteses'):
                break
            
            if token == 'identifier':
                addr = self._get_var_address(lexemas[i])
                operand_stack.append([('CRVL', addr)])
                prev_token_is_operand = True
            elif token in ('integer', 'real'):
                value = int(lexemas[i]) if token == 'integer' else float(lexemas[i])
                operand_stack.append([('CRCT', value)])
                prev_token_is_operand = True
            elif token in ('true', 'false'):
                value = 1 if token == 'true' else 0
                operand_stack.append([('CRCT', value)])
                prev_token_is_operand = True
            elif token in ('plus', 'minus') and not prev_token_is_operand:
                operator_stack.append('unary_' + token)
                prev_token_is_operand = False
            elif token in operators:
                while (operator_stack and operator_stack[-1] != 'right_parenteses' and
                       operators.get(operator_stack[-1], (None, 0))[1] >= operators[token][1]):
                    self._apply_operator(operator_stack.pop(), operand_stack, operators)
                operator_stack.append(token)
                prev_token_is_operand = False
            elif token == 'right_parenteses': # Token para '('
                operator_stack.append(token)
                prev_token_is_operand = False

            i += 1
        
        while operator_stack:
            op = operator_stack.pop()
            if op == 'right_parenteses':
                 raise Exception("Erro de Geração: Parênteses desbalanceados na expressão (falta ')').")
            self._apply_operator(op, operand_stack, operators)
        
        if operand_stack:
            final_code = operand_stack.pop()
            for instr in final_code:
                self.code.append(instr)
                self.code_address += 1
        return i
    
    def _parse_assignment(self, tokens, lexemas, start_idx):
        var_name = lexemas[start_idx]
        i = self._parse_simple_expression(tokens, lexemas, start_idx + 2)
        addr = self._get_var_address(var_name)
        self.code.append(('ARMZ', addr))
        self.code_address += 1
        return i
    
    def _parse_if_statement(self, tokens, lexemas, start_idx):
        i = start_idx + 1 # Pula 'if'
        if i < len(tokens) and tokens[i] == 'right_parenteses': i += 1 # Consome '('
        i = self._parse_simple_expression(tokens, lexemas, i)
        if i < len(tokens) and tokens[i] == 'left_parenteses': i += 1 # Consome ')'
            
        false_label = self._new_label()
        end_label = self._new_label()
        
        self._add_jump_instruction('DSVF', false_label)
        
        if i < len(tokens) and tokens[i] == 'execute_conditional': i += 1 # Consome 'then'
        i = self._parse_statement_block(tokens, lexemas, i)
        
        if i < len(tokens) and tokens[i] == 'otherwise_conditional': # Se existe um 'else'
            self._add_jump_instruction('DSVS', end_label)
            self._define_label(false_label)
            i += 1 # Consome 'else'
            i = self._parse_statement_block(tokens, lexemas, i)
            self._define_label(end_label)
        else: # Se não há 'else'
            self._define_label(false_label)
        
        return i
    
    def _parse_while_statement(self, tokens, lexemas, start_idx):
        start_label = self._new_label()
        end_label = self._new_label()
        
        self._define_label(start_label)
        i = start_idx + 1 # Pula 'while'
        if i < len(tokens) and tokens[i] == 'right_parenteses': i += 1 # Consome '('
        i = self._parse_simple_expression(tokens, lexemas, i)
        if i < len(tokens) and tokens[i] == 'left_parenteses': i += 1 # Consome ')'
        
        self._add_jump_instruction('DSVF', end_label)
        
        if i < len(tokens) and tokens[i] == 'execute_loop': i += 1 # Consome 'do'
        i = self._parse_statement_block(tokens, lexemas, i)
        self._add_jump_instruction('DSVS', start_label)
        self._define_label(end_label)
        return i

    # --- CORRIGIDO ---
    def _parse_procedure_call(self, tokens, lexemas, start_idx):
        proc_name = lexemas[start_idx]
        proc_label = f'PROC_{proc_name}' # Rótulo para o backpatching
        i = start_idx + 1
        
        if i < len(tokens) and tokens[i] == 'right_parenteses': # Consome '('
            i += 1
            while i < len(tokens) and tokens[i] != 'left_parenteses':
                i = self._parse_simple_expression(tokens, lexemas, i)
                if i < len(tokens) and tokens[i] == 'comma':
                    i += 1
                else:
                    break
            if i < len(tokens) and tokens[i] == 'left_parenteses': # Consome ')'
                i += 1
        
        # Usa o sistema de backpatching para a chamada
        self._add_jump_instruction('CHPR', proc_label)
        return i

    def _parse_io_statement(self, tokens, lexemas, start_idx):
        cmd = lexemas[start_idx]
        i = start_idx + 1
        
        if i < len(tokens) and tokens[i] == 'right_parenteses': i += 1 # Consome '('
        
        if cmd == 'read':
            if i < len(tokens) and tokens[i] == 'identifier':
                addr = self._get_var_address(lexemas[i])
                self.code.append(('LEIT',))
                self.code.append(('ARMZ', addr))
                self.code_address += 2
                i += 1
        elif cmd == 'write':
            i = self._parse_simple_expression(tokens, lexemas, i)
            self.code.append(('IMPR',))
            self.code_address += 1
        
        if i < len(tokens) and tokens[i] == 'left_parenteses': i += 1 # Consome ')'
        return i
    
    def _parse_statement_block(self, tokens, lexemas, start_idx):
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
        if start_idx >= len(tokens): return start_idx
        
        token = tokens[start_idx]
        if (token == 'identifier' and 
            start_idx + 1 < len(tokens) and 
            tokens[start_idx + 1] == 'assignment_operator'):
            return self._parse_assignment(tokens, lexemas, start_idx)
        elif token == 'conditional':
            return self._parse_if_statement(tokens, lexemas, start_idx)
        elif token == 'loop':
            return self._parse_while_statement(tokens, lexemas, start_idx)
        elif lexemas[start_idx] in ('read', 'write'):
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
        
        main_program_label = self._new_label()
        self._add_jump_instruction('DSVS', main_program_label)
        
        last_parsed_index = 0
        while True:
            try:
                proc_start_idx = tokens.index('procedure', last_parsed_index)
                proc_name = lexemas[proc_start_idx + 1]
                proc_label = f'PROC_{proc_name}'
                
                # --- CORRIGIDO: Define o rótulo do procedimento para resolver chamadas pendentes ---
                self._define_label(proc_label)
                
                self._enter_scope(proc_name)
                
                if proc_name in self.symbol_tables:
                    local_vars = [v for v in self.symbol_tables[proc_name] if v['Categoria'] in ('variavel', 'parametro')]
                    if local_vars:
                        self.code.append(('AMEM', len(local_vars)))
                        self.code_address += 1
                        for idx, var in enumerate(local_vars):
                            for entry in self.symbol_tables[proc_name]:
                                if entry['Lexema'] == var['Lexema']: entry['Endereco'] = idx

                body_start_idx = tokens.index('start_command', proc_start_idx)
                end_of_body_idx = self._parse_statement_block(tokens, lexemas, body_start_idx)

                if proc_name in self.symbol_tables:
                    local_vars = [v for v in self.symbol_tables[proc_name] if v['Categoria'] in ('variavel', 'parametro')]
                    if local_vars:
                        self.code.append(('DMEM', len(local_vars)))
                        self.code_address += 1
                
                self.code.append(('RTPR',))
                self.code_address += 1
                self._exit_scope()
                last_parsed_index = end_of_body_idx
            except ValueError:
                break

        self._define_label(main_program_label)
        
        try:
            main_start_idx = tokens.index('start_command', last_parsed_index)
            self._parse_statement_block(tokens, lexemas, main_start_idx)
        except ValueError:
            pass
        
        self.code.append(('PARA',))
        self.code_address += 1
        
        if self.backpatch_list:
            raise Exception(f"Erro de Geração: Rótulos de backpatching não resolvidos: {self.backpatch_list}")

        return self.code

    def print_code(self):
        """Imprime o código MEPA gerado de forma legível."""
        for i, instruction in enumerate(self.code):
            line = f"{i: >3}: "
            if len(instruction) == 1:
                if isinstance(instruction[0], str) and instruction[0].endswith(':'):
                    print(f"\n{instruction[0]}")
                else:
                    print(line + instruction[0])
            elif len(instruction) == 2:
                arg = instruction[1] if instruction[1] is not None else "???"
                print(f"{line}{instruction[0]:<10} {arg}")
