class TabelaSimbolos:
    def __init__(self):
        self.escopos = [{}]  # Pilha de escopos ativos
        self.nomes = ['global']   # Pilha de nomes de escopos ativos
        
        # NOVO: Histórico de todos os escopos já criados, com seus nomes.
        # Ele é uma lista de tuplas: (nome_do_escopo, dicionario_de_simbolos)
        self.historico = [(self.nomes[0], self.escopos[0])]

    def entrar_escopo(self, nome):
        """
        Cria um novo escopo, o adiciona à pilha de escopos ativos
        e também o registra permanentemente no histórico.
        """
        novo_dict = {}
        # Gera um nome único para o escopo para evitar colisões
        nome_esc = f"{nome}_{len(self.historico) + 1}"
        
        # Adiciona o novo escopo à pilha de escopos ativos
        self.escopos.append(novo_dict)
        self.nomes.append(nome_esc)
        
        # NOVO: Registra o novo escopo no histórico para não perdê-lo
        self.historico.append((nome_esc, novo_dict))

    def sair_escopo(self):
        """
        Remove o escopo atual da pilha de escopos ativos.
        Não mexe no histórico.
        """
        if len(self.escopos) > 1:
            self.escopos.pop()
            self.nomes.pop()

    def declarar(self, lexema, tipo, categoria, linha=None):
        escopo_atual = self.escopos[-1]
        nome_escopo_atual = self.nomes[-1]
        if lexema in escopo_atual:
            raise ErroSemantico(f"Símbolo '{lexema}' já declarado", linha, escopo=nome_escopo_atual)
        escopo_atual[lexema] = {'lexema': lexema, 'tipo': tipo, 'categoria': categoria, 'escopo': nome_escopo_atual, 'utilizada': False, 'linha': linha}

    def buscar(self, lexema):
        for esc in reversed(self.escopos):
            if lexema in esc:
                return esc[lexema]
        return None

    def marcar_utilizada(self, lexema):
        simb = self.buscar(lexema)
        if simb:
            simb['utilizada'] = True

    # MUDANÇA: O método agora itera sobre o histórico, não sobre a pilha ativa.
    def formatar_por_escopo(self):
        """
        Formata a tabela de símbolos em um dicionário, onde cada chave é um nome de escopo
        e cada valor é a lista de símbolos declarados naquele escopo.
        Utiliza o histórico para garantir que todos os escopos sejam incluídos.
        """
        tabelas_por_escopo = {}

        # MUDANÇA: Itera sobre o histórico de todos os escopos que já existiram.
        for nome_escopo, escopo_dict in self.historico:
            lista_simbolos = []
            for simbolo in escopo_dict.values():
                lista_simbolos.append({
                    'Lexema':    simbolo['lexema'],
                    'Categoria': simbolo['categoria'],
                    'Tipo':      simbolo['tipo'],
                    'Utilizada': simbolo['utilizada'],
                    'Linha':     simbolo['linha']
                })
            tabelas_por_escopo[nome_escopo] = lista_simbolos

        return tabelas_por_escopo

# A classe ErroSemantico permanece a mesma da resposta anterior.
class ErroSemantico(Exception):
    def __init__(self, msg, linha=None, escopo=None):
        super().__init__(msg)
        self.mensagem = msg
        self.linha = linha
        self.escopo = escopo

    def __str__(self):
        return f"Linha {self.linha or 'N/A'} | Escopo: {self.escopo or 'global'} | Erro: {self.mensagem}"


