from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """Modelo de usuário com controle de hierarquias (admin e básico)"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Hierarquia: 'admin' ou 'basico'
    role = db.Column(db.String(20), default='basico', nullable=False)
    
    # Status
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    criado_em = db.Column(db.DateTime, default=datetime.now, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def set_password(self, password):
        """Define a senha com hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.role == 'admin'

    def is_basico(self):
        """Verifica se o usuário é básico"""
        return self.role == 'basico'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


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


class Senha(db.Model):
    """Modelo para gerenciamento de senhas do painel de atendimento"""
    __tablename__ = 'senhas'

    id = db.Column(db.Integer, primary_key=True)
    
    # Identificação
    numero = db.Column(db.String(10), unique=True, nullable=False)  # A001, A002, etc
    sequencia_dia = db.Column(db.Integer, nullable=False)  # Sequência do dia
    
    # Tipo e status
    tipo = db.Column(db.String(30), default='nova_consulta', nullable=False)  # primeira_consulta, nova_consulta, retorno, interconsulta
    is_prioridade = db.Column(db.Boolean, default=False, nullable=False)  # Marca se é prioridade
    status = db.Column(db.String(20), default='aguardando', nullable=False)  # aguardando, chamada, rechamada, finalizada, cancelada, ausente
    
    # Atendimento
    guiche = db.Column(db.String(50), nullable=True)  # Guiche onde foi atendida
    usuario_atendimento = db.Column(db.String(100), nullable=True)  # Agente que atendeu
    
    # Contadores
    total_chamadas = db.Column(db.Integer, default=0, nullable=False)
    
    # Data e hora
    data_referencia = db.Column(db.Date, default=datetime.now, nullable=False)  # Data do dia
    criada_em = db.Column(db.DateTime, default=datetime.now, nullable=False)
    chamada_em = db.Column(db.DateTime, nullable=True)
    finalizada_em = db.Column(db.DateTime, nullable=True)
    
    # Relacionamento
    historico = db.relationship('HistoricoChamada', backref='senha', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Senha {self.numero} - {self.status}>'

    def marcar_como_chamada(self, guiche=None, usuario=None):
        """Marca a senha como chamada"""
        self.status = 'chamada' if self.total_chamadas == 0 else 'rechamada'
        self.total_chamadas += 1
        self.chamada_em = datetime.now()
        self.guiche = guiche
        self.usuario_atendimento = usuario

    def marcar_como_finalizada(self):
        """Marca a senha como finalizada"""
        self.status = 'finalizada'
        self.finalizada_em = datetime.now()

    def marcar_como_cancelada(self):
        """Marca a senha como cancelada"""
        self.status = 'cancelada'
        self.finalizada_em = datetime.now()

    def marcar_como_ausente(self):
        """Marca a senha como ausente após 3 chamadas"""
        if self.total_chamadas >= 3:
            self.status = 'ausente'
            self.finalizada_em = datetime.now()


class HistoricoChamada(db.Model):
    """Histórico de todas as ações realizadas em uma senha"""
    __tablename__ = 'historico_chamadas'

    id = db.Column(db.Integer, primary_key=True)
    
    # Relacionamento
    senha_id = db.Column(db.Integer, db.ForeignKey('senhas.id'), nullable=False)
    
    # Ação realizada
    acao = db.Column(db.String(50), nullable=False)  # chamada, rechamada, finalizada, cancelada, ausente
    guiche = db.Column(db.String(50), nullable=True)
    usuario = db.Column(db.String(100), nullable=True)
    
    # Timestamp
    criado_em = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Detalhes adicionais
    detalhes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Historico {self.senha_id} - {self.acao}>'
