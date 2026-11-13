/* ====================================================================
   CineSENAI & Teatro - Script Principal e Utilidades
   Autores: O Usuário e Sandro
   ==================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('preencherDemo')?.addEventListener('click', () => {
        const fields = {inputNome:'Cliente Demonstração', inputCpf:'123.456.789-00', inputTelefone:'(11) 99999-0000', inputEmail:'demonstracao@example.com',cardNumero:'4111 1111 1111 1111',cardNome:'CLIENTE DEMONSTRACAO',cardValidade:'12/' + String(new Date().getFullYear()+2).slice(-2),cardCvv:'123'};
        Object.entries(fields).forEach(([id,value]) => { const input=document.getElementById(id); if(input){ input.value=value;input.dispatchEvent(new Event('input',{bubbles:true})); } });
    });
    document.querySelectorAll('.date-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.date-tab').forEach(t => {
                t.classList.toggle('active', t === tab);
                t.setAttribute('aria-selected', String(t === tab));
            });
            document.querySelectorAll('[data-session-date]').forEach(panel => {
                panel.hidden = panel.dataset.sessionDate !== tab.dataset.date;
            });
        });
        tab.addEventListener('keydown', event => {
            const tabs = [...document.querySelectorAll('.date-tab')];
            const pos = tabs.indexOf(tab);
            if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
                event.preventDefault();
                const next = tabs[(pos + (event.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
                next.click(); next.focus();
            }
        });
    });
    document.querySelectorAll('.payment-method-radio-card').forEach(card => {
        card.setAttribute('role', 'button'); card.tabIndex = 0;
        card.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); card.click(); }
        });
    });
    document.querySelectorAll('label').forEach(label => {
        const field = label.parentElement.querySelector('input[id],select[id]');
        if (!label.htmlFor && field) label.htmlFor = field.id;
    });
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', () => {
            if (!img.src.endsWith('/static/images/favicon.svg')) img.src = '/static/images/favicon.svg';
        }, { once: true });
    });
    // Auto-dismiss de alertas após 5 segundos
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Utilitário para formatar moeda em JavaScript
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}
