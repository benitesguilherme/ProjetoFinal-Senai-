/* ====================================================================
   CineSENAI & Teatro - Lógica Interativa do Mapa de Assentos
   Autores: O Usuário e Sandro
   ==================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const seatButtons = document.querySelectorAll('.seat-chair:not(.seat-occupied)');
    const selectedListContainer = document.getElementById('selectedSeatsList');
    const emptyStateText = document.getElementById('emptyStateText');
    const grandTotalElement = document.getElementById('grandTotalVal');
    const selectedCountElement = document.getElementById('selectedCount');
    const btnContinuar = document.getElementById('btnContinuarBomboniere');

    // Preço base fornecido pelo template
    const precoBase = parseFloat(document.getElementById('sessaoInfoData')?.dataset.precoBase || 40.0);
    const sessaoId = document.getElementById('sessaoInfoData')?.dataset.sessaoId;

    // Estado local dos assentos selecionados: { seatId: { id, code, type: 'INTEIRA', price } }
    let selectedSeats = new Map();

    seatButtons.forEach(button => {
        button.addEventListener('click', () => {
            const seatId = button.dataset.seatId;
            const seatCode = button.dataset.seatCode;
            const seatType = button.dataset.seatType;

            if (selectedSeats.has(seatId)) {
                // Deselecionar
                selectedSeats.delete(seatId);
                button.classList.remove('seat-selected');
            } else {
                // Limite de até 8 ingressos por compra
                if (selectedSeats.size >= 8) {
                    alert('Você pode selecionar no máximo 8 assentos por pedido.');
                    return;
                }
                // Selecionar (padrão Inteira)
                selectedSeats.set(seatId, {
                    id: seatId,
                    code: seatCode,
                    tipo: 'INTEIRA',
                    preco: precoBase
                });
                button.classList.add('seat-selected');
            }

            button.setAttribute("aria-pressed", String(selectedSeats.has(seatId)));
            atualizarPainelResumo();
        });
    });

    function atualizarPainelResumo() {
        const count = selectedSeats.size;
        if (selectedCountElement) selectedCountElement.textContent = count;

        if (count === 0) {
            if (emptyStateText) emptyStateText.style.display = 'block';
            if (selectedListContainer) selectedListContainer.innerHTML = '';
            if (grandTotalElement) grandTotalElement.textContent = formatarMoeda(0);
            if (btnContinuar) {
                btnContinuar.disabled = true;
                btnContinuar.classList.add('btn-disabled');
            }
            return;
        }

        if (emptyStateText) emptyStateText.style.display = 'none';
        if (btnContinuar) {
            btnContinuar.disabled = false;
            btnContinuar.classList.remove('btn-disabled');
        }

        // Renderiza itens no painel
        let html = '';
        let total = 0;

        selectedSeats.forEach((item, id) => {
            const precoItem = item.tipo === 'INTEIRA' ? precoBase : (precoBase * 0.5);
            item.preco = precoItem;
            total += precoItem;

            html += `
                <div class="selected-seat-row-item" data-id="${id}">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="seat-code-badge">${item.code}</span>
                        <select aria-label="Tipo do ingresso para ${item.code}" class="ticket-type-select" onchange="alterarTipoIngresso('${id}', this.value)">
                            <option value="INTEIRA" ${item.tipo === 'INTEIRA' ? 'selected' : ''}>Inteira (${formatarMoeda(precoBase)})</option>
                            <option value="MEIA" ${item.tipo === 'MEIA' ? 'selected' : ''}>Meia-Entrada (${formatarMoeda(precoBase * 0.5)})</option>
                        </select>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span class="seat-price-display">${formatarMoeda(precoItem)}</span>
                        <button type="button" onclick="removerAssento('${id}')" style="background: none; border: none; color: #ef4444; cursor: pointer; font-size: 1rem;" title="Remover assento">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </div>
            `;
        });

        if (selectedListContainer) selectedListContainer.innerHTML = html;
        if (grandTotalElement) grandTotalElement.textContent = formatarMoeda(total);
    }

    // Funções globais chamadas pelos selects inline
    window.alterarTipoIngresso = function(seatId, novoTipo) {
        if (selectedSeats.has(seatId)) {
            const item = selectedSeats.get(seatId);
            item.tipo = novoTipo;
            atualizarPainelResumo();
        }
    };

    window.removerAssento = function(seatId) {
        if (selectedSeats.has(seatId)) {
            selectedSeats.delete(seatId);
            const btn = document.querySelector(`.seat-chair[data-seat-id="${seatId}"]`);
            if (btn) btn.classList.remove('seat-selected');
            atualizarPainelResumo();
        }
    };

    // Ação do botão avançar
    if (btnContinuar) {
        btnContinuar.addEventListener('click', () => {
            if (selectedSeats.size === 0) {
                alert('Por favor, selecione pelo menos um assento.');
                return;
            }

            const ids = [];
            const tipos = [];

            selectedSeats.forEach(item => {
                ids.push(item.id);
                tipos.push(item.tipo);
            });

            const queryParams = new URLSearchParams({
                assentos_selecionados: ids.join(','),
                tipos_ingressos: tipos.join(',')
            });

            window.location.href = `/sessao/${sessaoId}/bomboniere?${queryParams.toString()}`;
        });
    }

    // Polling em tempo real (a cada 5s) para atualizar cadeiras ocupadas concorrentemente
    if (sessaoId) {
        setInterval(async () => {
            try {
                const resp = await fetch(`/api/sessao/${sessaoId}/assentos`);
                if (!resp.ok) return;
                const data = await resp.json();
                if (data && Array.isArray(data.assentos)) {
                    let assentoConflito = false;
                    data.assentos.forEach(a => {
                        const btn = document.querySelector(`.seat-chair[data-seat-id="${a.id}"]`);
                        if (btn && a.ocupado === 1) {
                            if (!btn.classList.contains('seat-occupied')) {
                                btn.classList.add('seat-occupied');
                                btn.disabled = true;
                                btn.title = `Assento ${a.codigo} Ocupado`;
                            }
                            if (selectedSeats.has(String(a.id))) {
                                selectedSeats.delete(String(a.id));
                                btn.classList.remove('seat-selected');
                                assentoConflito = true;
                            }
                        }
                    });
                    if (assentoConflito) {
                        alert('Aviso: Uma das poltronas que você selecionou acabou de ser confirmada por outro cliente e foi desmarcada.');
                        atualizarPainelResumo();
                    }
                }
            } catch (err) {
                // Silêncio em oscilações de rede
            }
        }, 5000);
    }
});
