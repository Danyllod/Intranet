import json
import os
import base64
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from datetime import datetime, date, time
from .extensions import db  # mesmo db usado no projeto
from .models import ReservaSala, SolicitacaoCancelamento


main_bp = Blueprint('main', __name__)

# Dicionários para tradução de data para português
DIAS_SEMANA = {
    'Monday': 'Segunda',
    'Tuesday': 'Terça',
    'Wednesday': 'Quarta',
    'Thursday': 'Quinta',
    'Friday': 'Sexta',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

MESES = {
    'January': 'Janeiro',
    'February': 'Fevereiro',
    'March': 'Março',
    'April': 'Abril',
    'May': 'Maio',
    'June': 'Junho',
    'July': 'Julho',
    'August': 'Agosto',
    'September': 'Setembro',
    'October': 'Outubro',
    'November': 'Novembro',
    'December': 'Dezembro'
}

def traduzir_data_pt(data_obj):
    """Traduz a data para português com dia da semana"""
    dia_semana = DIAS_SEMANA.get(data_obj.strftime('%A'), '')
    dia_mes = data_obj.day
    mes = MESES.get(data_obj.strftime('%B'), '')
    return f"{dia_semana}, {dia_mes} de {mes}"

# Registrar filtro customizado
@main_bp.app_template_filter('traduzir_data_pt')
def filtro_traduzir_data_pt(data_obj):
    return traduzir_data_pt(data_obj)

# Caminho do arquivo de dados da revista
REVISTA_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'revista_data.json')
REVISTA_IMAGES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'imagens', 'revista_pages')
EDICOES_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'edicoes_data.json')
VIEWS_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'views_data.json')

# Criar pasta de imagens se não existir
os.makedirs(REVISTA_IMAGES_PATH, exist_ok=True)