class AnalisadorSemantico:
    def __init__(self):
        self.tabela = TabelaSimbolos()
        self.erros = []
        self.tipos_compat = {'int': {'int'}, 'real': {'int', 'real'}, 'boolean': {'boolean'}}
        self.declarar_builtins()

    def declarar_builtins(self):
        try:
            self.tabela.declarar('read', 'builtin', 'procedimento')
            self.tabela.marcar_utilizada('read')
            self.tabela.declarar('write', 'builtin', 'procedimento')
            self.tabela.marcar_utilizada('write')
        except ErroSemantico:
            pass

    def erro(self, msg, linha=None, escopo_especifico=None):
        escopo_atual = escopo_especifico if escopo_especifico is not None else self.tabela.nomes[-1]
        self.erros.append(ErroSemantico(msg, linha, escopo_atual))

    # MUDANÇA: Novo método para formatar a lista de erros em uma tabela.
    def formatar_erros(self):
        """Converte a lista de objetos ErroSemantico (ou strings) em uma lista de dicionários."""
        tabela_erros = []
        for e in self.erros:
            if isinstance(e, ErroSemantico):
                linha = e.linha
                escopo = e.escopo
                msg = e.mensagem
            else:
                # Se for só uma string, converte para um dict genérico
                linha = None
                escopo = None
                msg = str(e)
            tabela_erros.append({
                'Linha': linha,
                'Escopo': escopo,
                'Mensagem': msg
            })
        return tabela_erros

    def analisar(self, tokens, lexemas, linhas):
        # Reset para nova análise
        self.tabela = TabelaSimbolos()
        self.erros.clear()
        self.declarar_builtins()
        i = 0
        
        # ... (todo o loop de análise 'while i < len(tokens):' permanece exatamente o mesmo) ...
        # ... O código do loop foi omitido aqui por brevidade, pois não muda. ...
        # Reconhecer 'program <nome> ;'
        if i < len(tokens) and tokens[i] == 'program':
            i += 1
            if i < len(tokens) and tokens[i] == 'identifier':
                nome_prog = lexemas[i]
                try:
                    self.tabela.declarar(nome_prog, 'n/a', 'program', linhas[i])
                    self.tabela.marcar_utilizada(nome_prog)
                except ErroSemantico as e:
                    self.erros.append(e)
                i += 1
            if i < len(tokens) and tokens[i] == 'semicolon': i += 1

        while i < len(tokens):
            tok, lex, lin = tokens[i], lexemas[i], linhas[i]

            # Declaração de variáveis
            if tok in ('int', 'real', 'boolean'):
                tipo = tok
                i += 1
                while i < len(tokens) and tokens[i] != 'semicolon':
                    if tokens[i] == 'identifier':
                        try:
                            self.tabela.declarar(lexemas[i], tipo, 'variavel', linhas[i])
                        except ErroSemantico as e:
                            self.erros.append(e)
                    i += 1
                if i < len(tokens) and tokens[i] == 'semicolon': i += 1
                continue

            # Procedimento
            if tok == 'procedure':
                i += 1
                if i < len(tokens) and tokens[i] == 'identifier':
                    nome = lexemas[i]
                    try: 
                        self.tabela.declarar(nome, 'n/a', 'procedimento', lin)
                        self.tabela.entrar_escopo(nome)
                        escopo_atual = self.tabela.nomes[-1]
                        
                        # Processar parâmetros
                        i += 1
                        if i < len(tokens) and tokens[i] == 'right_parenteses':
                            i += 1
                            while i < len(tokens) and tokens[i] != 'left_parenteses':
                                if tokens[i] == 'variable':
                                    i += 1
                                    if tokens[i] == 'identifier':
                                        param_name = lexemas[i]
                                        i += 1
                                        if tokens[i] == 'colon':
                                            i += 1
                                            if tokens[i] in ('int', 'boolean'):
                                                tipo_p = tokens[i]
                                                try: 
                                                    self.tabela.declarar(
                                                        param_name, 
                                                        tipo_p, 
                                                        'parametro', 
                                                        linhas[i]
                                                    )
                                                except ErroSemantico as e: 
                                                    self.erros.append(e)
                                i += 1
                    except ErroSemantico as e: 
                        self.erros.append(e)


            # Início de bloco
            if tok == 'begin':
                self.tabela.entrar_escopo('begin_block')
                i += 1
                continue

            # Fim de bloco ou programa
            if tok in ('end', 'end_command'):
                escopo_atual = self.tabela.escopos[-1]
                for s in list(escopo_atual.values()):
                    if s['categoria'] in ('variavel', 'parametro') and not s['utilizada']:
                        kind = 'Parâmetro' if s['categoria'] == 'parametro' else 'Variável'
                        self.erro(f"Aviso: {kind} '{s['lexema']}' declarado mas não utilizado.",s['linha'],escopo_especifico=s['escopo'])
                self.tabela.sair_escopo()
                i += 1
                if i < len(tokens) and tokens[i] in ('semicolon', 'period'): i += 1
                continue

            # Identificador: atribuição ou chamada
            if tok == 'identifier':
                simb = self.tabela.buscar(lex)
                if not simb:
                    self.erro(f"Símbolo '{lex}' não declarado.", lin)
                    i += 1
                    continue
                self.tabela.marcar_utilizada(lex)
                if i + 1 < len(tokens) and tokens[i+1] == 'assignment_operator':
                    var_tipo = simb['tipo']
                    i += 2
                    exp_tipo, i = self._tipo_expressao(tokens, lexemas, linhas, i)
                    if exp_tipo and exp_tipo not in self.tipos_compat.get(var_tipo, {}):
                        self.erro(f"Incompatibilidade de tipos: não é possível atribuir '{exp_tipo}' a '{var_tipo}'.", lin)
                    continue
                i += 1
                continue
            i += 1
        # --- FIM DO LOOP DE ANÁLISE ---

        # MUDANÇA: O retorno agora é um dicionário estruturado.
        resultado_analise = {
            "erros": self.formatar_erros(),
            "tabelas_de_simbolos": self.tabela.formatar_por_escopo()
        }
        
        return resultado_analise

    def analisar_tokens(self, token_table):
        return self.analisar(token_table['token'], token_table['lexema'], token_table['linha'])

    def _tipo_expressao(self, toks, lexs, lins, i):
        if i >= len(toks): return None, i
        t, l, lin = toks[i], lexs[i], lins[i]
        if t == 'integer': return 'int', i + 1
        if t == 'real': return 'real', i + 1
        if t in ('true', 'false'): return 'boolean', i + 1
        if t == 'identifier':
            s = self.tabela.buscar(l)
            if s:
                self.tabela.marcar_utilizada(l)
                return s['tipo'], i + 1
            else:
                self.erro(f"Símbolo '{l}' não declarado (usado em expressão).", lin)
                return None, i + 1
        return None, i + 1
    
    def buscar_escopo(tabela, lexema, escopo_atual):
        # Primeiro busca no escopo atual
        if escopo_atual in tabela:
            for simbolo in tabela[escopo_atual]:
                if simbolo['Lexema'] == lexema:
                    return simbolo
        
        # Depois busca no escopo global
        if 'global' in tabela:
            for simbolo in tabela['global']:
                if simbolo['Lexema'] == lexema:
                    return simbolo
                    
        return None
