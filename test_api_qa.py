#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QA Script - Teste de API da Revista
Testa todos os endpoints de API para encontrar bugs
"""

import requests
import json
import time

BASE_URL = 'http://127.0.0.1:5000'

def test_api(name, method, endpoint, data=None, should_pass=True):
    """Função auxiliar para testar endpoints"""
    print(f'\n[TEST] {name}')
    print(f'   Método: {method} {endpoint}')
    try:
        if method == 'GET':
            response = requests.get(f'{BASE_URL}{endpoint}', timeout=5)
        elif method == 'POST':
            response = requests.post(f'{BASE_URL}{endpoint}', 
                                   json=data,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=5)
        
        print(f'   Status: {response.status_code}')
        resp_data = response.json()
        success = resp_data.get('success', False)
        
        # Validação
        if should_pass and success:
            print(f'   Resposta: {json.dumps(resp_data, ensure_ascii=False)[:150]}...')
            print('   ✅ PASSOU')
            return True
        elif not should_pass and not success:
            print(f'   Erro esperado: {resp_data.get("error")}')
            print('   ✅ COMPORTAMENTO CORRETO (falha esperada)')
            return True
        else:
            if should_pass:
                print(f'   ❌ FALHOU - esperava sucesso mas obteve: {resp_data}')
            else:
                print(f'   ❌ FALHOU - deveria ter falhado mas passou')
            return False
    except Exception as e:
        print(f'   ❌ ERRO: {str(e)}')
        return False

print('=' * 70)
print('🧪 QA - TESTE COMPLETO DE API')
print('=' * 70)

results = []

# ============ GET endpoints ============
print('\n\n📋 TESTES GET - Endpoints de Leitura')
print('─' * 70)

results.append(('Carregar Páginas', test_api(
    'GET /revista/api/carregar-paginas - Deve retornar lista de páginas',
    'GET',
    '/revista/api/carregar-paginas',
    should_pass=True
)))

results.append(('Carregar Edições', test_api(
    'GET /revista/api/carregar-edicoes - Deve retornar lista de edições',
    'GET',
    '/revista/api/carregar-edicoes',
    should_pass=True
)))

results.append(('Carregar Visualizações', test_api(
    'GET /revista/api/carregar-visualizacoes - Deve retornar contadores',
    'GET',
    '/revista/api/carregar-visualizacoes',
    should_pass=True
)))

# ============ POST endpoints - Casos Válidos ============
print('\n\n✅ TESTES POST - Casos Válidos')
print('─' * 70)

results.append(('Registrar Visualização (válido)', test_api(
    'POST /revista/api/registrar-visualizacao - Com edicao_id válido',
    'POST',
    '/revista/api/registrar-visualizacao',
    data={'edicao_id': 'janeiro'},
    should_pass=True
)))

results.append(('Salvar Edições (válido)', test_api(
    'POST /revista/api/salvar-edicoes - Com edições válidas',
    'POST',
    '/revista/api/salvar-edicoes',
    data={'edicoes': [{'id': 'fevereiro', 'nome': 'Fevereiro', 'mes': 2}]},
    should_pass=True
)))

# ============ POST endpoints - Casos Inválidos (Testes Negativos) ============
print('\n\n❌ TESTES POST - Casos Inválidos (Devem Falhar)')
print('─' * 70)

results.append(('Registrar Visualização (sem ID)', test_api(
    'POST /revista/api/registrar-visualizacao - Sem edicao_id (deve falhar)',
    'POST',
    '/revista/api/registrar-visualizacao',
    data={},
    should_pass=False
)))

results.append(('Registrar Visualização (ID vazio)', test_api(
    'POST /revista/api/registrar-visualizacao - Com edicao_id vazio (deve falhar)',
    'POST',
    '/revista/api/registrar-visualizacao',
    data={'edicao_id': ''},
    should_pass=False
)))

results.append(('Registrar Visualização (ID None)', test_api(
    'POST /revista/api/registrar-visualizacao - Com edicao_id None (deve falhar)',
    'POST',
    '/revista/api/registrar-visualizacao',
    data={'edicao_id': None},
    should_pass=False
)))

results.append(('Salvar Edições (sem campo edicoes)', test_api(
    'POST /revista/api/salvar-edicoes - Sem campo edicoes',
    'POST',
    '/revista/api/salvar-edicoes',
    data={},
    should_pass=True  # Deve aceitar (será uma lista vazia)
)))

# ============ RESUMO FINAL ============
print('\n\n' + '=' * 70)
print('📊 RESUMO DO QA')
print('=' * 70)

passed = sum(1 for _, result in results if result)
total = len(results)

for name, result in results:
    status = '✅' if result else '❌'
    print(f'{status} {name}')

print(f'\nTotal: {passed}/{total} testes passaram')
print(f'Taxa de sucesso: {(passed/total)*100:.1f}%')

if passed == total:
    print('\n🎉 TODOS OS TESTES PASSARAM!')
else:
    print(f'\n⚠️  {total - passed} teste(s) falharam')

print('=' * 70)
