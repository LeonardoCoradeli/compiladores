class TabelaSimbolos:
    def __init__(self):
        self.escopos = [{}]
        self.escopo_atual = 0
        self.escopo_nomes = {0: 'global'}
        self.proximo_escopo_id = 1
        # Pré-declarar built-ins se desejado
        # self.declarar_global('read', 'n/a', 'builtin')
        # self.declarar_global('write', 'n/a', 'builtin')

    def entrar_escopo(self, nome_escopo='anonimo'):
        self.escopos.append({})
        self.escopo_atual += 1
        self.escopo_nomes[self.escopo_atual] = f"{nome_escopo}_{self.proximo_escopo_id}"
        self.proximo_escopo_id += 1

    def sair_escopo(self):
        if self.escopo_atual > 0:
            self.escopos.pop()
            self.escopo_atual -= 1

    def declarar(self, nome, tipo, categoria, linha=None):
        escopo = self.escopos[self.escopo_atual]
        if nome in escopo:
            raise ErroSemantico(f"Símbolo '{nome}' já declarado neste escopo.", linha)
        escopo[nome] = {
            'lexema': nome,
            'token': 'identifier',
            'categoria': categoria,
            'tipo': tipo,
            'valor': None,
            'escopo': self.escopo_nomes[self.escopo_atual],
            'utilizada': False,
            'linha': linha
        }

    def declarar_global(self, nome, tipo, categoria, linha=None):
        saved = self.escopo_atual
        self.escopo_atual = 0
        self.declarar(nome, tipo, categoria, linha)
        self.escopo_atual = saved

    def buscar(self, nome):
        for i in range(self.escopo_atual, -1, -1):
            if nome in self.escopos[i]:
                return self.escopos[i][nome]
        return None

    def marcar_utilizada(self, nome):
        simbolo = self.buscar(nome)
        if simbolo:
            simbolo['utilizada'] = True

    def atualizar_valor(self, nome, valor):
        simbolo = self.buscar(nome)
        if simbolo:
            simbolo['valor'] = valor

    def obter_tabela_formatada(self):
        tabela = []
        for escopo in self.escopos:
            for attrs in escopo.values():
                tabela.append({
                    'Lexema': attrs['lexema'],
                    'Token': attrs['token'],
                    'Categoria': attrs['categoria'],
                    'Tipo': attrs['tipo'],
                    'Valor': attrs['valor'],
                    'Escopo': attrs['escopo'],
                    'Utilizada': attrs['utilizada']
                })
        return tabela

