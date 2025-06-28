class MepaInterpreterDebug:
    def __init__(self, mepa_code, input_data=None, debug=False):
        self.C = mepa_code        
        self.D = [0] * 100       
        self.i = 0                
        self.s = -1               
        self.input_data = input_data or []  
        self.input_index = 0      
        self.output = []          
        self.running = True       
        self.debug = debug        
        self.step_count = 0       

    def print_debug(self, msg):
        if self.debug:
            print(msg)

    def print_state(self):
        if self.debug:
            stack_values = []
            if self.s >= 0:
                for i in range(max(0, self.s-3), self.s+1):
                    if i <= self.s:
                        stack_values.append(f"[{i}]={self.D[i]}")
            
            print(f"  Estado: PC={self.i}, S={self.s}, Stack: {' '.join(stack_values)}")
            print(f"  Memória 0-9: {self.D[0:10]}")

    def run(self):
        """Executa o programa MEPA até encontrar PARA ou fim do código"""
        while self.running and self.i < len(self.C):
            instruction = self.C[self.i]
            self.step_count += 1
            
            
            if self.step_count > 1000:
                raise RuntimeError("Limite de passos excedido - possível loop infinito")
            
            
            if isinstance(instruction, str):
                instruction = [instruction]
            elif not isinstance(instruction, list):
                raise RuntimeError(f"Instrução inválida: {instruction}")
            
            op = instruction[0]
            args = instruction[1:] if len(instruction) > 1 else []

            self.print_debug(f"\nPasso {self.step_count}: Instrução {self.i}: {instruction}")
            self.print_state()

            try:
                
                if op == "INPP":
                    self.inpp()
                elif op == "AMEM":
                    if not args:
                        raise RuntimeError("AMEM requer um argumento")
                    self.amem(args[0])
                elif op == "DMEM":
                    if not args:
                        raise RuntimeError("DMEM requer um argumento")
                    self.dmem(args[0])
                elif op == "CRCT":
                    if not args:
                        raise RuntimeError("CRCT requer um argumento")
                    self.crct(args[0])
                elif op == "CRVL":
                    if not args:
                        raise RuntimeError("CRVL requer um argumento")
                    self.crvl(args[0])
                elif op == "ARMZ":
                    if not args:
                        raise RuntimeError("ARMZ requer um argumento")
                    self.armz(args[0])
                elif op == "SOMA":
                    self.soma()
                elif op == "SUBT":
                    self.subt()
                elif op == "MULT":
                    self.mult()
                elif op == "DIVI":
                    self.divi()
                elif op == "INVR":
                    self.invr()
                elif op == "CONJ":
                    self.conj()
                elif op == "DISJ":
                    self.disj()
                elif op == "NEGA":
                    self.nega()
                elif op == "CMME":
                    self.cmme()
                elif op == "CMMA":
                    self.cmma()
                elif op == "CMIG":
                    self.cmig()
                elif op == "CMDG":
                    self.cmdg()
                elif op == "CMAG":
                    self.cmag()
                elif op == "CMEG":
                    self.cmeg()
                elif op == "DSVS":
                    if not args:
                        raise RuntimeError("DSVS requer um argumento")
                    self.dsvs(args[0])
                elif op == "DSVF":
                    if not args:
                        raise RuntimeError("DSVF requer um argumento")
                    self.dsvf(args[0])
                elif op == "LEIT":
                    self.leit()
                elif op == "IMPR":
                    self.impr()
                elif op == "IMPC":
                    self.impc()
                elif op == "IMPE":
                    self.impe()
                elif op == "PARA":
                    self.para()
                elif op == "NADA":
                    self.nada()
                elif op == "CHPR":
                    
                    if not args:
                        raise RuntimeError("CHPR requer um argumento")
                    self.chpr(args[0])
                elif op == "RTPR":
                    
                    self.rtpr()
                else:
                    raise RuntimeError(f"Instrução desconhecida: {op}")
                
                
                if op not in ["DSVS", "DSVF", "PARA", "CHPR", "RTPR"]:
                    self.i += 1
                elif op == "DSVF" and not hasattr(self, '_jumped'):
                    self.i += 1
                
                
                if hasattr(self, '_jumped'):
                    delattr(self, '_jumped')
                        
            except Exception as e:
                self.print_debug(f"ERRO na instrução {op}:")
                self.print_state()
                raise RuntimeError(f"Erro na instrução {op} na posição {self.i}: {e}")
        
        return {
            "memory": self.D,
            "stack_top": self.s,
            "output": self.output,
            "final_pc": self.i,
            "steps": self.step_count
        }

    
    def inpp(self):
        """Inicializa o programa principal"""
        self.D = [0] * 100  
        self.s = -1         
        self.print_debug("  -> INPP: Inicializado")

    def amem(self, m):
        """Aloca m posições na memória"""
        self.s += m
        self.print_debug(f"  -> AMEM {m}: s = {self.s}")

    def dmem(self, m):
        """Desaloca m posições da memória"""
        self.s -= m
        self.print_debug(f"  -> DMEM {m}: s = {self.s}")

    def crct(self, k):
        """Empilha constante k"""
        if self.s >= 99:
            raise RuntimeError("Stack overflow")
        self.s += 1
        self.D[self.s] = k
        self.print_debug(f"  -> CRCT {k}: empilhado em [{self.s}]")

    def crvl(self, n):
        """Empilha valor do endereço n"""
        if self.s >= 99:
            raise RuntimeError("Stack overflow")
        if n < 0 or n >= 100:
            raise RuntimeError(f"Endereço inválido: {n}")
        self.s += 1
        self.D[self.s] = self.D[n]
        self.print_debug(f"  -> CRVL {n}: valor {self.D[n]} empilhado em [{self.s}]")

    def armz(self, n):
        """Armazena topo no endereço n e desempilha"""
        if self.s < 0:
            raise RuntimeError("Stack underflow")
        if n < 0 or n >= 100:
            raise RuntimeError(f"Endereço inválido: {n}")
        value = self.D[self.s]
        self.D[n] = value
        self.s -= 1
        self.print_debug(f"  -> ARMZ {n}: valor {value} armazenado, s = {self.s}")

    def soma(self):
        """Soma os dois valores do topo"""
        if self.s < 1:
            raise RuntimeError("Stack underflow - precisa de 2 elementos")
        b = self.D[self.s]
        a = self.D[self.s-1]
        result = a + b
        self.D[self.s-1] = result
        self.s -= 1
        self.print_debug(f"  -> SOMA: {a} + {b} = {result}")

    def subt(self):
        """Subtrai os dois valores do topo (a - b)"""
        if self.s < 1:
            raise RuntimeError("Stack underflow - precisa de 2 elementos")
        b = self.D[self.s]
        a = self.D[self.s-1]
        result = a - b
        self.D[self.s-1] = result
        self.s -= 1
        self.print_debug(f"  -> SUBT: {a} - {b} = {result}")

    def mult(self):
        """Multiplica os dois valores do topo"""
        if self.s < 1:
            raise RuntimeError("Stack underflow - precisa de 2 elementos")
        b = self.D[self.s]
        a = self.D[self.s-1]
        result = a * b
        self.D[self.s-1] = result
        self.s -= 1
        self.print_debug(f"  -> MULT: {a} * {b} = {result}")

    def divi(self):
        """Divide os dois valores do topo (a / b)"""
        if self.s < 1:
            raise RuntimeError("Stack underflow - precisa de 2 elementos")
        b = self.D[self.s]
        a = self.D[self.s-1]
        self.print_debug(f"  -> DIVI: tentando {a} / {b}")
        if b == 0:
            raise RuntimeError("Divisão por zero")
        result = a // b  
        self.D[self.s-1] = result
        self.s -= 1
        self.print_debug(f"  -> DIVI: {a} / {b} = {result}")

    def invr(self):
        """Inverte o sinal do topo"""
        if self.s < 0:
            raise RuntimeError("Stack underflow")
        self.D[self.s] = -self.D[self.s]
        self.print_debug(f"  -> INVR: resultado = {self.D[self.s]}")

    def conj(self):
        """Operação lógica AND"""
        if self.s < 1:
            raise RuntimeError("Stack underflow - precisa de 2 elementos")
        b = self.D[self.s]
        a = self.D[self.s-1]
        result = 1 if (a != 0 and b != 0) else 0
        self.D[self.s-1] = result
        self.s -= 1
        self.print_debug(f"  -> CONJ: {a} AND {b} = {result}")

    def disj(self):
        """Operação lógica OR"""
        if self.s < 1:
            raise RuntimeError("Stack underflow - precisa de 2 elementos")
        b = self.D[self.s]
        a = self.D[self.s-1]
        result = 1 if (a != 0 or b != 0) else 0
        self.D[self.s-1] = result
        self.s -= 1
        self.print_debug(f"  -> DISJ: {a} OR {b} = {result}")

    def nega(self):
        """Operação lógica NOT"""
        if self.s < 0:
            raise RuntimeError("Stack underflow")
        result = 0 if self.D[self.s] != 0 else 1
        self.D[self.s] = result
        self.print_debug(f"  -> NEGA: resultado = {result}")

    def cmme(self):
        """Comparação: a < b"""
        if self.s < 1:
            raise RuntimeError("Stack underflow - precisa de 2 elementos")
        b = self.D[self.s]
        a = self.D[self.s-1]
        result = 1 if a < b else 0
        self.D[self.s-1] = result
        self.s -= 1
        self.print_debug(f"  -> CMME: {a} < {b} = {result}")

    def cmma(self):
        """Comparação: a > b"""
        if self.s < 1:
            raise RuntimeError("Stack underflow - precisa de 2 elementos")
        b = self.D[self.s]
        a = self.D[self.s-1]
        result = 1 if a > b else 0
        self.D[self.s-1] = result
        self.s -= 1
        self.print_debug(f"  -> CMMA: {a} > {b} = {result}")

    def cmig(self):
        """Comparação: a == b"""
        if self.s < 1:
            raise RuntimeError("Stack underflow - precisa de 2 elementos")
        b = self.D[self.s]
        a = self.D[self.s-1]
        result = 1 if a == b else 0
        self.D[self.s-1] = result
        self.s -= 1
        self.print_debug(f"  -> CMIG: {a} == {b} = {result}")

    def cmdg(self):
        """Comparação: a != b"""
        if self.s < 1:
            raise RuntimeError("Stack underflow - precisa de 2 elementos")
        b = self.D[self.s]
        a = self.D[self.s-1]
        result = 1 if a != b else 0
        self.D[self.s-1] = result
        self.s -= 1
        self.print_debug(f"  -> CMDG: {a} != {b} = {result}")

    def cmag(self):
        """Comparação: a >= b"""
        if self.s < 1:
            raise RuntimeError("Stack underflow - precisa de 2 elementos")
        b = self.D[self.s]
        a = self.D[self.s-1]
        result = 1 if a >= b else 0
        self.D[self.s-1] = result
        self.s -= 1
        self.print_debug(f"  -> CMAG: {a} >= {b} = {result}")

    def cmeg(self):
        """Comparação: a <= b"""
        if self.s < 1:
            raise RuntimeError("Stack underflow - precisa de 2 elementos")
        b = self.D[self.s]
        a = self.D[self.s-1]
        result = 1 if a <= b else 0
        self.D[self.s-1] = result
        self.s -= 1
        self.print_debug(f"  -> CMEG: {a} <= {b} = {result}")

    def dsvs(self, p):
        """Desvio incondicional"""
        
        if not isinstance(p, int):
            raise RuntimeError(f"Endereço de desvio deve ser um número inteiro: {p}")
        if p < 0 or p >= len(self.C):
            raise RuntimeError(f"Endereço de desvio inválido: {p}")
        self.i = p
        self._jumped = True
        self.print_debug(f"  -> DSVS {p}: saltando para {p}")

    def dsvf(self, p):
        """Desvio se falso (topo == 0)"""
        if self.s < 0:
            raise RuntimeError("Stack underflow")
        
        if not isinstance(p, int):
            raise RuntimeError(f"Endereço de desvio deve ser um número inteiro: {p}")
        if p < 0 or p >= len(self.C):
            raise RuntimeError(f"Endereço de desvio inválido: {p}")
        
        condition = self.D[self.s]
        self.s -= 1
        
        if condition == 0:
            self.i = p
            self._jumped = True
            self.print_debug(f"  -> DSVF {p}: condição falsa, saltando para {p}")
        else:
            self.print_debug(f"  -> DSVF {p}: condição verdadeira, continuando")

    def leit(self):
        """Lê um valor da entrada"""
        if self.s >= 99:
            raise RuntimeError("Stack overflow")
        
        self.s += 1
        if self.input_index >= len(self.input_data):
            value = 0  
        else:
            value = self.input_data[self.input_index]
            self.input_index += 1
        
        self.D[self.s] = value
        self.print_debug(f"  -> LEIT: valor {value} lido")

    def impr(self):
        """Imprime o valor do topo"""
        if self.s < 0:
            raise RuntimeError("Stack underflow")
        value = self.D[self.s]
        self.output.append(str(value))
        self.s -= 1
        self.print_debug(f"  -> IMPR: {value}")

    def impc(self):
        """Imprime caractere"""
        if self.s < 0:
            raise RuntimeError("Stack underflow")
        char_code = self.D[self.s]
        if 0 <= char_code <= 127:  
            char = chr(char_code)
            self.output.append(char)
        else:
            self.output.append('?')  
        self.s -= 1
        self.print_debug(f"  -> IMPC: código {char_code}")

    def impe(self):
        """Imprime fim de linha"""
        self.output.append("\n")
        self.print_debug("  -> IMPE: nova linha")

    def para(self):
        """Termina a execução"""
        self.running = False
        self.print_debug("  -> PARA: fim da execução")

    def nada(self):
        """Operação nula (apenas desempilha)"""
        if self.s < 0:
            raise RuntimeError("Stack underflow")
        self.s -= 1
        self.print_debug("  -> NADA: desempilhado")

    def chpr(self, p):
        """Chama procedimento (versão simplificada)"""
        
        if not isinstance(p, int):
            raise RuntimeError(f"Endereço de chamada deve ser um número inteiro: {p}")
        
        if self.s >= 99:
            raise RuntimeError("Stack overflow")
        self.s += 1
        self.D[self.s] = self.i + 1  
        self.i = p
        self._jumped = True
        self.print_debug(f"  -> CHPR {p}: chamando procedimento, retorno em {self.D[self.s]}")

    def rtpr(self):
        """Retorna de procedimento (versão simplificada)"""
        if self.s < 0:
            raise RuntimeError("Stack underflow - sem endereço de retorno")
        return_address = self.D[self.s]
        self.s -= 1
        self.i = return_address
        self._jumped = True
        self.print_debug(f"  -> RTPR: retornando para {return_address}")



