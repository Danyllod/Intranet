from .extensions import db
from datetime import datetime


class ReservaSala(db.Model):
    __tablename__ = 'reservas_salas'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    reservado_por = db.Column(db.String(100), nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    local = db.Column(db.String(50), nullable=False)  
    
    # Campos adicionais
    evento = db.Column(db.String(200), nullable=True)  
    participantes = db.Column(db.Text, nullable=True)  
    confirmado = db.Column(db.Boolean, default=True, nullable=False)  # True = Confirmada, False = Cancelada
    
    # Campos para solicitação
    status = db.Column(db.String(20), default='pendente', nullable=False)  # pendente, aprovado, negado
    data_solicitacao = db.Column(db.DateTime, default=datetime.now, nullable=False)
    data_decisao = db.Column(db.DateTime, nullable=True)
    motivo_negacao = db.Column(db.Text, nullable=True)
    aprovado_por = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Reserva {self.data} {self.local} - {self.status}>'


class SolicitacaoCancelamento(db.Model):
    __tablename__ = 'solicitacoes_cancelamento'

    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas_salas.id'), nullable=False)
    solicitante = db.Column(db.String(100), nullable=False)
    motivo = db.Column(db.Text, nullable=False)
    
    # Campos de status
    status = db.Column(db.String(20), default='pendente', nullable=False)  # pendente, aprovado, negado
    data_solicitacao = db.Column(db.DateTime, default=datetime.now, nullable=False)
    data_decisao = db.Column(db.DateTime, nullable=True)
    motivo_negacao = db.Column(db.Text, nullable=True)
    aprovado_por = db.Column(db.String(100), nullable=True)

    # Relacionamento
    reserva = db.relationship('ReservaSala', backref='cancelamentos')

    def __repr__(self):
        return f'<Cancelamento Reserva {self.reserva_id} - {self.status}>'
