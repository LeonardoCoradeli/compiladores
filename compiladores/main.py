from flask import Flask, request, jsonify
from alfabeto import obter_tokens
from flask_cors import CORS
from utils import find_file
from tabela import get_table
from follow_sets import get_follow_set
from lexico import AnaliseLexica
from sintatico import SyntacticAnalyzer
from semantico import AnalisadorSemantico
from gerador import MEPACodeGenerator
from MepaInterpreter import MepaInterpreterDebug

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return jsonify({'message': 'API de Análise Léxica'}),200

@app.route('/enviar_conteudo', methods=['POST'])
def enviar_conteudo():
    try:
        conteudo = request.data.decode('utf-8')
        
        # Análise léxica
        lexico = AnaliseLexica(obter_tokens())
        lexico.create_table(conteudo)
        print("Análise léxica concluída")
        
        # Análise sintática
        analisador = SyntacticAnalyzer(get_table(), get_follow_set())
        erros_sintaticos = analisador.parse(lexico.table)
        print(f"Erros sintáticos: {len(erros_sintaticos)}")
        
        # Análise semântica
        analisador_semantico = AnalisadorSemantico()
        resultado_sem = analisador_semantico.analisar_tokens(lexico.table)
        erros_semanticos = resultado_sem['erros']
        tabela_simbolos = resultado_sem['tabelas_de_simbolos']
        print(f"Erros semânticos: {len(erros_semanticos)}")
        print(f"Tabela de símbolos: {bool(tabela_simbolos)}")
        
        # Separar erros fatais de avisos
        erros_fatais = []
        avisos = []
        for erro in erros_semanticos:
            if 'Aviso:' in erro.get('Mensagem', ''):
                avisos.append(erro)
            else:
                erros_fatais.append(erro)
        
        print(f"Erros fatais: {len(erros_fatais)}, Avisos: {len(avisos)}")
        
        # Geração de código MEPA (executada mesmo com avisos)
        mepa_code = []
        execution_output = []
        erro_geracao = None
        
        # Verifica se podemos gerar código (apenas erros fatais impedem)
        if not erros_sintaticos and not erros_fatais:
            try:
                print("Preparando para gerar código MEPA...")
                
                # Prepara endereços das variáveis
                current_address = 0
                address_map = {}
                
                # Primeiro: variáveis globais
                if 'global' in tabela_simbolos:
                    for symbol in tabela_simbolos['global']:
                        if symbol['Categoria'] in ('variavel', 'parametro'):
                            symbol['Endereco'] = current_address
                            address_map[symbol['Lexema']] = current_address
                            print(f"Global: {symbol['Lexema']} @ {current_address}")
                            current_address += 1
                
                # Depois: outros escopos
                for scope_name, symbols in tabela_simbolos.items():
                    if scope_name == 'global':
                        continue
                        
                    print(f"Processando escopo: {scope_name}")
                    for symbol in symbols:
                        if symbol['Categoria'] in ('variavel', 'parametro'):
                            # Se já foi mapeada globalmente, não remapear
                            if symbol['Lexema'] not in address_map:
                                symbol['Endereco'] = current_address
                                address_map[symbol['Lexema']] = current_address
                                print(f"{scope_name}: {symbol['Lexema']} @ {current_address}")
                                current_address += 1
                
                # Gera código MEPA
                print("Criando gerador de código...")
                code_gen = MEPACodeGenerator(tabela_simbolos)
                print("Gerando código MEPA...")
                mepa_code = code_gen.generate(lexico.table)
                print(f"Código gerado: {len(mepa_code)} instruções")
                
                # Se tivermos código, formatar para saída
                if mepa_code:
                    # Converter para formato serializável
                    mepa_code_serializable = []
                    for instr in mepa_code:
                        if isinstance(instr, tuple):
                            mepa_code_serializable.append(list(instr))
                        else:
                            mepa_code_serializable.append(instr)
                    mepa_code = mepa_code_serializable
                
            except Exception as e:
                import traceback
                traceback_str = traceback.format_exc()
                print(f"ERRO na geração: {traceback_str}")
                erro_geracao = traceback_str
                erros_fatais.append({
                    'Mensagem': f"Erro na geração: {str(e)}",
                    'Linha': 'N/A',
                    'Escopo': 'geração'
                })
        else:
            print("Não gerando código devido a erros fatais ou sintáticos")
        
        # Formata resposta
        resposta = {
            'tabela_lexica': lexico.table,
            'tabela_simbolos': tabela_simbolos,
            'mepa_code': mepa_code,
            'execution_output': execution_output,
            'erros': {
                'sintaxe': [{'linha': e[0], 'mensagem': e[1]} for e in erros_sintaticos],
                'semantica_erros': erros_fatais,
                'semantica_avisos': avisos
            }
        }
        
        return jsonify(resposta), 200
        
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"ERRO GERAL: {traceback_str}")
        return jsonify({
            'error': str(e),
            'traceback': traceback_str
        }), 500
    
@app.route('/alfabeto_tokens', methods=['GET'])
def alfabeto_tokens():
    try:
        tokens = obter_tokens()
        return jsonify({'tokens': tokens}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/tabela/<id>', methods=['GET'])
def tabela(id):
    try:
        file_path = find_file(f'{id}.csv')
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return jsonify({'tabela': content}), 200
    except FileNotFoundError:
        return jsonify({'error': 'Arquivo tabela.csv não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/interpretar', methods=['POST'])
def interpretador():
    try:
        # Acessa os dados JSON diretamente
        data = request.get_json()
        mepa_code = data.get('mepa_code')  # Acessa a chave diretamente
        
        print("Conteúdo recebido:", mepa_code)  # Debug
        
        # Verifica se mepa_code existe
        if not mepa_code:
            return jsonify({'error': 'mepa_code não encontrado no corpo da requisição'}), 400
        
        interpretador = MepaInterpreterDebug(mepa_code)
        resultado = interpretador.run()
        print("Resultado: ")
        print(resultado)

        return jsonify({
            "memoria": resultado['memory'],
            "pilha": resultado['stack_top'],
            'saida': resultado['saida']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