if __name__ == "__main__":
    
    codigo_exemplo = [
        ['INPP'], 
        ['AMEM', 6], 
        ['CRCT', 1], 
        ['CRVL', 0], 
        ['CMME'], 
        ['CRCT', 1], 
        ['CRVL', 0], 
        ['CRCT', 12], 
        ['CRVL', 0], 
        ['SUBT'], 
        ['CRCT', 2], 
        ['CRVL', 1], 
        ['CRCT', 10], 
        ['CRVL', 2], 
        ['CRCT', 11], 
        ['CRVL', 0], 
        ['CRVL', 1], 
        ['SOMA'], 
        ['CRVL', 2], 
        ['CRVL', 3], 
        ['CRCT', 1], 
        ['CRVL', 4], 
        ['CRCT', 0], 
        ['CRVL', 5], 
        ['CRCT', 1], 
        ['CRVL', 0], 
        ['CRVL', 0], 
        ['CRVL', 0], 
        ['CRVL', 1], 
        ['CRVL', 3], 
        ['CRVL', 0], 
        ['SOMA'], 
        ['CRCT', 20], 
        ['CRVL', 1], 
        ['CRCT', 10], 
        ['MULT'], 
        ['CRVL', 2], 
        ['CRVL', 2], 
        ['CRVL', 0], 
        ['DIVI'], 
        ['CRVL', 1], 
        ['CRVL', 0], 
        ['CMME'], 
        ['CRCT', 1], 
        ['CRVL', 0], 
        ['CRCT', 1], 
        ['CRVL', 1], 
        ['CRCT', 2], 
        ['CRVL', 0], 
        ['CRVL', 0], 
        ['CRVL', 0], 
        ['CRVL', 1], 
        ['CRVL', 0], 
        ['CMMA'], 
        ['CRCT', 1], 
        ['CRVL', 1], 
        ['CMMA'], 
        ['CRCT', 10], 
        ['CRVL', 1], 
        ['CRCT', 2], 
        ['CRVL', 0], 
        ['CRVL', 0], 
        ['SUBT'], 
        ['CRCT', 1], 
        ['ARMZ', 0], 
        ['PARA']
    ]
    
    
    codigo_simples = [
        ['INPP'],
        ['CRCT', 10],
        ['CRCT', 5],
        ['SOMA'],
        ['IMPR'],
        ['PARA']
    ]
    
    interpreter = MepaInterpreterDebug(codigo_exemplo, input_data=[], debug=True)
    
    try:
        print("Executando código MEPA...")
        resultado = interpreter.run()
        print(f"\nExecução concluída em {resultado['steps']} passos")
        print("Saída:", "".join(resultado["output"]))
        print(f"Memória final (0-9): {resultado['memory'][0:10]}")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        print(f"Execução parou no passo {interpreter.step_count}")