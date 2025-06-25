from flask import Flask, request, jsonify
from alfabeto import obter_tokens
from flask_cors import CORS
from utils import find_file
from tabela import get_table
from follow_sets import get_follow_set
from lexico import AnaliseLexica
from sintatico import SyntacticAnalyzer
from semantico import AnalisadorSemantico

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

        # Análise sintática
        analisador = SyntacticAnalyzer(get_table(), get_follow_set())
        erros_sintaticos = analisador.parse(lexico.table)

        erros_sintaticos_json = [
            {'mensagem': erro[1], 'linha': erro[0]}
            for erro in erros_sintaticos
        ]

        # Análise semântica
        analisador_semantico = AnalisadorSemantico()
        resultado_sem = analisador_semantico.analisar_tokens(lexico.table)
        erros_semanticos = resultado_sem['erros']
        tabela_simbolos = resultado_sem['tabelas_de_simbolos']

        print(tabela_simbolos)

        # Os dicionários de erro vêm com chaves 'Linha','Escopo','Mensagem'
        erros_semanticos_json = [
            {
                'mensagem': erro['Mensagem'],
                'linha': erro['Linha'],
                'escopo': erro.get('Escopo')
            }
            for erro in erros_semanticos
        ]

        sucesso = not erros_sintaticos and not erros_semanticos

        resposta = {
            'message': 'Conteúdo processado com sucesso',
            'tabela_lexica': lexico.table,
            'tabela_simbolos': tabela_simbolos,
            'resultado_analise': {
                'sintaxe': erros_sintaticos_json,
                'semantica': erros_semanticos_json,
                'sucesso': sucesso
            }
        }

        return jsonify(resposta), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

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

    
if __name__ == '__main__':
    app.run(debug=True)
