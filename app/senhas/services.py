"""
Services para o módulo de Painel de Senhas
Contém toda a lógica de negócio para gerenciamento de fila e atendimento.
"""

from datetime import datetime, date
from app.models import db, Senha, HistoricoChamada


def gerar_senha(tipo="nova_consulta", is_prioridade=False):
    """
    Gera uma nova senha no formato A00X.
    
    Args:
        tipo (str): Tipo de consulta - 'primeira_consulta', 'nova_consulta', 'retorno', 'interconsulta'
        is_prioridade (bool): Se a senha é prioritária
    
    Returns:
        dict: Informações da senha gerada ou erro
    """
    try:
        prefixo = 'A'
        hoje = date.today()
        
        # Buscar última sequência do dia
        ultima_senha = Senha.query.filter(
            Senha.data_referencia == hoje,
            Senha.numero.startswith(prefixo)
        ).order_by(Senha.sequencia_dia.desc()).first()
        
        sequencia = (ultima_senha.sequencia_dia + 1) if ultima_senha else 1
        numero = f"{prefixo}{sequencia:03d}"
        
        # Criar nova senha
        nova_senha = Senha(
            numero=numero,
            sequencia_dia=sequencia,
            tipo=tipo,
            is_prioridade=is_prioridade,
            status='aguardando',
            data_referencia=hoje
        )
        
        db.session.add(nova_senha)
        db.session.commit()
        
        # Contar posição na fila
        # Prioridades aparecem primeiro, depois ordem de sequência
        posicao_fila = Senha.query.filter(
            Senha.data_referencia == hoje,
            Senha.status == 'aguardando'
        ).filter(
            db.or_(
                Senha.is_prioridade == True,
                db.and_(Senha.is_prioridade == False, Senha.sequencia_dia < sequencia)
            )
        ).count() + 1
        
        # Contar total de senhas aguardando
        total_fila = Senha.query.filter(
            Senha.data_referencia == hoje,
            Senha.status == 'aguardando'
        ).count()
        
        return {
            'success': True,
            'senha_id': nova_senha.id,
            'numero': nova_senha.numero,
            'tipo': nova_senha.tipo,
            'is_prioridade': nova_senha.is_prioridade,
            'posicao_fila': posicao_fila,
            'total_fila': total_fila,
            'message': f'Senha {numero} gerada com sucesso'
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Erro ao gerar senha: {str(e)}'
        }


def buscar_proxima_senha():
    """
    Busca a próxima senha na fila segundo prioridades.
    Prioriza senhas marcadas como prioridade, depois ordem de sequência.
    
    Returns:
        Senha: Objeto da próxima senha ou None
    """
    hoje = date.today()
    
    # Buscar próxima prioritária não chamada
    senha = Senha.query.filter(
        Senha.data_referencia == hoje,
        Senha.is_prioridade == True,
        Senha.status == 'aguardando'
    ).order_by(Senha.sequencia_dia.asc()).first()
    
    # Se não houver prioritária, buscar normal por sequência
    if not senha:
        senha = Senha.query.filter(
            Senha.data_referencia == hoje,
            Senha.is_prioridade == False,
            Senha.status == 'aguardando'
        ).order_by(Senha.sequencia_dia.asc()).first()
    
    return senha


def chamar_proxima_senha(guiche=None, usuario=None):
    """
    Chama a próxima senha na fila.
    
    Args:
        guiche (str): Local de atendimento
        usuario (str): Agente que chamou
    
    Returns:
        dict: Informações da senha chamada ou erro
    """
    try:
        senha = buscar_proxima_senha()
        
        if not senha:
            return {
                'success': False,
                'message': 'Nenhuma senha na fila'
            }
        
        # Marcar como chamada
        senha.marcar_como_chamada(guiche, usuario)
        
        # Registrar no histórico
        historico = HistoricoChamada(
            senha_id=senha.id,
            acao='chamada' if senha.total_chamadas == 1 else 'rechamada',
            guiche=guiche,
            usuario=usuario,
            detalhes=f'Chamada #{senha.total_chamadas}'
        )
        
        db.session.add(historico)
        db.session.commit()
        
        return {
            'success': True,
            'senha_id': senha.id,
            'numero': senha.numero,
            'tipo': senha.tipo,
            'is_prioridade': senha.is_prioridade,
            'total_chamadas': senha.total_chamadas,
            'guiche': guiche,
            'message': f'Senha {senha.numero} chamada'
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Erro ao chamar próxima senha: {str(e)}'
        }


