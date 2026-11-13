/* ====================================================================
   CineSENAI & Teatro - Lógica Interativa da Bomboniere
   Autores: O Usuário e Sandro
   ==================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Quantidades selecionadas no formato: { produtoId: { id, nome, preco, qtd } }
    const cart = new Map();

    const subtotalBomboniereEl = document.getElementById('subtotalBomboniereVal');
    const grandTotalEl = document.getElementById('checkoutGrandTotalVal');
    const bomboniereItemsListEl = document.getElementById('bomboniereItemsList');
    const totalIngressosVal = parseFloat(document.getElementById('ingressosSubtotalVal')?.dataset.valor || 0);

    const btnAvancar = document.getElementById('btnAvancarCheckout');
    const btnPular = document.getElementById('btnPularCheckout');

    const sessaoId = document.getElementById('bombonierePageData')?.dataset.sessaoId;
    const assentosIdsStr = document.getElementById('bombonierePageData')?.dataset.assentosIds || '';
    const tiposIngressosStr = document.getElementById('bombonierePageData')?.dataset.tiposIngressos || '';

    // Filtros de Categoria da Bomboniere
    const tabButtons = document.querySelectorAll('.snack-tab-btn');
    const productCards = document.querySelectorAll('.snack-product-card');

    tabButtons.forEach(tab => {
        tab.addEventListener('click', () => {
            tabButtons.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const categoria = tab.dataset.categoria;
            productCards.forEach(card => {
                if (categoria === 'todos' || card.dataset.categoria === categoria) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // Controles de Quantidade (+ e -)
    document.querySelectorAll('.btn-counter-plus').forEach(btn => {
        btn.addEventListener('click', () => {
            const pid = btn.dataset.productId;
            const nome = btn.dataset.productName;
            const preco = parseFloat(btn.dataset.productPrice);
            const inputQtd = document.getElementById(`qtd-input-${pid}`);

            let atual = parseInt(inputQtd.value || 0);
            if (atual >= 20) return;
            atual += 1;
            inputQtd.value = atual;

            cart.set(pid, { id: pid, nome: nome, preco: preco, qtd: atual });
            atualizarResumoBomboniere();
        });
    });

    document.querySelectorAll('.btn-counter-minus').forEach(btn => {
        btn.addEventListener('click', () => {
            const pid = btn.dataset.productId;
            const nome = btn.dataset.productName;
            const preco = parseFloat(btn.dataset.productPrice);
            const inputQtd = document.getElementById(`qtd-input-${pid}`);

            let atual = parseInt(inputQtd.value || 0);
            if (atual > 0) {
                atual -= 1;
                inputQtd.value = atual;

                if (atual === 0) {
                    cart.delete(pid);
                } else {
                    cart.set(pid, { id: pid, nome: nome, preco: preco, qtd: atual });
                }
                atualizarResumoBomboniere();
            }
        });
    });

    function atualizarResumoBomboniere() {
        let subtotalBomboniere = 0;
        let html = '';

        cart.forEach((item, pid) => {
            const sub = item.preco * item.qtd;
            subtotalBomboniere += sub;

            html += `
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div>
                        <span style="font-weight: 700; color: #fff;">${item.qtd}x</span> 
                        <span style="color: var(--text-secondary);">${item.nome}</span>
                    </div>
                    <span style="font-weight: 700; color: #fff;">${formatarMoeda(sub)}</span>
                </div>
            `;
        });

        if (bomboniereItemsListEl) {
            bomboniereItemsListEl.innerHTML = html || '<p style="color: var(--text-muted); font-size: 0.85rem; font-style: italic;">Nenhum produto adicionado.</p>';
        }

        if (subtotalBomboniereEl) {
            subtotalBomboniereEl.textContent = formatarMoeda(subtotalBomboniere);
        }

        const grandTotal = totalIngressosVal + subtotalBomboniere;
        if (grandTotalEl) {
            grandTotalEl.textContent = formatarMoeda(grandTotal);
        }
    }

    function navegarParaCheckout(incluirBomboniere = true) {
        const itensSerialized = [];
        if (incluirBomboniere) {
            cart.forEach((item) => {
                if (item.qtd > 0) {
                    itensSerialized.push(`${item.id}:${item.qtd}`);
                }
            });
        }

        const queryParams = new URLSearchParams({
            sessao_id: sessaoId,
            assentos_ids: assentosIdsStr,
            tipos_ingressos: tiposIngressosStr,
            itens_bomboniere: itensSerialized.join(',')
        });

        window.location.href = `/checkout?${queryParams.toString()}`;
    }

    if (btnAvancar) {
        btnAvancar.addEventListener('click', () => navegarParaCheckout(true));
    }

    if (btnPular) {
        btnPular.addEventListener('click', () => navegarParaCheckout(false));
    }
});
