from datetime import date, time
from ..extensions import db
from ..models import ReservaSala


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
