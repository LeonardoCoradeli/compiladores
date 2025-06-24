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