def carregar_revista_data():
    """Carrega os dados da revista do arquivo JSON"""
    try:
        with open(REVISTA_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@main_bp.route('/')
def index():
    return render_template('index.html', title='Início')

@main_bp.route('/noticias')
def noticias():
    return render_template('noticias.html', title='Notícias')

@main_bp.route('/categoria/<cat>')
def categoria(cat):
    categorias_validas = ['tecnologia', 'politica', 'esportes', 'entretenimento', 'mundo', 'outros']
    if cat not in categorias_validas:
        return render_template('404.html'), 404
    return render_template('categoria.html', categoria=cat, title=cat.title())

@main_bp.route('/sobre')
def sobre():
    return render_template('about.html', title='Sobre Nós')

@main_bp.route('/artigo/<int:id>')
def artigo(id):
    artigo_data = {
        'id': id,
        'titulo': f'Artigo Detalhado Número {id}',
        'categoria': 'Tecnologia',
        'autor': 'Redação Conexão CRESM',
        'data': '14 de Janeiro de 2026',
        'conteudo': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt...',
        'views': 1500
    }
    return render_template('artigo.html', artigo=artigo_data, title=artigo_data['titulo'])

@main_bp.route('/jornal')
def jornal():
    return render_template('jornal.html', title='Jornal CRESM')

@main_bp.route('/revista')
def revista():
    revista_data = carregar_revista_data()
    edicoes = obter_edicoes_disponiveis()
    return render_template('revista.html', title='Revista CRESM', revista=revista_data, edicoes=edicoes, edicao_atual='janeiro')

def obter_edicoes_disponiveis():
    """Retorna lista de edições disponíveis"""
    try:
        with open(EDICOES_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('edicoes', [])
    except FileNotFoundError:
        # Se o arquivo não existir, retorna as edições padrão
        return [
            {'id': 'janeiro', 'nome': 'Janeiro', 'mes': 1},
        ]

@main_bp.route('/editar-revista')
def editar_revista():
    """Página para editar a revista"""
    return render_template('editar-revista.html', title='Editar Revista')

@main_bp.route('/api/salvar-revista', methods=['POST'])
def salvar_revista_api():
    """Salva os dados da revista com imagens"""
    try:
        dados = request.get_json()
        pages = dados.get('pages', [])
        
        print(f"[DEBUG] Salvando revista com {len(pages)} páginas")
        
        # Processar imagens
        revista_processada = {
            'pages': [],
            'saved_at': datetime.now().isoformat()
        }
        
        for idx, page in enumerate(pages):
            page_data = {}
            
            # Se a página tem uma imagem em base64
            if page.get('image') and page['image'].startswith('data:image/png;base64,'):
                # Extrair e salvar a imagem
                image_base64 = page['image'].split(',')[1]
                image_bytes = base64.b64decode(image_base64)
                
                # Nome do arquivo
                filename = f'page_{idx + 1}_{int(datetime.now().timestamp())}.png'
                filepath = os.path.join(REVISTA_IMAGES_PATH, filename)
                
                # Salvar imagem
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                
                # Salvar caminho relativo
                page_data['image'] = f'/static/imagens/revista_pages/{filename}'
                print(f"[DEBUG] Página {idx + 1} salva: {filename}")
            else:
                # Se já tem um caminho salvo, mantém
                if page.get('image'):
                    page_data['image'] = page['image']
            
            revista_processada['pages'].append(page_data)
        
        # Salvar dados no JSON
        with open(REVISTA_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(revista_processada, f, ensure_ascii=False, indent=2)
        
        print(f"[DEBUG] Revista salva com sucesso!")
        return jsonify({'success': True, 'message': 'Revista salva com sucesso!'})
    except Exception as e:
        print(f"[ERROR] Erro ao salvar: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/carregar-paginas-revista', methods=['GET'])
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

@main_bp.route('/api/carregar-edicoes', methods=['GET'])
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

@main_bp.route('/api/salvar-edicoes', methods=['POST'])
def salvar_edicoes():
    """Salva a lista de edições"""
    try:
        dados = request.get_json()
        edicoes = dados.get('edicoes', [])
        
        print(f"[DEBUG] Salvando {len(edicoes)} edições")
        
        edicoes_data = {
            'edicoes': edicoes,
            'saved_at': datetime.now().isoformat()
        }
        
        # Salvar dados no JSON
        with open(EDICOES_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(edicoes_data, f, ensure_ascii=False, indent=2)
        
        print(f"[DEBUG] Edições salvas com sucesso!")
        return jsonify({'success': True, 'message': 'Edições salvas com sucesso!'})
    except Exception as e:
        print(f"[ERROR] Erro ao salvar edições: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/carregar-visualizacoes', methods=['GET'])
def carregar_visualizacoes():
    """Carrega os dados de visualizações das edições"""
    try:
        with open(VIEWS_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            visualizacoes = data.get('visualizacoes', {})
        
        return jsonify({
            'success': True,
            'visualizacoes': visualizacoes
        })
    except FileNotFoundError:
        return jsonify({
            'success': True,
            'visualizacoes': {}
        })
    except Exception as e:
        print(f"[ERROR] Erro ao carregar visualizações: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/registrar-visualizacao', methods=['POST'])
def registrar_visualizacao():
    """Registra uma visualização de uma edição"""
    try:
        dados = request.get_json()
        edicao_id = dados.get('edicao_id')
        
        if not edicao_id:
            return jsonify({'success': False, 'error': 'ID da edição não fornecido'}), 400
        
        # Carregar dados existentes
        try:
            with open(VIEWS_DATA_PATH, 'r', encoding='utf-8') as f:
                views_data = json.load(f)
        except FileNotFoundError:
            views_data = {'visualizacoes': {}}
        
        # Incrementar visualização
        if 'visualizacoes' not in views_data:
            views_data['visualizacoes'] = {}
        
        if edicao_id not in views_data['visualizacoes']:
            views_data['visualizacoes'][edicao_id] = 0
        
        views_data['visualizacoes'][edicao_id] += 1
        views_data['saved_at'] = datetime.now().isoformat()
        
        # Salvar dados
        with open(VIEWS_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(views_data, f, ensure_ascii=False, indent=2)
        
        print(f"[DEBUG] Visualização registrada para {edicao_id}")
        return jsonify({'success': True, 'message': 'Visualização registrada'})
    except Exception as e:
        print(f"[ERROR] Erro ao registrar visualização: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
@main_bp.route('/agenda-salas')
def agenda_salas():
    # Ordena por data e horário - mostra reservas aprovadas e também as canceladas
    # (permitindo que o usuário veja na agenda quando um horário foi liberado)
    reservas = (ReservaSala.query
                .filter(ReservaSala.status.in_(['aprovado', 'cancelado']))
                .order_by(ReservaSala.data.asc(),
                        ReservaSala.hora_inicio.asc())
                .all())
    hoje = date.today().isoformat()
    return render_template('agenda_salas.html',
                        title='Agenda de Salas',
                        reservas=reservas,
                        hoje=hoje)


def verificar_conflito_horario(data, hora_inicio, hora_fim, local):
    """
    Verifica se há conflito de horário para a mesma sala.
    Considera apenas reservas APROVADAS.
    Retorna True se há conflito, False se não há.
    """
    # Busca todas as reservas APROVADAS para a mesma sala na mesma data
    reservas_existentes = ReservaSala.query.filter(
        ReservaSala.data == data,
        ReservaSala.local == local,
        ReservaSala.status == 'aprovado'  # Apenas reservas aprovadas
    ).all()
    
    # Verifica se há sobreposição de horários
    for reserva in reservas_existentes:
        # Se a hora de início da nova reserva é antes do fim da existente
        # E a hora de fim da nova reserva é depois do início da existente
        if hora_inicio < reserva.hora_fim and hora_fim > reserva.hora_inicio:
            return True  # Há conflito
    
    return False  # Sem conflito


@main_bp.route('/agenda-salas/solicitar', methods=['GET', 'POST'])
def solicitar_reserva_sala():
    erro = None
    sucesso = None
    
    if request.method == 'POST':
        data_str = request.form.get('data')              # yyyy-mm-dd
        hora_inicio_str = request.form.get('hora_inicio')  # hh:mm
        hora_fim_str = request.form.get('hora_fim')        # hh:mm
        reservado_por = request.form.get('reservado_por')
        local = request.form.get('local')
        evento = request.form.get('evento')
        participantes = request.form.get('participantes')

        # Converte para tipos Python
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fim = datetime.strptime(hora_fim_str, '%H:%M').time()

        # Validações adicionais
        hoje = date.today()
        if data < hoje:
            erro = "A data da reserva não pode ser anterior a hoje."
            return render_template('solicitar_reserva_sala.html',
                                 title='Solicitar Reserva de Sala',
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
            return render_template('solicitar_reserva_sala.html',
                                 title='Solicitar Reserva de Sala',
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
            return render_template('solicitar_reserva_sala.html',
                                 title='Solicitar Reserva de Sala',
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

        return render_template('solicitar_reserva_sala.html',
                             title='Solicitar Reserva de Sala',
                             sucesso=sucesso)

    # GET: exibe o formulário
    hoje = date.today().isoformat()
    return render_template('solicitar_reserva_sala.html',
                        title='Solicitar Reserva de Sala',
                        erro=erro,
                        hoje=hoje)


@main_bp.route('/agenda-salas/gerenciar', methods=['GET'])
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
    
    return render_template('gerenciar_solicitacoes.html',
                        title='Gerenciar Solicitações',
                        solicitacoes=solicitacoes,
                        cancelamentos=cancelamentos,
                        incluir_historico=incluir_historico,
                        aba_ativa=aba_ativa)


@main_bp.route('/agenda-salas/aprovar/<int:id>', methods=['POST'])
def aprovar_solicitacao(id):
    """Aprova uma solicitação de reserva"""
    solicitacao = ReservaSala.query.get_or_404(id)
    aprovado_por = request.form.get('aprovado_por', 'Admin')
    
    solicitacao.status = 'aprovado'
    solicitacao.data_decisao = datetime.now()
    solicitacao.aprovado_por = aprovado_por
    
    db.session.commit()
    
    return redirect(url_for('main.gerenciar_solicitacoes'))


@main_bp.route('/agenda-salas/negar/<int:id>', methods=['POST'])
def negar_solicitacao(id):
    """Nega uma solicitação de reserva"""
    solicitacao = ReservaSala.query.get_or_404(id)
    motivo = request.form.get('motivo_negacao', 'Sem justificativa')
    
    solicitacao.status = 'negado'
    solicitacao.data_decisao = datetime.now()
    solicitacao.motivo_negacao = motivo
    
    db.session.commit()
    
    return redirect(url_for('main.gerenciar_solicitacoes'))


@main_bp.route('/agenda-salas/gerenciar-confirmacoes', methods=['GET'])
def gerenciar_confirmacoes():
    """Mostra todas as reuniões aprovadas para confirmar/cancelar a partir de hoje"""
    today = date.today()
    reunioes = (ReservaSala.query
               .filter_by(status='aprovado')
               .filter(ReservaSala.data >= today)
               .order_by(ReservaSala.data.asc(),
                        ReservaSala.hora_inicio.asc())
               .all())
    
    return render_template('gerenciar_confirmacoes.html',
                        title='Gerenciar Confirmações',
                        reunioes=reunioes)


@main_bp.route('/agenda-salas/confirmar/<int:id>', methods=['POST'])
def confirmar_reuniao(id):
    """Confirma uma reunião"""
    reuniao = ReservaSala.query.get_or_404(id)
    reuniao.confirmado = True
    db.session.commit()
    
    return redirect(url_for('main.gerenciar_confirmacoes'))


@main_bp.route('/agenda-salas/cancelar/<int:id>', methods=['POST'])
def cancelar_reuniao(id):
    """Cancela uma reunião e libera o horário para novas reservas."""
    reuniao = ReservaSala.query.get_or_404(id)
    reuniao.confirmado = False
    reuniao.status = 'cancelado'
    reuniao.data_decisao = datetime.now()
    db.session.commit()
    
    return redirect(url_for('main.gerenciar_confirmacoes'))


@main_bp.route('/agenda-salas/solicitar-cancelamento', methods=['GET', 'POST'])
def solicitar_cancelamento_reserva():
    """Permite solicitar o cancelamento de uma reserva aprovada"""
    erro = None
    sucesso = False
    reserva = None
    reservas = []
    today = date.today()
    
    if request.method == 'POST':
        reserva_id = request.form.get('reserva_id')
        solicitante = request.form.get('solicitante', '').strip()
        
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
    
    return render_template('solicitar_cancelamento_reserva.html',
                        title='Solicitar Cancelamento',
                        erro=erro,
                        sucesso=sucesso,
                        reserva=reserva,
                        reservas=reservas)


@main_bp.route('/agenda-salas/aprovar-cancelamento/<int:id>', methods=['POST'])
def aprovar_cancelamento(id):
    """Aprova uma solicitação de cancelamento"""
    solicitacao = SolicitacaoCancelamento.query.get_or_404(id)
    aprovado_por = request.form.get('aprovado_por', 'Admin')
    
    # Atualiza a solicitação
    solicitacao.status = 'aprovado'
    solicitacao.data_decisao = datetime.now()
    solicitacao.aprovado_por = aprovado_por
    
    # Atualiza a reserva associada
    reserva = solicitacao.reserva
    reserva.status = 'cancelado'
    reserva.confirmado = False
    
    db.session.commit()
    
    return redirect(url_for('main.gerenciar_solicitacoes', tab='cancelamentos'))


@main_bp.route('/agenda-salas/negar-cancelamento/<int:id>', methods=['POST'])
def negar_cancelamento(id):
    """Nega uma solicitação de cancelamento"""
    solicitacao = SolicitacaoCancelamento.query.get_or_404(id)
    motivo = request.form.get('motivo_negacao', 'Sem justificativa')
    
    solicitacao.status = 'negado'
    solicitacao.data_decisao = datetime.now()
    solicitacao.motivo_negacao = motivo
    
    db.session.commit()
    
    return redirect(url_for('main.gerenciar_solicitacoes', tab='cancelamentos'))
