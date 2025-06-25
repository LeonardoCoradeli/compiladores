# Módulo: Tabela de Símbolos Corrigida

class TabelaSimbolos:
    def __init__(self):
        # A lista de escopos funciona como a nossa pilha. O último dicionário é o topo.
        self.escopos = [{}]
        # <<< MELHORIA: Não precisamos de 'escopo_atual' e 'escopo_nomes' complexos.
        # A pilha de escopos em si já gerencia isso de forma mais simples.
        self.nomes_escopo_pilha = ['global']

    def entrar_escopo(self, nome_escopo='anonimo'):
        """ Empurra um novo escopo (dicionário) para o topo da pilha. """
        self.escopos.append({})
        # Adiciona um nome único para o escopo para fins de depuração/impressão
        nome_unico = f"{nome_escopo}_{len(self.escopos)}"
        self.nomes_escopo_pilha.append(nome_unico)

    def sair_escopo(self):
        """ Remove o escopo do topo da pilha. """
        if len(self.escopos) > 1:
            self.escopos.pop()
            self.nomes_escopo_pilha.pop()

    def declarar(self, nome, tipo, categoria, linha=None):
        """ Declara um símbolo no escopo atual (topo da pilha). """
        escopo_atual = self.escopos[-1]  # Pega o topo da pilha
        if nome in escopo_atual:
            raise ErroSemantico(f"Símbolo '{nome}' já declarado neste escopo.", linha)

        # <<< CORRIGIDO: O campo 'valor' foi removido. Não é responsabilidade do compilador.
        escopo_atual[nome] = {
            'lexema': nome,
            'token': 'identifier',
            'categoria': categoria,
            'tipo': tipo,
            # 'valor': None, # <<< REMOVIDO
            'escopo': self.nomes_escopo_pilha[-1],
            'utilizada': False,
            'linha': linha
        }

    # <<< REMOVIDO: O método declarar_global era complicado e propenso a erros.
    # É mais simples lidar com isso diretamente no analisador, se necessário,
    # ou garantir que as declarações globais ocorram quando apenas o escopo global está na pilha.

    def buscar(self, nome):
        """ Procura por um símbolo do escopo atual (topo) para o global (base). """
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        return None

    def marcar_utilizada(self, nome):
        simbolo = self.buscar(nome)
        if simbolo:
            simbolo['utilizada'] = True

    # <<< REMOVIDO: Este método é o cerne do erro conceitual. O compilador não atualiza valores.
    # def atualizar_valor(self, nome, valor): ...

    def obter_tabela_formatada(self):
        """ Gera uma lista formatada de todos os símbolos de todos os escopos. """
        tabela = []
        # Como os escopos são removidos ao sair, precisamos de uma cópia ou outra abordagem.
        # Para simplificar, vamos assumir que a tabela é gerada no final, antes de qualquer "limpeza".
        # A sua abordagem com hist_escopos era uma forma de lidar com isso.
        # Aqui, vamos apenas iterar sobre os escopos que ainda existem.
        for escopo in self.escopos:
            for attrs in escopo.values():
                tabela.append({
                    'Lexema': attrs['lexema'],
                    'Token': attrs['token'],
                    'Categoria': attrs['categoria'],
                    'Tipo': attrs['tipo'],
                    # 'Valor': attrs.get('valor', 'N/A'), # O valor não existe mais
                    'Escopo': attrs['escopo'],
                    'Utilizada': attrs['utilizada']
                })
        return tabela

    def todos_simbolos_escopo_atual(self):
        if not self.escopos:
            return []
        return list(self.escopos[-1].values())

