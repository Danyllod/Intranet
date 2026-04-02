#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug - Teste POST Detalhado
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print('=' * 70)
print('🔍 DEBUG - Teste POST Detalhado')
print('=' * 70)

endpoint = '/agenda-salas/solicitar'
data = {
    'data': '2026-04-15',
    'hora_inicio': '10:00',
    'hora_fim': '11:00',
    'reservado_por': 'João Silva',
    'local': 'Sala 1',
    'evento': 'Reunião',
    'participantes': '5'
}

print(f'\nEndpoint: {endpoint}')
print(f'Dados enviados:\n{json.dumps(data, ensure_ascii=False, indent=2)}')
print('\nRequisição...')

try:
    response = requests.post(f'{BASE_URL}{endpoint}', 
                           data=data,  # Importante: usar data, não json!
                           timeout=10)
    
    print(f'Status: {response.status_code}')
    print(f'Headers: {dict(response.headers)}')
    print(f'\nTamanho da resposta: {len(response.text)} caracteres')
    
    if response.status_code >= 400:
        print(f'\n🔴 ERRO {response.status_code}')
        print(f'Primeiros 1000 caracteres da resposta:')
        print(response.text[:1000])
        
        # Tenta extrair a mensagem de erro
        if 'Traceback' in response.text:
            print('\n⚠️  STACK TRACE ENCONTRADO!')
            lines = response.text.split('\n')
            for i, line in enumerate(lines):
                if 'Traceback' in line:
                    # Imprime desde Traceback até o próximo bloco
                    for error_line in lines[i:i+20]:
                        print(error_line)
                    break
    else:
        print('\n✅ Sucesso!')
        print(response.text[:500])
        
except Exception as e:
    print(f'\n❌ Erro na requisição: {str(e)}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 70)
