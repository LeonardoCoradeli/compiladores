from flask import Flask, request, jsonify
from alfabeto import obter_tokens
from lexico import AnaliseLexica
from flask_cors import CORS
from utils import find_file
from sintatico import AnalisadorIntegrado
from tabela import get_table
from follow_sets import get_follow_set


app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return jsonify({'message': 'API de Análise Léxica'}),200

@app.route('/enviar_conteudo', methods=['POST'])
def enviar_conteudo():
    try:
        conteudo = request.data.decode('utf-8')  
        lexico = AnaliseLexica(obter_tokens())
        lexico.create_table(conteudo)
        
        if not conteudo:
            return jsonify({'error': 'Conteúdo não fornecido'}), 400
        
        # Utiliza o novo analisador integrado
        analisador = AnalisadorIntegrado(get_table(), get_follow_set())
        resultado_analise = analisador.analisar(lexico.table)

        print(resultado_analise)
        
        # Formata os erros semânticos para serem serializáveis em JSON,
        # pois objetos de exceção não são diretamente convertidos.
        erros_semanticos_json = [
            {'mensagem': erro.mensagem, 'linha': erro.linha} 
            for erro in resultado_analise['semantica']
        ]
        
        # Monta a resposta final com os resultados da análise
        resposta = {
            'message': 'Conteúdo processado com sucesso',
            'tabela_lexica': lexico.table,
            'resultado_analise': {
                'sintaxe': resultado_analise['sintaxe'],
                'semantica': erros_semanticos_json,
                'sucesso': resultado_analise['sucesso']
            }
        }
        
        return jsonify(resposta), 200
    except Exception as e:
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
