# Arquitetura de Blueprints - Intranet CRESM

## 📁 Estrutura Organizada por Feature

A aplicação Flask foi refatorada seguindo o padrão de **blueprints por funcionalidade**, não por tipo técnico. Isso mantém o código modular, fácil de evoluir e simples de encontrar onde cada coisa está.

### Blueprint `main` — Páginas Institucionais
**Prefixo:** `/` (sem prefixo)  
**Arquivo:** `app/main/routes.py`

| Rota | Função | Descrição |
|------|--------|-----------|
| `GET /` | `index()` | Página inicial |
| `GET /noticias` | `noticias()` | Listagem de notícias |
| `GET /categoria/<cat>` | `categoria()` | Artigos por categoria |
| `GET /sobre` | `sobre()` | Página "Sobre Nós" |
| `GET /artigo/<id>` | `artigo()` | Detalhe de um artigo |
| `GET /jornal` | `jornal()` | Jornal mensal |

**Utilities:** Filtro customizado `traduzir_data_pt` para formatar datas em português.

---

### Blueprint `revista` — Gestão de Revista
**Prefixo:** `/revista`  
**Arquivos:**
- `app/revista/routes.py` — Rotas
- `app/revista/services.py` — Lógica de negócio

#### Rotas de Páginas
| Rota | Função | Descrição |
|------|--------|-----------|
| `GET /revista/` | `revista()` | Exibe revista com edições |
| `GET /revista/editar` | `editar_revista()` | Página de edição |

#### Rotas de API
| Rota | Método | Função | Descrição |
|------|--------|--------|-----------|
| `/revista/api/salvar` | POST | `salvar_revista_api()` | Salva páginas com imagens (base64) |
| `/revista/api/carregar-paginas` | GET | `carregar_paginas_revista()` | Carrega páginas salvas |
| `/revista/api/carregar-edicoes` | GET | `carregar_edicoes()` | Lista edições disponíveis |
| `/revista/api/salvar-edicoes` | POST | `salvar_edicoes_api()` | Salva lista de edições |
| `/revista/api/carregar-visualizacoes` | GET | `carregar_visualizacoes_api()` | Estatísticas de visualizações |
| `/revista/api/registrar-visualizacao` | POST | `registrar_visualizacao_api()` | Registra visualização de edição |

#### Funcionalidades em `services.py`
- `carregar_revista_data()` — Lê JSON de revista
- `salvar_revista_com_imagens(pages)` — Processa base64 e salvaimagens
- `obter_edicoes_disponiveis()` — Retorna edições cadastradas
- `salvar_edicoes(edicoes)` — Persiste edições
- `carregar_visualizacoes()` — Carrega dados de views
- `registrar_visualizacao(edicao_id)` — Incrementa contador

**Arquivos de Dados:**
- `revista_data.json` — Páginas da revista
- `edicoes_data.json` — Lista de edições
- `views_data.json` — Contadores de visualização

---

### Blueprint `salas` — Agenda e Reservas de Salas
**Prefixo:** `/agenda-salas`  
**Arquivos:**
- `app/salas/routes.py` — Rotas
- `app/salas/services.py` — Verificação de conflitos

#### Rotas de Páginas
| Rota | Função | Descrição |
|------|--------|-----------|
| `GET /agenda-salas/` | `agenda_salas()` | Visualiza agenda (reservas aprovadas e canceladas) |
| `GET /agenda-salas/solicitar` | `solicitar_reserva_sala()` | Formulário de solicitação |
| `GET /agenda-salas/gerenciar` | `gerenciar_solicitacoes()` | Painel admin de solicitações |
| `GET /agenda-salas/gerenciar-confirmacoes` | `gerenciar_confirmacoes()` | Confirmar/cancelar reuniões futuras |
| `GET /agenda-salas/solicitar-cancelamento` | `solicitar_cancelamento_reserva()` | Solicitar cancelamento |

#### Rotas de Ações (POST)
| Rota | Método | Função | Descrição |
|------|--------|--------|-----------|
| `/agenda-salas/aprovar/<id>` | POST | `aprovar_solicitacao()` | Aprova solicitação pendente |
| `/agenda-salas/negar/<id>` | POST | `negar_solicitacao()` | Nega solicitação |
| `/agenda-salas/confirmar/<id>` | POST | `confirmar_reuniao()` | Confirma reunião aprovada |
| `/agenda-salas/cancelar/<id>` | POST | `cancelar_reuniao()` | Cancela reunião confirmada |
| `/agenda-salas/aprovar-cancelamento/<id>` | POST | `aprovar_cancelamento()` | Aprova cancelamento |
| `/agenda-salas/negar-cancelamento/<id>` | POST | `negar_cancelamento()` | Nega cancelamento |

#### Funcionalidades em `services.py`
- `verificar_conflito_horario(data, hora_inicio, hora_fim, local)` → Valida sobreposição de horários

**Fluxo de Reservas:**
```
1. Usuário solicita → status = 'pendente'
2. Admin aprova → status = 'aprovado'
3. Admin confirma → confirmado = True
4. Usuário cancela → status = 'cancelado'
```

---

### Blueprint `auth` — Autenticação (Futuro)
**Prefixo:** `/auth`  
**Arquivo:** `app/auth/routes.py` (template)

- Implementação futura de login/logout
- Controle de usuário e permissões

---

### Blueprint `senhas` — Painel de Senhas (Futuro)
**Prefixo:** `/senhas`  
**Arquivo:** `app/senhas/routes.py` (template)

- Implementação futura de gerenciamento de senhas

---

## 🔧 Como Registrar um Novo Blueprint

Quando criar um novo módulo, siga esses passos:

1. **Criar a pasta do módulo:**
   ```
   app/novo_modulo/
   ├── __init__.py
   ├── routes.py
   └── services.py (se necessário)
   ```

2. **Registrar em `__init__.py`:**
   ```python
   from flask import Blueprint
   
   novo_bp = Blueprint('novo_modulo', __name__, url_prefix='/novo-modulo')
   
   from . import routes
   ```

3. **Adicionar rotas em `routes.py`:**
   ```python
   from . import novo_bp
   
   @novo_bp.route('/')
   def index():
       return render_template('novo_modulo/index.html')
   ```

4. **Registrar em `app/__init__.py`:**
   ```python
   from app.novo_modulo import novo_bp
   app.register_blueprint(novo_bp)
   ```

---

## ✅ Benefícios da Estrutura Atual

- **Modular:** Cada feature é independente e pode evoluir sem afetar outras
- **Escalável:** Fácil adicionar novos blueprints
- **Organizado:** Código de negócio em `services.py`, rotas em `routes.py`
- **Maintível:** Prefixos claros nas rotas facilitam permissões e logging
- **Testável:** Cada blueprint pode ser testado isoladamente

---

## 📝 Templates por Blueprint

```
templates/
├── base.html
├── 404.html
├── main/
│   ├── index.html
│   ├── noticias.html
│   ├── categoria.html
│   ├── about.html
│   ├── artigo.html
│   └── jornal.html
├── revista/
│   ├── revista.html
│   └── editar-revista.html
├── salas/
│   ├── agenda_salas.html
│   ├── solicitar_reserva_sala.html
│   ├── gerenciar_solicitacoes.html
│   ├── gerenciar_confirmacoes.html
│   └── solicitar_cancelamento_reserva.html
└── auth/
    └── (futuro)
```

Cada blueprint busca seus templates no subfolder correspondente, evitando conflitos de nomes.
