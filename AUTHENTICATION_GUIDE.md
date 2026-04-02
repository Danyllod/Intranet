## 🔐 Sistema de Autenticação - Documentação

### 📋 Resumo
Sistema de autenticação com hierarquias de usuários (Administrador e Básico) implementado com Flask-Login.

---

## 👥 Hierarquias de Usuários

### Administrador
- **Acesso a:**
  - ✅ Página de Admin (gerenciamento de usuários)
  - ✅ Relatórios (diários e mensais)
  - ✅ Recepção (geração de senhas)
  - ✅ Atendimento (controle de filas)
  - ✅ Painel (visualização pública)

- **Permissões:**
  - Criar, editar e deletar usuários básicos
  - Ativar/desativar usuários
  - Alterar senhas de outros usuários

### Usuário Básico
- **Acesso a:**
  - ✅ Recepção (geração de senhas)
  - ✅ Atendimento (controle de filas)
  - ✅ Painel (visualização pública)
  - ❌ Admin (gerenciamento de usuários)
  - ❌ Relatórios

### Página Painel
- **Acesso:** 🌐 Público (sem autenticação necessária)
- **Função:** Exibição de senhas em tempo real

---

## 🚀 Como Usar

### 1. Iniciar a Aplicação

```bash
python app.py
```

A aplicação estará disponível em: `http://127.0.0.1:5000`

### 2. Acessar a Página de Login

- URL: `http://127.0.0.1:5000/auth/login`
- Use as credenciais de teste criadas durante a inicialização

### 3. Usuários de Teste Pré-criados

```
Admin:
  Username: admin
  Email: admin@cresm.local
  Senha: admin123

Recepção (Usuário Básico):
  Username: recepcao
  Email: recepcao@cresm.local
  Senha: recepcao123

Atendimento (Usuário Básico):
  Username: atendimento
  Email: atendimento@cresm.local
  Senha: atendimento123
```

---

## 🔧 Estrutura Técnica

### Modelos
- **User** (`app/models.py`)
  - Hierarquias: `admin` e `basico`
  - Método: `is_admin()`, `is_basico()`
  - Hash de senhas com Werkzeug

### Decoradores (`app/auth/decorators.py`)
- `@login_required_custom`: Requer login
- `@admin_required`: Requer admin
- `@basico_required`: Requer básico ou admin

### Rotas (`app/auth/routes.py`)

#### Login
- `GET/POST /auth/login` - Página e processamento de login
- `GET /auth/logout` - Logout do usuário

#### Administração
- `GET /auth/admin` - Lista de usuários (paginada)
- `GET /auth/admin/novo` - Formulário de novo usuário
- `POST /auth/admin/novo` - Criar usuário
- `GET /auth/admin/editar/<id>` - Formulário de editar
- `POST /auth/admin/editar/<id>` - Atualizar usuário
- `POST /auth/admin/deletar/<id>` - Deletar usuário
- `POST /auth/admin/toggle-ativo/<id>` - Ativar/desativar usuário

#### Protegidas (Senhas)
- `GET /senhas/recepcao` - Requer `basico_required`
- `GET /senhas/atendimento` - Requer `basico_required`
- `GET /senhas/relatorios` - Requer `admin_required`
- `GET /senhas/relatorios/diario` - Requer `admin_required`
- `GET /senhas/relatorios/mensal` - Requer `admin_required`
- `GET /senhas/painel` - Público (sem autenticação)

---

## 📊 Painéis Laterais

Todos os templates de senhas incluem um painel lateral com navegação rápida:

- **Admin** vê: Gerenciar Usuários, Relatórios, Recepção, Atendimento, Painel
- **Básico** vê: Recepção, Atendimento, Painel
- **Público** vê: Login, Painel

---

## 🔐 Segurança

- Senhas são hash com Werkzeug (`generate_password_hash`, `check_password_hash`)
- Cookies de sessão com `HTTPOnly`
- Proteção contra XSS com Jinja2
- CSRF protegido (via formulários)

---

## 📝 Inicializar Novos Usuários

Para criar novos usuários após a inicialização:

```bash
python init_users.py
```

Este script:
- Cria usuário admin se não existir
- Cria usuários de teste (recepcao, atendimento)

---

## 🐛 Resolução de Problemas

### Erro: "User object is not callable"
- Verifique se o `User` foi importado corretamente em `__init__.py`
- Reinicie o servidor

### Erro ao acessar rotas protegidas
- Faça login no `/auth/login`
- Verifique se sua conta tem a permissão necessária

### Usuários não aparecem
- Execute `python init_users.py` para criar usuários de teste
- Verifique o banco de dados em `instance/reservas.db`

---

## 🎨 Personalização

### Mudar Senhas de Teste
Edite `init_users.py` e modifique:
```python
admin.set_password('sua_nova_senha')
```

### Adicionar Novos Níveis de Hierarquia
1. Edite o campo `role` no modelo `User`
2. Crie novos decoradores em `app/auth/decorators.py`
3. Proteja rotas com os novos decoradores

### Customizar Sidebar
Edite os templates em `templates/senhas/` e a condicional:
```jinja2
{% if current_user.is_admin() %}
    <!-- Conteúdo admin -->
{% endif %}
```

---

## 📚 Referências

- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [Werkzeug Security](https://werkzeug.palletsprojects.com/security/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/security/)

---

**Última atualização:** Abril de 2026
