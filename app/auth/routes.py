"""
Rotas de autenticação: login, logout e gerenciamento de usuários
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from . import auth_bp
from ..models import db, User
from .decorators import admin_required


# ============================================================================
# PÁGINA DE LOGIN
# ============================================================================

@auth_bp.get("/login")
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html', title='Login', include_navbar=False)


@auth_bp.post("/login")
def login_post():
    """Processa o login do usuário"""
    username = request.form.get('username')
    password = request.form.get('password')
    remember = request.form.get('remember')
    
    if not username or not password:
        flash('Por favor, preencha usuário e senha.', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        flash('Usuário ou senha inválidos.', 'error')
        return redirect(url_for('auth.login'))
    
    if not user.ativo:
        flash('Usuário inativo. Contate o administrador.', 'error')
        return redirect(url_for('auth.login'))
    
    login_user(user, remember=bool(remember))
    flash(f'Bem-vindo, {user.username}!', 'success')
    
    # Redirecionar para página anterior ou dashboard
    next_page = request.args.get('next')
    if next_page and next_page.startswith('/'):
        return redirect(next_page)
    
    # Admin vai para admin, básico para recepcao
    if user.is_admin():
        return redirect(url_for('auth.admin'))
    else:
        return redirect(url_for('senhas.recepcao'))


# ============================================================================
# LOGOUT
# ============================================================================

@auth_bp.get("/logout")
@login_required
def logout():
    """Faz logout do usuário"""
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.index'))


# ============================================================================
# PAINEL ADMINISTRATIVO - GERENCIAR USUÁRIOS
# ============================================================================

@auth_bp.get("/admin")
@admin_required
def admin():
    """Página de administração de usuários"""
    page = request.args.get('page', 1, type=int)
    usuarios = User.query.filter_by(role='basico').paginate(page=page, per_page=10)
    
    return render_template(
        'auth/admin.html',
        title='Administração de Usuários',
        usuarios=usuarios,
        include_navbar=False
    )


@auth_bp.get("/admin/novo")
@admin_required
def novo_usuario_form():
    """Formulário para criar novo usuário"""
    return render_template('auth/novo_usuario.html', title='Novo Usuário', include_navbar=False)


@auth_bp.post("/admin/novo")
@admin_required
def novo_usuario():
    """Cria novo usuário"""
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    role = request.form.get('role', 'basico')
    
    # Validações
    if not username or not email or not password:
        flash('Por favor, preencha todos os campos.', 'error')
        return redirect(url_for('auth.novo_usuario_form'))
    
    if password != password_confirm:
        flash('As senhas não correspondem.', 'error')
        return redirect(url_for('auth.novo_usuario_form'))
    
    if len(password) < 6:
        flash('A senha deve ter no mínimo 6 caracteres.', 'error')
        return redirect(url_for('auth.novo_usuario_form'))
    
    if User.query.filter_by(username=username).first():
        flash('Usuário com este nome já existe.', 'error')
        return redirect(url_for('auth.novo_usuario_form'))
    
    if User.query.filter_by(email=email).first():
        flash('Usuário com este email já existe.', 'error')
        return redirect(url_for('auth.novo_usuario_form'))
    
    # Criar novo usuário
    novo_user = User(
        username=username,
        email=email,
        role=role
    )
    novo_user.set_password(password)
    
    db.session.add(novo_user)
    db.session.commit()
    
    flash(f'Usuário {username} criado com sucesso!', 'success')
    return redirect(url_for('auth.admin'))


@auth_bp.get("/admin/editar/<int:user_id>")
@admin_required
def editar_usuario_form(user_id):
    """Formulário para editar usuário"""
    user = User.query.get_or_404(user_id)
    
    # Não permitir editar admin
    if user.is_admin():
        flash('Não é permitido editar usuários administradores.', 'error')
        return redirect(url_for('auth.admin'))
    
    return render_template(
        'auth/editar_usuario.html',
        title='Editar Usuário',
        user=user,
        include_navbar=False
    )


@auth_bp.post("/admin/editar/<int:user_id>")
@admin_required
def editar_usuario(user_id):
    """Atualiza dados do usuário"""
    user = User.query.get_or_404(user_id)
    
    # Não permitir editar admin
    if user.is_admin():
        flash('Não é permitido editar usuários administradores.', 'error')
        return redirect(url_for('auth.admin'))
    
    email = request.form.get('email')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    ativo = request.form.get('ativo')
    
    # Validações
    if not email:
        flash('Email é obrigatório.', 'error')
        return redirect(url_for('auth.editar_usuario_form', user_id=user_id))
    
    # Verificar se email já existe em outro usuário
    outro_user = User.query.filter_by(email=email).first()
    if outro_user and outro_user.id != user.id:
        flash('Este email já está em uso.', 'error')
        return redirect(url_for('auth.editar_usuario_form', user_id=user_id))
    
    # Atualizar email
    user.email = email
    user.ativo = bool(ativo)
    
    # Atualizar senha se foi preenchida
    if password:
        if password != password_confirm:
            flash('As senhas não correspondem.', 'error')
            return redirect(url_for('auth.editar_usuario_form', user_id=user_id))
        
        if len(password) < 6:
            flash('A senha deve ter no mínimo 6 caracteres.', 'error')
            return redirect(url_for('auth.editar_usuario_form', user_id=user_id))
        
        user.set_password(password)
    
    db.session.commit()
    flash(f'Usuário {user.username} atualizado com sucesso!', 'success')
    return redirect(url_for('auth.admin'))


@auth_bp.post("/admin/deletar/<int:user_id>")
@admin_required
def deletar_usuario(user_id):
    """Deleta um usuário"""
    user = User.query.get_or_404(user_id)
    
    # Não permitir deletar admin
    if user.is_admin():
        flash('Não é permitido deletar usuários administradores.', 'error')
        return redirect(url_for('auth.admin'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Usuário {username} deletado com sucesso!', 'success')
    return redirect(url_for('auth.admin'))


@auth_bp.post("/admin/toggle-ativo/<int:user_id>")
@admin_required
def toggle_ativo_usuario(user_id):
    """Ativa ou desativa um usuário"""
    user = User.query.get_or_404(user_id)
    
    # Não permitir desativar admin
    if user.is_admin():
        flash('Não é permitido desativar administradores.', 'error')
        return redirect(url_for('auth.admin'))
    
    user.ativo = not user.ativo
    db.session.commit()
    
    status = 'ativado' if user.ativo else 'desativado'
    flash(f'Usuário {user.username} {status} com sucesso!', 'success')
    return redirect(url_for('auth.admin'))
