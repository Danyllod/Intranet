from flask import render_template, request, jsonify
from . import revista_bp
from .services import (
    carregar_revista_data,
    salvar_revista_com_imagens,
    obter_edicoes_disponiveis,
    salvar_edicoes,
    carregar_visualizacoes,
    registrar_visualizacao
)


@revista_bp.route('/')
def revista():
    revista_data = carregar_revista_data()
    edicoes = obter_edicoes_disponiveis()
    return render_template('revista/revista.html', title='Revista CRESM', revista=revista_data, edicoes=edicoes, edicao_atual='janeiro')


@revista_bp.route('/editar')
def editar_revista():
    """Página para editar a revista"""
    return render_template('revista/editar-revista.html', title='Editar Revista')


@revista_bp.route('/api/salvar', methods=['POST'])
def salvar_revista_api():
    """Salva os dados da revista com imagens"""
    try:
        dados = request.get_json()
        pages = dados.get('pages', [])
        
        print(f"[DEBUG] Salvando revista com {len(pages)} páginas")
        salvar_revista_com_imagens(pages)
        
        return jsonify({'success': True, 'message': 'Revista salva com sucesso!'})
    except Exception as e:
        print(f"[ERROR] Erro ao salvar: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@revista_bp.route('/api/carregar-paginas', methods=['GET'])
def carregar_paginas_revista():
    """Carrega as páginas da revista"""
    try:
        revista_data = carregar_revista_data()
        pages = revista_data.get('pages', [])
        
        print(f"[DEBUG] Carregadas {len(pages)} páginas da revista")
        
        return jsonify({
            'success': True,
            'pages': pages
        })
    except Exception as e:
        print(f"[ERROR] Erro ao carregar páginas: {str(e)}")
        return jsonify({'success': False, 'error': str(e), 'pages': []}), 500


@revista_bp.route('/api/carregar-edicoes', methods=['GET'])
def carregar_edicoes():
    """Carrega lista de edições disponíveis"""
    try:
        edicoes = obter_edicoes_disponiveis()
        return jsonify({
            'success': True,
            'edicoes': edicoes
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@revista_bp.route('/api/salvar-edicoes', methods=['POST'])
def salvar_edicoes_api():
    """Salva a lista de edições"""
    try:
        dados = request.get_json()
        edicoes = dados.get('edicoes', [])
        
        print(f"[DEBUG] Salvando {len(edicoes)} edições")
        salvar_edicoes(edicoes)
        
        return jsonify({'success': True, 'message': 'Edições salvas com sucesso!'})
    except Exception as e:
        print(f"[ERROR] Erro ao salvar edições: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@revista_bp.route('/api/carregar-visualizacoes', methods=['GET'])
def carregar_visualizacoes_api():
    """Carrega os dados de visualizações das edições"""
    try:
        visualizacoes = carregar_visualizacoes()
        
        return jsonify({
            'success': True,
            'visualizacoes': visualizacoes
        })
    except Exception as e:
        print(f"[ERROR] Erro ao carregar visualizações: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@revista_bp.route('/api/registrar-visualizacao', methods=['POST'])
def registrar_visualizacao_api():
    """Registra uma visualização de uma edição"""
    try:
        dados = request.get_json()
        edicao_id = dados.get('edicao_id')
        
        if not edicao_id:
            return jsonify({'success': False, 'error': 'ID da edição não fornecido'}), 400
        
        registrar_visualizacao(edicao_id)
        return jsonify({'success': True, 'message': 'Visualização registrada'})
    except Exception as e:
        print(f"[ERROR] Erro ao registrar visualização: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
