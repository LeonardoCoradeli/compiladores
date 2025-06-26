class MEPAInterpreter:
    def __init__(self, code):
        self.code = code
        self.D = []  # Área de dados
        self.C = []  # Área de código
        self.i = 0   # Contador de programa
        self.s = -1  # Topo da pilha
        self.output = []
        self.labels = {}
        
        # Pré-processamento: extrai labels
        current_idx = 0
        for instr in code:
            if isinstance(instr[0], str) and instr[0].endswith(':'):
                self.labels[instr[0][:-1]] = current_idx
            else:
                self.C.append(instr)
                current_idx += 1
    
    def run(self):
        self.i = 0
        self.s = -1
        self.D = [0] * 1000  # Tamanho arbitrário da memória
        
        while self.i < len(self.C):
            instr = self.C[self.i]
            op = instr[0]
            args = instr[1:] if len(instr) > 1 else []
            
            # Executa instrução
            if op == 'INPP':
                self.s = -1
            elif op == 'AMEM':
                self.s += args[0]
            elif op == 'DMEM':
                self.s -= args[0]
            elif op == 'CRCT':
                self.s += 1
                self.D[self.s] = args[0]
            elif op == 'CRVL':
                self.s += 1
                self.D[self.s] = self.D[args[0]]
            elif op == 'ARMZ':
                self.D[args[0]] = self.D[self.s]
                self.s -= 1
            elif op == 'SOMA':
                self.D[self.s-1] += self.D[self.s]
                self.s -= 1
            elif op == 'SUBT':
                self.D[self.s-1] -= self.D[self.s]
                self.s -= 1
            elif op == 'MULT':
                self.D[self.s-1] *= self.D[self.s]
                self.s -= 1
            elif op == 'DIVI':
                self.D[self.s-1] /= self.D[self.s]
                self.s -= 1
            elif op == 'CMMA':
                self.D[self.s-1] = 1 if self.D[self.s-1] > self.D[self.s] else 0
                self.s -= 1
            elif op == 'CMME':
                self.D[self.s-1] = 1 if self.D[self.s-1] < self.D[self.s] else 0
                self.s -= 1
            elif op == 'DSVF':
                if self.D[self.s] == 0:
                    self.i = self.labels[args[0]]
                    self.s -= 1
                    continue
                self.s -= 1
            elif op == 'DSVS':
                self.i = self.labels[args[0]]
                continue
            elif op == 'LEIT':
                self.s += 1
                try:
                    self.D[self.s] = float(input("Entre com um valor: "))
                except:
                    self.D[self.s] = 0
            elif op == 'IMPR':
                self.output.append(str(self.D[self.s]))
                self.s -= 1
            elif op == 'IMPE':
                self.output.append("\n")
            elif op == 'NADA':
                pass  # Não faz nada
            
            self.i += 1
        
        return self.output