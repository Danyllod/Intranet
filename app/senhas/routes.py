"""
Rotas do módulo de Painel de Senhas
Endpoints para interface html e APIs de atendimento.
"""

from flask import render_template, request, jsonify, redirect, url_for
from . import senhas_bp
from app.models import db, Senha
from app.auth.decorators import admin_required, basico_required
from .services import (
    gerar_senha,
    chamar_proxima_senha,
    rechamar_senha,
    finalizar_senha,
    cancelar_senha,
    marcar_ausente_senha,
    toggle_prioridade_senha,
    obter_status_painel,
    obter_fila_do_dia,
    obter_ultimas_chamadas,
    obter_relatorio_diario,
    obter_relatorio_mensal
)


# ============================================================================
# PÁGINAS HTML
# ============================================================================

@senhas_bp.get("/recepcao")
@basico_required
def recepcao():
    """Página de recepção para geração de senhas"""
    return render_template(
        "senhas/recepcao.html",
        title="Recepção - Painel de Senhas",
        include_navbar=False
    )


@senhas_bp.get("/atendimento")
@basico_required
def atendimento():
    """Página de atendimento para agentes"""
    return render_template(
        "senhas/atendimento.html",
        title="Atendimento - Painel de Senhas",
        include_navbar=False
    )


@senhas_bp.get("/painel")
def painel():
    """Painel público de visualização de senhas - sem autenticação"""
    return render_template(
        "senhas/painel.html",
        title="Painel de Senhas",
        include_navbar=False
    )


@senhas_bp.get("/relatorios")
@admin_required
def relatorios():
    """Redireciona para relatórios diários - apenas administrador"""
    return redirect(url_for('senhas.relatorios_diario'))


@senhas_bp.get("/relatorios/diario")
@admin_required
def relatorios_diario():
    """Página de relatórios diários - apenas administrador"""
    return render_template(
        "senhas/relatorios.html",
        title="Relatórios Diários - Painel de Senhas",
        tipo_relatorio="diario",
        include_navbar=False
    )


@senhas_bp.get("/relatorios/mensal")
@admin_required
def relatorios_mensal():
    """Página de relatórios mensais - apenas administrador"""
    return render_template(
        "senhas/relatorios.html",
        title="Relatórios Mensais - Painel de Senhas",
        tipo_relatorio="mensal",
        include_navbar=False
    )


# ============================================================================
# AÇÕES (POST)
# ============================================================================

@senhas_bp.post("/recepcao/gerar")
def gerar():
    """Gera nova senha"""
    try:
        tipo = request.form.get("tipo", "nova_consulta")
        is_prioridade = request.form.get("is_prioridade", "false").lower() == "true"
        resultado = gerar_senha(tipo=tipo, is_prioridade=is_prioridade)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar senha: {str(e)}'
        }), 400


@senhas_bp.post("/atendimento/proxima")
def proxima():
    """Chama a próxima senha na fila. Se houver senha em atendimento, finaliza-a primeiro."""
    try:
        guiche = request.form.get("guiche")
        usuario = request.form.get("usuario")
        
        # Auto-finalizar senha anterior se houver uma em atendimento
        from datetime import date
        hoje = date.today()
        senha_em_atendimento = Senha.query.filter(
            Senha.data_referencia == hoje,
            Senha.status.in_(['chamada', 'rechamada'])
        ).order_by(Senha.chamada_em.desc()).first()
        
        if senha_em_atendimento:
            senha_em_atendimento.marcar_como_finalizada()
            db.session.commit()
        
        resultado = chamar_proxima_senha(guiche=guiche, usuario=usuario)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao chamar próxima senha: {str(e)}'
        }), 400


@senhas_bp.post("/atendimento/rechamar/<int:senha_id>")
def rechamar(senha_id):
    """Rechamada de uma senha"""
    try:
        guiche = request.form.get("guiche")
        usuario = request.form.get("usuario")
        resultado = rechamar_senha(senha_id, guiche=guiche, usuario=usuario)
        
        if not resultado['success']:
            return jsonify(resultado), 404
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao rechamar senha: {str(e)}'
        }), 400


