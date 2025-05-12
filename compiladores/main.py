from flask import Flask, request, jsonify
from alfabeto import obter_tokens
from lexico import AnaliseLexica
from sintatico import Grammar,Parser, ParseError
from flask_cors import CORS
from utils import find_file


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
        
        grammar = Grammar()
        parser = Parser(grammar)

        parser.parse(lexico.table['token'])
        
        return jsonify({'message': 'Conteúdo processado com sucesso', 'tabela':lexico.table, 'sintatico': "Analise Sintatica concluida"}), 200
    except ParseError as e:
        return jsonify({'message': 'Conteúdo processado com sucesso', 
                        'tabela':lexico.table, 
                        'sintatico': f'Esperado: {e.expected}, encontrado: {e.found}, posição: {e.position}'}), 200
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
