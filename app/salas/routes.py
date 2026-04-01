from flask import render_template, request, redirect, url_for, jsonify
from datetime import datetime, date
from . import salas_bp
from .services import verificar_conflito_horario
from ..extensions import db
from ..models import ReservaSala, SolicitacaoCancelamento


def get_request_data(key, default=None):
    """Obtém dados de request.form ou request.json"""
    if request.method == 'POST':
        # Tenta JSON primeiro
        if request.is_json:
            return request.get_json().get(key, default)
        # Se não for JSON, tenta form data
        return request.form.get(key, default)
    return default


@salas_bp.route('/')
def agenda_salas():
    # Ordena por data e horário - mostra reservas aprovadas e também as canceladas
    # (permitindo que o usuário veja na agenda quando um horário foi liberado)
    reservas = (ReservaSala.query
                .filter(ReservaSala.status.in_(['aprovado', 'cancelado']))
                .order_by(ReservaSala.data.asc(),
                        ReservaSala.hora_inicio.asc())
                .all())
    hoje = date.today().isoformat()
    return render_template('salas/agenda_salas.html',
                        title='Agenda de Salas',
                        reservas=reservas,
                        hoje=hoje)


@salas_bp.route('/solicitar', methods=['GET', 'POST'])
def solicitar_reserva_sala():
    erro = None
    sucesso = None
    
    if request.method == 'POST':
        data_str = get_request_data('data')               # yyyy-mm-dd
        hora_inicio_str = get_request_data('hora_inicio') # hh:mm
        hora_fim_str = get_request_data('hora_fim')       # hh:mm
        reservado_por = get_request_data('reservado_por')
        local = get_request_data('local')
        evento = get_request_data('evento')
        participantes = get_request_data('participantes')

        # Converte para tipos Python
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fim = datetime.strptime(hora_fim_str, '%H:%M').time()

        # Validações adicionais
        hoje = date.today()
        if data < hoje:
            erro = "A data da reserva não pode ser anterior a hoje."
            return render_template('salas/solicitar_reserva_sala.html',
                                 title='Solicitar Reserva de Sala',
                                 form={},
                                 erro=erro,
                                 hoje=hoje.isoformat(),
                                 formulario_data={
                                     'data': data_str,
                                     'hora_inicio': hora_inicio_str,
                                     'hora_fim': hora_fim_str,
                                     'reservado_por': reservado_por,
                                     'local': local,
                                     'evento': evento,
                                     'participantes': participantes
                                 })

        if hora_inicio >= hora_fim:
            erro = "O horário de início deve ser anterior ao horário de fim."
            return render_template('salas/solicitar_reserva_sala.html',
                                 title='Solicitar Reserva de Sala',
                                 form={},
                                 erro=erro,
                                 hoje=hoje.isoformat(),
                                 formulario_data={
                                     'data': data_str,
                                     'hora_inicio': hora_inicio_str,
                                     'hora_fim': hora_fim_str,
                                     'reservado_por': reservado_por,
                                     'local': local,
                                     'evento': evento,
                                     'participantes': participantes
                                 })

        # Validação de conflito de horário por sala
        if verificar_conflito_horario(data, hora_inicio, hora_fim, local):
            erro = f"Conflito de horário! Já existe uma reserva aprovada para a sala {local} neste período."
            return render_template('salas/solicitar_reserva_sala.html',
                                 title='Solicitar Reserva de Sala',
                                 form={},
                                 erro=erro,
                                 hoje=hoje.isoformat(),
                                 formulario_data={
                                     'data': data_str,
                                     'hora_inicio': hora_inicio_str,
                                     'hora_fim': hora_fim_str,
                                     'reservado_por': reservado_por,
                                     'local': local,
                                     'evento': evento,
                                     'participantes': participantes
                                 })

        # Cria nova solicitação com status 'pendente'
        nova_solicitacao = ReservaSala(
            data=data,
            reservado_por=reservado_por,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            local=local,
            evento=evento,
            participantes=participantes,
            status='pendente'  # Nova solicitação inicia como pendente
        )

        db.session.add(nova_solicitacao)
        db.session.commit()
        sucesso = True

        return render_template('salas/solicitar_reserva_sala.html',
                             title='Solicitar Reserva de Sala',
                             form={},
                             sucesso=sucesso)

    # GET: exibe o formulário
    hoje = date.today().isoformat()
    return render_template('salas/solicitar_reserva_sala.html',
                        title='Solicitar Reserva de Sala',
                        form={},
                        erro=erro,
                        hoje=hoje)


