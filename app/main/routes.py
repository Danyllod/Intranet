from flask import render_template
from . import main_bp


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


@main_bp.route('/')
def index():
    return render_template('main/index.html', title='Início')


@main_bp.route('/noticias')
def noticias():
    return render_template('main/noticias.html', title='Notícias')


@main_bp.route('/categoria/<cat>')
def categoria(cat):
    categorias_validas = ['tecnologia', 'politica', 'esportes', 'entretenimento', 'mundo', 'outros']
    if cat not in categorias_validas:
        return render_template('404.html'), 404
    return render_template('main/categoria.html', categoria=cat, title=cat.title())


@main_bp.route('/sobre')
def sobre():
    return render_template('main/about.html', title='Sobre Nós')


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
    return render_template('main/artigo.html', artigo=artigo_data, title=artigo_data['titulo'])


@main_bp.route('/jornal')
def jornal():
    return render_template('main/jornal.html', title='Jornal CRESM')
