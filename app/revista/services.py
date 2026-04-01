import json
import os
import base64
from datetime import datetime


# Caminho dos arquivos de dados
REVISTA_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'revista_data.json')
REVISTA_IMAGES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'imagens', 'revista_pages')
EDICOES_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'edicoes_data.json')
VIEWS_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'views_data.json')

# Criar pasta de imagens se não existir
os.makedirs(REVISTA_IMAGES_PATH, exist_ok=True)


def carregar_revista_data():
    """Carrega os dados da revista do arquivo JSON"""
    try:
        with open(REVISTA_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def salvar_revista_com_imagens(pages):
    """
    Salva os dados da revista com imagens.
    Processa base64 e salva arquivos.
    """
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


def salvar_edicoes(edicoes):
    """Salva a lista de edições"""
    edicoes_data = {
        'edicoes': edicoes,
        'saved_at': datetime.now().isoformat()
    }
    
    with open(EDICOES_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(edicoes_data, f, ensure_ascii=False, indent=2)
    
    print(f"[DEBUG] Edições salvas com sucesso!")


def carregar_visualizacoes():
    """Carrega os dados de visualizações das edições"""
    try:
        with open(VIEWS_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('visualizacoes', {})
    except FileNotFoundError:
        return {}


def registrar_visualizacao(edicao_id):
    """Registra uma visualização de uma edição"""
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