class ErroSemantico(Exception):
    def __init__(self, mensagem, linha=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.linha = linha

class AnalisadorSemantico:
    def __init__(self):
        self.tabela = TabelaSimbolos()
        self.erros = []
        self.tipos_compativel = {
            # Destino: {Origens permitidas}
            'int': {'int'},
            'real': {'int', 'real'},
            'boolean': {'boolean'}
        }
        # Adicionar built-ins
        self.tabela.declarar('read', 'builtin', 'procedimento')
        self.tabela.declarar('write', 'builtin', 'procedimento')

    def erro(self, mensagem, linha=None):
        self.erros.append(ErroSemantico(mensagem, linha))

    def verificar_compatibilidade_atribuicao(self, tipo_variavel, tipo_expressao, linha):
        """ Verifica se o tipo da expressão é compatível com o tipo da variável. """
        if tipo_expressao not in self.tipos_compativel.get(tipo_variavel, set()):
             self.erro(f"Tipo incompatível: não é possível atribuir uma expressão do tipo '{tipo_expressao}' a uma variável do tipo '{tipo_variavel}'.", linha)

    def analisar_tokens(self, token_table):
        # Reinicia o estado para uma nova análise
        self.erros.clear()
        self.tabela = TabelaSimbolos()
        self.tabela.declarar('read', 'builtin', 'procedimento')
        self.tabela.declarar('write', 'builtin', 'procedimento')

        tokens = token_table['token']
        lexemas = token_table['lexema']
        linhas = token_table['linha']

        i = 0
        # O loop principal para percorrer os tokens precisa ser mais robusto,
        # idealmente guiado por uma gramática (usando um parser).
        # Este loop simplificado serve para demonstrar a correção da tabela de símbolos.
        
        # Simulação de análise simplificada
        # Este loop é apenas um exemplo e não representa um parser completo
        while i < len(tokens):
            tok = tokens[i]
            lexema = lexemas[i]
            linha = linhas[i]

            if tok in ('int', 'real', 'boolean'):
                tipo_atual = tok
                i += 2 # Pula tipo e ':'
                while i < len(tokens) and tokens[i] != 'semicolon':
                    if tokens[i] == 'identifier':
                        self._declarar_variavel(lexemas[i], tipo_atual, linhas[i])
                    i += 1 # Pula identificador ou vírgula
                i += 1 # Pula ';'
                continue

            elif tok == 'procedure':
                i += 1
                nome_proc = lexemas[i]
                self.tabela.declarar(nome_proc, 'n/a', 'procedimento', linhas[i])
                self.tabela.entrar_escopo(nome_proc)
                # Aqui viria a análise de parâmetros e do corpo do procedimento
                i += 1
                continue

            elif tok == 'begin':
                # Em algumas linguagens, 'begin' pode abrir um escopo anônimo
                self.tabela.entrar_escopo()
                i += 1
                continue

            elif tok == 'end_command':
                # Antes de sair, verifica variáveis não usadas no escopo que está fechando
                self._verificar_variaveis_nao_usadas_escopo_atual()
                self.tabela.sair_escopo()
                i += 1
                continue

            elif tok == 'identifier':
                simbolo = self.tabela.buscar(lexema)
                if not simbolo:
                    self.erro(f"Símbolo '{lexema}' não foi declarado.", linha)
                    i += 1
                    continue
                
                self.tabela.marcar_utilizada(lexema)

                # Verifica se é uma atribuição
                if i + 1 < len(tokens) and tokens[i+1] == 'assignment_operator':
                    i += 2 # Avança para o início da expressão
                    
                    # <<< CORRIGIDO: Agora obtemos apenas o TIPO da expressão
                    tipo_da_expressao, new_i = self._obter_tipo_expressao(tokens, lexemas, linhas, i)
                    i = new_i

                    if tipo_da_expressao:
                        # A verificação de compatibilidade é a única coisa que fazemos
                        self.verificar_compatibilidade_atribuicao(simbolo['tipo'], tipo_da_expressao, linha)

                    # <<< REMOVIDO: A chamada para atualizar o valor não existe mais
                    # self.tabela.atualizar_valor(nome, val)
                    continue

            i += 1

        return self.erros, self.tabela.obter_tabela_formatada()

    def _declarar_variavel(self, nome, tipo, linha):
        try:
            self.tabela.declarar(nome, tipo, 'variavel', linha)
        except ErroSemantico as e:
            self.erro(e.mensagem, linha)

    def _obter_tipo_expressao(self, tokens, lexemas, linhas, i):
        # <<< CORRIGIDO: Esta função agora retorna apenas o TIPO, não o valor.
        # Esta é uma versão muito simplificada que lida apenas com um único termo.
        # Uma análise de expressão real seria recursiva e lidaria com operadores.
        if i >= len(tokens): return None, i
        
        tok, lex, linha = tokens[i], lexemas[i], linhas[i]

        if tok == 'integer': return 'int', i + 1
        if tok == 'real': return 'real', i + 1
        if tok == 'true' or tok == 'false': return 'boolean', i + 1
        
        if tok == 'identifier':
            sym = self.tabela.buscar(lex)
            if sym:
                self.tabela.marcar_utilizada(lex)
                # Retorna o tipo do símbolo encontrado na tabela
                return sym['tipo'], i + 1
            else:
                self.erro(f"Símbolo '{lex}' não declarado usado em uma expressão.", linha)
                return None, i + 1
        
        # Retorno padrão se a expressão for desconhecida
        return None, i + 1

    def _verificar_variaveis_nao_usadas_escopo_atual(self):
        """ Verifica variáveis não utilizadas apenas no escopo do topo da pilha. """
        for simbolo in self.tabela.todos_simbolos_escopo_atual():
            if simbolo['categoria'] == 'variavel' and not simbolo['utilizada']:
                self.erro(f"Aviso: Variável '{simbolo['lexema']}' declarada mas não usada no escopo '{simbolo['escopo']}'.", simbolo['linha'])