@salas_bp.route('/gerenciar', methods=['GET'])
def gerenciar_solicitacoes():
    """Mostra todas as solicitações pendentes e histórico de aprovações/negações"""
    incluir_historico = request.args.get('historico', 'false').lower() == 'true'
    aba_ativa = request.args.get('tab', 'reservas')
    
    if incluir_historico:
        # Mostra pendentes + histórico (aprovadas e negadas)
        solicitacoes = (ReservaSala.query
                       .order_by(ReservaSala.data_solicitacao.desc())
                       .all())
    else:
        # Mostra apenas pendentes
        solicitacoes = (ReservaSala.query
                       .filter_by(status='pendente')
                       .order_by(ReservaSala.data_solicitacao.desc())
                       .all())
    
    # Carrega solicitações de cancelamento
    if incluir_historico:
        cancelamentos = (SolicitacaoCancelamento.query
                        .order_by(SolicitacaoCancelamento.data_solicitacao.desc())
                        .all())
    else:
        cancelamentos = (SolicitacaoCancelamento.query
                        .filter_by(status='pendente')
                        .order_by(SolicitacaoCancelamento.data_solicitacao.desc())
                        .all())
    
    return render_template('salas/gerenciar_solicitacoes.html',
                        title='Gerenciar Solicitações',
                        solicitacoes=solicitacoes,
                        cancelamentos=cancelamentos,
                        incluir_historico=incluir_historico,
                        aba_ativa=aba_ativa)


@salas_bp.route('/aprovar/<int:id>', methods=['POST'])
def aprovar_solicitacao(id):
    """Aprova uma solicitação de reserva"""
    solicitacao = ReservaSala.query.get_or_404(id)
    aprovado_por = get_request_data('aprovado_por', 'Admin')
    
    solicitacao.status = 'aprovado'
    solicitacao.data_decisao = datetime.now()
    solicitacao.aprovado_por = aprovado_por
    
    db.session.commit()
    
    return redirect(url_for('salas.gerenciar_solicitacoes'))


@salas_bp.route('/negar/<int:id>', methods=['POST'])
def negar_solicitacao(id):
    """Nega uma solicitação de reserva"""
    solicitacao = ReservaSala.query.get_or_404(id)
    motivo = get_request_data('motivo_negacao', 'Sem justificativa')
    
    solicitacao.status = 'negado'
    solicitacao.data_decisao = datetime.now()
    solicitacao.motivo_negacao = motivo
    
    db.session.commit()
    
    return redirect(url_for('salas.gerenciar_solicitacoes'))


@salas_bp.route('/gerenciar-confirmacoes', methods=['GET'])
def gerenciar_confirmacoes():
    """Mostra todas as reuniões aprovadas para confirmar/cancelar a partir de hoje"""
    today = date.today()
    reunioes = (ReservaSala.query
               .filter_by(status='aprovado')
               .filter(ReservaSala.data >= today)
               .order_by(ReservaSala.data.asc(),
                        ReservaSala.hora_inicio.asc())
               .all())
    
    return render_template('salas/gerenciar_confirmacoes.html',
                        title='Gerenciar Confirmações',
                        reunioes=reunioes)


@salas_bp.route('/confirmar/<int:id>', methods=['POST'])
def confirmar_reuniao(id):
    """Confirma uma reunião"""
    reuniao = ReservaSala.query.get_or_404(id)
    reuniao.confirmado = True
    db.session.commit()
    
    return redirect(url_for('salas.gerenciar_confirmacoes'))