def rechamar_senha(senha_id, guiche=None, usuario=None):
    """
    Rechamada de uma senha que estava sendo atendida.
    Incrementa total_chamadas. A marcação como ausente é manual.
    
    Args:
        senha_id (int): ID da senha
        guiche (str): Local de atendimento
        usuario (str): Agente que rechamou
    
    Returns:
        dict: Resultado da operação
    """
    try:
        senha = Senha.query.get(senha_id)
        
        if not senha:
            return {
                'success': False,
                'message': 'Senha não encontrada'
            }
        
        # Incrementar chamadas
        senha.marcar_como_chamada(guiche, usuario)
        acao = 'rechamada'
        
        # Registrar no histórico
        historico = HistoricoChamada(
            senha_id=senha.id,
            acao=acao,
            guiche=guiche,
            usuario=usuario,
            detalhes=f'Rechamada #{senha.total_chamadas}'
        )
        
        db.session.add(historico)
        db.session.commit()
        
        return {
            'success': True,
            'senha_id': senha.id,
            'numero': senha.numero,
            'tipo': senha.tipo,
            'is_prioridade': senha.is_prioridade,
            'status': senha.status,
            'total_chamadas': senha.total_chamadas,
            'message': f'Senha {senha.numero} rechamada'
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Erro ao rechamar senha: {str(e)}'
        }


def finalizar_senha(senha_id, usuario=None):
    """
    Finaliza o atendimento de uma senha.
    
    Args:
        senha_id (int): ID da senha
        usuario (str): Agente que finalizou
    
    Returns:
        dict: Resultado da operação
    """
    try:
        senha = Senha.query.get(senha_id)
        
        if not senha:
            return {
                'success': False,
                'message': 'Senha não encontrada'
            }
        
        senha.marcar_como_finalizada()
        
        # Registrar no histórico
        historico = HistoricoChamada(
            senha_id=senha.id,
            acao='finalizada',
            usuario=usuario,
            detalhes=f'Atendimento finalizado'
        )
        
        db.session.add(historico)
        db.session.commit()
        
        return {
            'success': True,
            'senha_id': senha.id,
            'numero': senha.numero,
            'status': 'finalizada',
            'message': f'Atendimento da senha {senha.numero} finalizado'
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Erro ao finalizar senha: {str(e)}'
        }


def cancelar_senha(senha_id, usuario=None, motivo=None):
    """
    Cancela uma senha.
    
    Args:
        senha_id (int): ID da senha
        usuario (str): Agente que cancelou
        motivo (str): Motivo do cancelamento
    
    Returns:
        dict: Resultado da operação
    """
    try:
        senha = Senha.query.get(senha_id)
        
        if not senha:
            return {
                'success': False,
                'message': 'Senha não encontrada'
            }
        
        senha.marcar_como_cancelada()
        
        # Registrar no histórico
        historico = HistoricoChamada(
            senha_id=senha.id,
            acao='cancelada',
            usuario=usuario,
            detalhes=motivo or 'Cancelamento solicitado'
        )
        
        db.session.add(historico)
        db.session.commit()
        
        return {
            'success': True,
            'senha_id': senha.id,
            'numero': senha.numero,
            'status': 'cancelada',
            'message': f'Senha {senha.numero} cancelada'
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Erro ao cancelar senha: {str(e)}'
        }


def marcar_ausente_senha(senha_id, usuario=None):
    """
    Marca uma senha como ausente (não compareceu).
    
    Args:
        senha_id (int): ID da senha
        usuario (str): Agente que marcou como ausente
    
    Returns:
        dict: Resultado da operação
    """
    try:
        senha = Senha.query.get(senha_id)
        
        if not senha:
            return {
                'success': False,
                'message': 'Senha não encontrada'
            }
        
        senha.marcar_como_ausente()
        
        # Registrar no histórico
        historico = HistoricoChamada(
            senha_id=senha.id,
            acao='ausente',
            usuario=usuario,
            detalhes='Marcada como ausente'
        )
        
        db.session.add(historico)
        db.session.commit()
        
        return {
            'success': True,
            'senha_id': senha.id,
            'numero': senha.numero,
            'status': 'ausente',
            'message': f'Senha {senha.numero} marcada como AUSENTE'
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Erro ao marcar ausente: {str(e)}'
        }