@senhas_bp.post("/atendimento/finalizar/<int:senha_id>")
def finalizar(senha_id):
    """Finaliza atendimento de uma senha"""
    try:
        usuario = request.form.get("usuario")
        resultado = finalizar_senha(senha_id, usuario=usuario)
        
        if not resultado['success']:
            return jsonify(resultado), 404
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao finalizar senha: {str(e)}'
        }), 400


@senhas_bp.post("/atendimento/cancelar/<int:senha_id>")
def cancelar(senha_id):
    """Cancela uma senha"""
    try:
        usuario = request.form.get("usuario")
        motivo = request.form.get("motivo")
        resultado = cancelar_senha(senha_id, usuario=usuario, motivo=motivo)
        
        if not resultado['success']:
            return jsonify(resultado), 404
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao cancelar senha: {str(e)}'
        }), 400


@senhas_bp.post("/atendimento/ausente/<int:senha_id>")
def marcar_ausente(senha_id):
    """Marca uma senha como ausente"""
    try:
        usuario = request.form.get("usuario")
        resultado = marcar_ausente_senha(senha_id, usuario=usuario)
        
        if not resultado['success']:
            return jsonify(resultado), 404
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao marcar ausente: {str(e)}'
        }), 400


@senhas_bp.post("/atendimento/toggle-prioridade/<int:senha_id>")
def toggle_prioridade(senha_id):
    """Alterna prioridade de uma senha"""
    try:
        resultado = toggle_prioridade_senha(senha_id)
        
        if not resultado['success']:
            return jsonify(resultado), 404
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao alterar prioridade: {str(e)}'
        }), 400


# ============================================================================
# APIS JSON (GET)
# ============================================================================

@senhas_bp.get("/api/painel-status")
def api_painel_status():
    """API: Status atual do painel de atendimento"""
    try:
        status = obter_status_painel()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter status: {str(e)}'
        }), 500


@senhas_bp.get("/api/fila")
def api_fila():
    """API: Fila do dia"""
    try:
        fila = obter_fila_do_dia()
        return jsonify(fila)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter fila: {str(e)}'
        }), 500


@senhas_bp.get("/api/ultimas")
def api_ultimas():
    """API: Ultimas senhas atendidas"""
    try:
        limite = request.args.get("limite", 5, type=int)
        ultimas = obter_ultimas_chamadas(limite=limite)
        return jsonify(ultimas)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter ultimas: {str(e)}'
        }), 500


@senhas_bp.get("/api/relatorio/diario")
def api_relatorio_diario():
    """API: Relatório diário"""
    try:
        data_ref = request.args.get("data_ref")  # formato YYYY-MM-DD
        status_filtro = request.args.get("status")  # opcional: finalizada, cancelada, ausente
        
        if data_ref:
            from datetime import datetime as dt
            data_ref = dt.strptime(data_ref, "%Y-%m-%d").date()
        
        relatorio = obter_relatorio_diario(data_ref=data_ref)
        
        # Filtrar senhas por status se solicitado
        if status_filtro:
            relatorio['senhas'] = [s for s in relatorio['senhas'] if s['status'] == status_filtro]
        
        return jsonify(relatorio)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar relatório: {str(e)}'
        }), 500


@senhas_bp.get("/api/relatorio/mensal")
def api_relatorio_mensal():
    """API: Relatório mensal"""
    try:
        ano = request.args.get("ano", type=int)
        mes = request.args.get("mes", type=int)
        status_filtro = request.args.get("status")  # opcional: finalizada, cancelada, ausente
        
        relatorio = obter_relatorio_mensal(ano=ano, mes=mes)
        
        # Filtrar senhas por status se solicitado
        if status_filtro:
            relatorio['senhas'] = [s for s in relatorio['senhas'] if s['status'] == status_filtro]
        
        return jsonify(relatorio)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar relatório: {str(e)}'
        }), 500

