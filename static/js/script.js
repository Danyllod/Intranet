// Atualizar data atual no header
document.addEventListener('DOMContentLoaded', function() {
    const dataAtual = document.getElementById('data-atual');
    if (dataAtual) {
        const hoje = new Date();
        const opcoes = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        const dataFormatada = hoje.toLocaleDateString('pt-BR', opcoes);
        dataAtual.textContent = dataFormatada;
    }

    console.log('Conexão CRESM carregado com sucesso!');
});