def toggle_prioridade_senha(senha_id):
    """
    Alterna o status de prioridade de uma senha.
    
    Args:
        senha_id (int): ID da senha
    
    Returns:
        dict: Resultado da operação
    """
    try:
        senha = Senha.query.get(senha_id)
        
        if not senha:
            return {
                'success': False,
                'message': 'Senha não encontrada'
            }
        
        # Alternar prioridade
        senha.is_prioridade = not senha.is_prioridade
        db.session.commit()
        
        return {
            'success': True,
            'senha_id': senha.id,
            'numero': senha.numero,
            'is_prioridade': senha.is_prioridade,
            'message': f'Senha {senha.numero} {"marcada como prioridade" if senha.is_prioridade else "desmarcada como prioridade"}'
        }
    
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Erro ao alterar prioridade: {str(e)}'
        }


def obter_status_painel():
    """
    Retorna status atual do painel de atendimento.
    
    Returns:
        dict: Status com senhas atual e ultimas
    """
    hoje = date.today()
    
    # Senha atual sendo atendida (a mais recente com status chamada/rechamada)
    atual = Senha.query.filter(
        Senha.data_referencia == hoje,
        Senha.status.in_(['chamada', 'rechamada'])
    ).order_by(Senha.chamada_em.desc()).first()
    
    # Ultimas 5 finalizadas
    ultimas = Senha.query.filter(
        Senha.data_referencia == hoje,
        Senha.status.in_(['finalizada', 'cancelada', 'ausente'])
    ).order_by(Senha.finalizada_em.desc()).limit(5).all()
    
    # Contagem de senhas na fila
    na_fila_normal = Senha.query.filter(
        Senha.data_referencia == hoje,
        Senha.tipo == 'normal',
        Senha.status == 'aguardando'
    ).count()
    
    na_fila_prioritaria = Senha.query.filter(
        Senha.data_referencia == hoje,
        Senha.tipo == 'prioritaria',
        Senha.status == 'aguardando'
    ).count()
    
    return {
        'data_referencia': str(hoje),
        'atual': {
            'id': atual.id,
            'numero': atual.numero,
            'tipo': atual.tipo,
            'status': atual.status,
            'guiche': atual.guiche,
            'chamada_em': atual.chamada_em.isoformat() if atual else None
        } if atual else None,
        'ultimas': [
            {
                'id': s.id,
                'numero': s.numero,
                'tipo': s.tipo,
                'status': s.status,
                'finalizada_em': s.finalizada_em.isoformat()
            }
            for s in ultimas
        ],
        'fila': {
            'normal': na_fila_normal,
            'prioritaria': na_fila_prioritaria,
            'total': na_fila_normal + na_fila_prioritaria
        }
    }


def obter_fila_do_dia():
    """
    Retorna todas as senhas aguardando atendimento do dia.
    
    Returns:
        dict: Lista de senhas na fila
    """
    hoje = date.today()
    
    senhas_fila = Senha.query.filter(
        Senha.data_referencia == hoje,
        Senha.status == 'aguardando'
    ).order_by(
        Senha.is_prioridade.desc(),  # Prioritárias primeiro
        Senha.sequencia_dia.asc()
    ).all()
    
    return {
        'data_referencia': str(hoje),
        'total': len(senhas_fila),
        'senhas': [
            {
                'id': s.id,
                'numero': s.numero,
                'tipo': s.tipo,
                'is_prioridade': s.is_prioridade,
                'sequencia_dia': s.sequencia_dia,
                'criada_em': s.criada_em.isoformat()
            }
            for s in senhas_fila
        ]
    }


def obter_ultimas_chamadas(limite=5):
    """
    Retorna as últimas senhas chamadas.
    
    Args:
        limite (int): Número máximo de senhas a retornar
    
    Returns:
        dict: Lista de ultimas chamadas
    """
    hoje = date.today()
    
    ultimas = Senha.query.filter(
        Senha.data_referencia == hoje,
        Senha.status.in_(['finalizada', 'cancelada', 'ausente'])
    ).order_by(Senha.finalizada_em.desc()).limit(limite).all()
    
    return {
        'data_referencia': str(hoje),
        'total': len(ultimas),
        'ultimas': [
            {
                'id': s.id,
                'numero': s.numero,
                'tipo': s.tipo,
                'is_prioridade': s.is_prioridade,
                'status': s.status,
                'total_chamadas': s.total_chamadas,
                'criada_em': s.criada_em.isoformat(),
                'finalizada_em': s.finalizada_em.isoformat() if s.finalizada_em else None
            }
            for s in ultimas
        ]
    }