@salas_bp.route('/cancelar/<int:id>', methods=['POST'])
def cancelar_reuniao(id):
    """Cancela uma reunião e libera o horário para novas reservas."""
    reuniao = ReservaSala.query.get_or_404(id)
    reuniao.confirmado = False
    reuniao.status = 'cancelado'
    reuniao.data_decisao = datetime.now()
    db.session.commit()
    
    return redirect(url_for('salas.gerenciar_confirmacoes'))


@salas_bp.route('/solicitar-cancelamento', methods=['GET', 'POST'])
def solicitar_cancelamento_reserva():
    """Permite solicitar o cancelamento de uma reserva aprovada"""
    erro = None
    sucesso = False
    reserva = None
    reservas = []
    today = date.today()
    
    if request.method == 'POST':
        reserva_id = get_request_data('reserva_id')
        solicitante = get_request_data('solicitante', '').strip()
        
        # Validações
        if not reserva_id:
            erro = "Por favor, selecione uma reserva."
        elif not solicitante:
            erro = "Por favor, informe seu nome."
        else:
            # Verifica se a reserva existe e está aprovada
            reserva_obj = ReservaSala.query.get(reserva_id)
            if not reserva_obj:
                erro = "Reserva não encontrada."
            elif reserva_obj.status != 'aprovado':
                erro = "Apenas reservas aprovadas podem ser canceladas."
            else:
                # Cria a solicitação de cancelamento
                try:
                    solicitacao = SolicitacaoCancelamento(
                        reserva_id=reserva_id,
                        solicitante=solicitante,
                        motivo=f"Cancelamento solicitado por {solicitante}",
                        status='pendente'
                    )
                    db.session.add(solicitacao)
                    db.session.commit()
                    sucesso = True
                except Exception as e:
                    db.session.rollback()
                    erro = f"Erro ao criar solicitação: {str(e)}"
    
    if request.method == 'GET':
        # Carrega lista de reservas aprovadas a partir de hoje
        reservas = (ReservaSala.query
                   .filter_by(status='aprovado')
                   .filter(ReservaSala.data >= today)
                   .order_by(ReservaSala.data.asc(), ReservaSala.hora_inicio.asc())
                   .all())
    
    return render_template('salas/solicitar_cancelamento_reserva.html',
                        title='Solicitar Cancelamento',
                        erro=erro,
                        sucesso=sucesso,
                        reserva=reserva,
                        reservas=reservas)


@salas_bp.route('/aprovar-cancelamento/<int:id>', methods=['POST'])
def aprovar_cancelamento(id):
    """Aprova uma solicitação de cancelamento"""
    solicitacao = SolicitacaoCancelamento.query.get_or_404(id)
    aprovado_por = get_request_data('aprovado_por', 'Admin')
    
    # Atualiza a solicitação
    solicitacao.status = 'aprovado'
    solicitacao.data_decisao = datetime.now()
    solicitacao.aprovado_por = aprovado_por
    
    # Atualiza a reserva associada
    reserva = solicitacao.reserva
    reserva.status = 'cancelado'
    reserva.confirmado = False
    
    db.session.commit()
    
    return redirect(url_for('salas.gerenciar_solicitacoes', tab='cancelamentos'))


@salas_bp.route('/negar-cancelamento/<int:id>', methods=['POST'])
def negar_cancelamento(id):
    """Nega uma solicitação de cancelamento"""
    solicitacao = SolicitacaoCancelamento.query.get_or_404(id)
    motivo = get_request_data('motivo_negacao', 'Sem justificativa')
    
    solicitacao.status = 'negado'
    solicitacao.data_decisao = datetime.now()
    solicitacao.motivo_negacao = motivo
    
    db.session.commit()
    
    return redirect(url_for('salas.gerenciar_solicitacoes', tab='cancelamentos'))