class ErroSemantico(Exception):
    def __init__(self, mensagem, linha=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.linha = linha

class AnalisadorSemantico:
    def __init__(self):
        self.tabela = TabelaSimbolos()
        self.erros = []
        # pré-declarar procedimentos e funções internas
        self.tabela.declarar_global('read', 'n/a', 'builtin')
        self.tabela.declarar_global('write', 'n/a', 'builtin')
        self.tipos_compativel = {
            'int': {'int'},
            'real': {'int', 'real'},
            'boolean': {'boolean'}
        }

    def erro(self, mensagem, linha=None):
        self.erros.append(ErroSemantico(mensagem, linha))

    def verificar_tipo(self, dest, orig):
        return orig in self.tipos_compativel.get(dest, set())

    def analisar_tokens(self, token_table):
        self.erros.clear()
        self.tabela = TabelaSimbolos()
        # re-declarar built-ins após reset
        self.tabela.declarar_global('read', 'n/a', 'builtin')
        self.tabela.declarar_global('write', 'n/a', 'builtin')

        tokens = token_table['token']
        lexemas = token_table['lexema']
        linhas = token_table['linha']

        i = 0
        # declarar programa
        if i < len(tokens) and tokens[i] == 'program' and i+1 < len(tokens) and tokens[i+1] == 'identifier':
            nome_prog = lexemas[i+1]
            self.tabela.declarar_global(nome_prog, 'n/a', 'programa', linhas[i+1])
            i += 2
        # laço principal
        while i < len(tokens):
            tok = tokens[i]
            # declaração de procedimento
            if tok == 'procedure' and i+1 < len(tokens) and tokens[i+1] == 'identifier':
                nome_proc = lexemas[i+1]
                self.tabela.declarar_global(nome_proc, 'n/a', 'procedimento', linhas[i+1])
                self.tabela.entrar_escopo(nome_proc)
                i += 2
                # parâmetros formais
                if i < len(tokens) and tokens[i] == 'variable':
                    i += 1
                    while i < len(tokens) and tokens[i] != 'right_parenteses':
                        if tokens[i] == 'identifier' and i+2 < len(tokens) and tokens[i+1] == 'colon':
                            nome_par = lexemas[i]
                            tipo_par = tokens[i+2]
                            self._declarar_variavel(nome_par, tipo_par, linhas[i])
                            i += 3
                            continue
                        i += 1
                # avançar até fim da declaração;
                while i < len(tokens) and tokens[i] != 'semicolon': i += 1
                i += 1
                continue
            # fim de escopo em 'end' (exceto final programa)
            if tok == 'end_command':
                if not (i+1 < len(tokens) and tokens[i+1] == 'dot'):
                    self.tabela.sair_escopo()
                i += 1
                continue
            # declaração de variáveis
            if tok in ('int', 'real', 'boolean'):
                tipo_atual = tok
                i += 1
                if i < len(tokens) and tokens[i] == 'colon':
                    i += 1
                while i < len(tokens) and tokens[i] != 'semicolon':
                    if tokens[i] == 'identifier':
                        self._declarar_variavel(lexemas[i], tipo_atual, linhas[i])
                    i += 1
                i += 1
                continue
            # uso de identificador ou chamada
            if tok == 'identifier':
                nome = lexemas[i]
                simbolo = self.tabela.buscar(nome)
                if not simbolo:
                    self.erro(f"Símbolo '{nome}' não foi declarado.", linhas[i])
                else:
                    self.tabela.marcar_utilizada(nome)
                    # atribuição
                    if i+1 < len(tokens) and tokens[i+1] == 'assignment_operator':
                        i += 2
                        val, tipo_val, new_i = self._analisar_expressao(tokens, lexemas, linhas, i)
                        i = new_i
                        if simbolo and tipo_val is not None:
                            if not self.verificar_tipo(simbolo['tipo'], tipo_val):
                                self.erro(f"Tipo incompatível: atribuir '{tipo_val}' em '{simbolo['tipo']}'.", linhas[i-1])
                            else:
                                self.tabela.atualizar_valor(nome, val)
                        continue
            i += 1

        # avisos de não utilização
        for entry in self.tabela.obter_tabela_formatada():
            if entry['Categoria'] == 'variavel' and not entry['Utilizada']:
                self.erro(f"Aviso: Variável '{entry['Lexema']}' declarada mas não usada.", None)

        return self.erros, self.tabela.obter_tabela_formatada()

    def _declarar_variavel(self, nome, tipo, linha):
        try:
            self.tabela.declarar(nome, tipo, 'variavel', linha)
        except ErroSemantico as e:
            self.erro(e.mensagem, linha)

    def _analisar_expressao(self, tokens, lexemas, linhas, i):
        if i >= len(tokens): return None, None, i
        tok, lex = tokens[i], lexemas[i]
        if tok == 'integer': return int(lex), 'int', i+1
        if tok == 'real': return float(lex), 'real', i+1
        if tok == 'true': return True, 'boolean', i+1
        if tok == 'false': return False, 'boolean', i+1
        if tok == 'identifier':
            sym = self.tabela.buscar(lex)
            if sym:
                self.tabela.marcar_utilizada(lex)
                return sym['valor'], sym['tipo'], i+1
            else:
                self.erro(f"Símbolo '{lex}' não declarado.", linhas[i])
                return None, None, i+1
        return None, None, i+1

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
            # Gerar mensagem de erro mais amigável
            current_structure = self._get_friendly_non_terminal_name(stack_top)
            found_token = self._get_friendly_token_name(current_token['type'])
            
            # Buscar tokens esperados
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
            
            # Recuperação de erro usando conjunto FOLLOW
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


class AnalisadorIntegrado:
    """Classe que integra análise sintática e semântica"""
    
    def __init__(self, parsing_table, follow_sets):
        self.analisador_sintatico = SyntacticAnalyzer(parsing_table, follow_sets)
        self.analisador_semantico = AnalisadorSemantico()
    
    def analisar(self, token_table):
        """Executa análise sintática seguida de análise semântica"""
        print("=== INICIANDO ANÁLISE SINTÁTICA ===")
        erros_sintaticos = self.analisador_sintatico.parse(token_table)
        
        if erros_sintaticos:
            print("ERROS SINTÁTICOS ENCONTRADOS:")
            for linha, erro in erros_sintaticos:
                print(f"  Linha {linha}: {erro}")
            print("\n⚠️  Análise semântica não será executada devido a erros sintáticos.")
            return {
                'sintaxe': erros_sintaticos,
                'semantica': [],
                'tabela_simbolos': [],
                'sucesso': False
            }
        else:
            print("✅ Análise sintática concluída com sucesso!")
        
        print("\n=== INICIANDO ANÁLISE SEMÂNTICA ===")
        erros_semanticos, tabela_simbolos = self.analisador_semantico.analisar_tokens(token_table)
        
        if erros_semanticos:
            print("ERROS SEMÂNTICOS ENCONTRADOS:")
            for erro in erros_semanticos:
                linha_info = f" (linha {erro.linha})" if erro.linha else ""
                print(f"  {erro.mensagem}{linha_info}")
        else:
            print("✅ Análise semântica concluída com sucesso!")
        
        num_erros_reais = len([e for e in erros_semanticos if "Aviso:" not in e.mensagem])
        sucesso = len(erros_sintaticos) == 0 and num_erros_reais == 0
        
        if sucesso:
            print("\n🎉 ANÁLISE COMPLETA: Código válido sintaticamente e semanticamente!")
        else:
            if num_erros_reais > 0:
                print(f"\n❌ ANÁLISE COMPLETA: Encontrados {len(erros_sintaticos)} erros sintáticos e {num_erros_reais} erros semânticos.")
            else:
                print("\n🎉 ANÁLISE COMPLETA: Código válido, mas com avisos semânticos.")

        return {
            'sintaxe': erros_sintaticos,
            'semantica': erros_semanticos,
            'tabela_simbolos': tabela_simbolos,
            'sucesso': sucesso
        }