def obter_relatorio_diario(data_ref=None):
    """
    Gera relatório diário de senhas processadas.
    
    Args:
        data_ref (date): Data de referência (default: hoje)
    
    Returns:
        dict: Estatísticas do dia
    """
    if not data_ref:
        data_ref = date.today()
    
    senhas = Senha.query.filter(Senha.data_referencia == data_ref).all()
    
    total = len(senhas)
    finalizadas = len([s for s in senhas if s.status == 'finalizada'])
    canceladas = len([s for s in senhas if s.status == 'cancelada'])
    ausentes = len([s for s in senhas if s.status == 'ausente'])
    
    # Tempo médio de atendimento (apenas senhas finalizadas com sucesso)
    tempos = []
    for s in senhas:
        if s.status == 'finalizada' and s.criada_em and s.finalizada_em:
            tempo = (s.finalizada_em - s.criada_em).total_seconds() // 60
            tempos.append(tempo)
    
    tempo_medio = sum(tempos) // len(tempos) if tempos else 0
    
    return {
        'data_referencia': str(data_ref),
        'total_senhas': total,
        'finalizadas': finalizadas,
        'canceladas': canceladas,
        'ausentes': ausentes,
        'em_atendimento': len([s for s in senhas if s.status in ['chamada', 'rechamada']]),
        'na_fila': len([s for s in senhas if s.status == 'aguardando']),
        'por_tipo': {
            'primeira_consulta': len([s for s in senhas if s.tipo == 'primeira_consulta']),
            'nova_consulta': len([s for s in senhas if s.tipo == 'nova_consulta']),
            'retorno': len([s for s in senhas if s.tipo == 'retorno']),
            'interconsulta': len([s for s in senhas if s.tipo == 'interconsulta'])
        },
        'senhas': [
            {
                'id': s.id,
                'numero': s.numero,
                'tipo': s.tipo,
                'status': s.status,
                'criada_em': s.criada_em.isoformat() if s.criada_em else None,
                'finalizada_em': s.finalizada_em.isoformat() if s.finalizada_em else None,
                'chamada_em': s.chamada_em.isoformat() if s.chamada_em else None
            }
            for s in senhas
        ],
        'tempo_medio_atendimento_minutos': tempo_medio
    }


def obter_relatorio_mensal(ano=None, mes=None):
    """
    Gera relatório mensal agregado.
    
    Args:
        ano (int): Ano (default: ano atual)
        mes (int): Mês 1-12 (default: mês atual)
    
    Returns:
        dict: Estatísticas do mês
    """
    if not ano:
        ano = datetime.now().year
    if not mes:
        mes = datetime.now().month
    
    # Buscar todas as senhas do mês
    from datetime import datetime as dt
    primeiro_dia = date(ano, mes, 1)
    
    if mes == 12:
        ultimo_dia = date(ano + 1, 1, 1)
    else:
        ultimo_dia = date(ano, mes + 1, 1)
    
    senhas = Senha.query.filter(
        Senha.data_referencia >= primeiro_dia,
        Senha.data_referencia < ultimo_dia
    ).all()
    
    total = len(senhas)
    finalizadas = len([s for s in senhas if s.status == 'finalizada'])
    canceladas = len([s for s in senhas if s.status == 'cancelada'])
    ausentes = len([s for s in senhas if s.status == 'ausente'])
    
    return {
        'periodo': f'{ano}-{mes:02d}',
        'total_senhas': total,
        'finalizadas': finalizadas,
        'canceladas': canceladas,
        'ausentes': ausentes,
        'por_tipo': {
            'primeira_consulta': len([s for s in senhas if s.tipo == 'primeira_consulta']),
            'nova_consulta': len([s for s in senhas if s.tipo == 'nova_consulta']),
            'retorno': len([s for s in senhas if s.tipo == 'retorno']),
            'interconsulta': len([s for s in senhas if s.tipo == 'interconsulta'])
        },
        'senhas': [
            {
                'id': s.id,
                'numero': s.numero,
                'tipo': s.tipo,
                'status': s.status,
                'criada_em': s.criada_em.isoformat() if s.criada_em else None,
                'finalizada_em': s.finalizada_em.isoformat() if s.finalizada_em else None,
                'chamada_em': s.chamada_em.isoformat() if s.chamada_em else None
            }
            for s in senhas
        ]
    }
