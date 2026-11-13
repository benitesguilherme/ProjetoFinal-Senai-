/* ====================================================================
   CineSENAI & Teatro - Lógica do Checkout e Pagamento Simulado
   Autores: O Usuário e Sandro
   ==================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Alternador de Métodos de Pagamento
    const paymentTabButtons = document.querySelectorAll('.payment-method-radio-card');
    const paymentSections = document.querySelectorAll('.payment-detail-section');
    let selectedPaymentMethod = 'PIX';

    paymentTabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            paymentTabButtons.forEach(b => { b.classList.remove('selected'); b.setAttribute('aria-pressed','false'); });
            btn.setAttribute('aria-pressed','true');
            btn.classList.add('selected');

            selectedPaymentMethod = btn.dataset.method;

            paymentSections.forEach(sec => {
                if (sec.id === `section-${selectedPaymentMethod}`) {
                    sec.style.display = 'block';
                } else {
                    sec.style.display = 'none';
                }
            });
        });
    });

    // 2. Máscaras de Entrada (CPF, Telefone, Cartão)
    const cpfInput = document.getElementById('inputCpf');
    if (cpfInput) {
        cpfInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '');
            if (val.length > 11) val = val.slice(0, 11);
            val = val.replace(/(\d{3})(\d)/, '$1.$2');
            val = val.replace(/(\d{3})(\d)/, '$1.$2');
            val = val.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
            e.target.value = val;
        });
    }

    const telInput = document.getElementById('inputTelefone');
    if (telInput) {
        telInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '');
            if (val.length > 11) val = val.slice(0, 11);
            if (val.length > 10) {
                val = val.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
            } else if (val.length > 5) {
                val = val.replace(/^(\d{2})(\d{4})(\d{0,4})$/, '($1) $2-$3');
            } else if (val.length > 2) {
                val = val.replace(/^(\d{2})(\d{0,5})$/, '($1) $2');
            }
            e.target.value = val;
        });
    }

    // 3. Detecção de Bandeira e Validação do Cartão de Crédito
    const cardNumInput = document.getElementById('cardNumero');
    const cardNameInput = document.getElementById('cardNome');
    const cardExpInput = document.getElementById('cardValidade');
    const cardCvvInput = document.getElementById('cardCvv');

    const previewNum = document.getElementById('previewCardNum');
    const previewName = document.getElementById('previewCardName');
    const previewExp = document.getElementById('previewCardExp');
    const previewBrandName = document.getElementById('previewCardBrandName');
    const previewBrandIcon = document.getElementById('previewCardBrandIcon');
    const cardNumStatusIcon = document.getElementById('cardNumStatusIcon');
    const brandPills = document.querySelectorAll('.brand-pill');

    function detectarBandeira(numeroLimpo) {
        if (!numeroLimpo) {
            return { nome: 'CARTÃO', iconClass: 'fa-solid fa-credit-card', cor: '#94a3b8' };
        }
        // Elo
        const eloPrefixes = ['4011', '4389', '4514', '4576', '5041', '5066', '5067', '5090', '6277', '6362', '6363', '6504', '6509', '6516', '6550'];
        for (const pref of eloPrefixes) {
            if (numeroLimpo.startsWith(pref)) {
                return { nome: 'ELO', iconClass: 'fa-solid fa-credit-card', cor: '#00a4e4' };
            }
        }
        // Amex (34 ou 37)
        if (numeroLimpo.startsWith('34') || numeroLimpo.startsWith('37')) {
            return { nome: 'AMEX', iconClass: 'fa-brands fa-cc-amex', cor: '#007bc1' };
        }
        // Hipercard (606282 ou 3841)
        if (numeroLimpo.startsWith('606282') || numeroLimpo.startsWith('3841')) {
            return { nome: 'HIPERCARD', iconClass: 'fa-solid fa-credit-card', cor: '#d92525' };
        }
        // Visa (inicia com 4)
        if (numeroLimpo.startsWith('4')) {
            return { nome: 'VISA', iconClass: 'fa-brands fa-cc-visa', cor: '#1a1f71' };
        }
        // Mastercard (51-55 ou 22-27)
        const p2 = parseInt(numeroLimpo.slice(0, 2), 10);
        const p4 = parseInt(numeroLimpo.slice(0, 4), 10);
        if ((p2 >= 51 && p2 <= 55) || (p4 >= 2221 && p4 <= 2720)) {
            return { nome: 'MASTERCARD', iconClass: 'fa-brands fa-cc-mastercard', cor: '#ff5f00' };
        }
        return { nome: 'CARTÃO', iconClass: 'fa-regular fa-credit-card', cor: '#cbd5e1' };
    }

    function atualizarVisualBandeira(bandeira) {
        if (previewBrandName) previewBrandName.textContent = bandeira.nome;
        if (previewBrandIcon) {
            previewBrandIcon.className = bandeira.iconClass;
            previewBrandIcon.style.color = bandeira.cor;
        }
        brandPills.forEach(pill => {
            if (pill.dataset.brand === bandeira.nome) {
                pill.style.background = 'var(--accent-gold)';
                pill.style.color = '#000';
                pill.style.fontWeight = 'bold';
            } else {
                pill.style.background = 'rgba(255,255,255,0.06)';
                pill.style.color = 'var(--text-muted)';
                pill.style.fontWeight = 'normal';
            }
        });
    }

    if (cardNumInput) {
        cardNumInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '').slice(0, 16);
            const bandeira = detectarBandeira(val);
            atualizarVisualBandeira(bandeira);

            let formatted = val.replace(/(\d{4})/g, '$1 ').trim();
            e.target.value = formatted;
            if (previewNum) previewNum.textContent = formatted || '•••• •••• •••• ••••';

            // Feedback visual no campo
            const minLen = bandeira.nome === 'AMEX' ? 15 : 16;
            if (val.length >= minLen) {
                cardNumInput.style.borderColor = '#00e676';
                if (cardNumStatusIcon) {
                    cardNumStatusIcon.style.display = 'block';
                    cardNumStatusIcon.innerHTML = '<i class="fa-solid fa-circle-check" style="color: #00e676;"></i>';
                }
                const errEl = document.getElementById('cardNumErrorMsg');
                if (errEl) errEl.style.display = 'none';
            } else {
                cardNumInput.style.borderColor = 'var(--border-color)';
                if (cardNumStatusIcon) cardNumStatusIcon.style.display = 'none';
            }
        });
    }

    if (cardNameInput) {
        cardNameInput.addEventListener('input', (e) => {
            const val = e.target.value.toUpperCase();
            if (previewName) previewName.textContent = val || 'NOME NO CARTÃO';
            const errEl = document.getElementById('cardNomeErrorMsg');
            if (val.length >= 3) {
                cardNameInput.style.borderColor = '#00e676';
                if (errEl) errEl.style.display = 'none';
            } else {
                cardNameInput.style.borderColor = 'var(--border-color)';
            }
        });
    }

    if (cardExpInput) {
        cardExpInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '').slice(0, 4);
            if (val.length > 2) val = val.slice(0, 2) + '/' + val.slice(2);
            e.target.value = val;
            if (previewExp) previewExp.textContent = val || 'MM/AA';

            const errEl = document.getElementById('cardExpErrorMsg');
            if (val.length === 5) {
                const [mesStr, anoStr] = val.split('/');
                const mes = parseInt(mesStr, 10);
                const ano = parseInt(anoStr, 10);
                const agora = new Date();
                const anoAtual = agora.getFullYear() % 100;
                const mesAtual = agora.getMonth() + 1;

                if (mes >= 1 && mes <= 12 && (ano > anoAtual || (ano === anoAtual && mes >= mesAtual))) {
                    cardExpInput.style.borderColor = '#00e676';
                    if (errEl) errEl.style.display = 'none';
                } else {
                    cardExpInput.style.borderColor = '#ef4444';
                    if (errEl) {
                        errEl.textContent = 'Validade vencida ou mês inválido.';
                        errEl.style.display = 'block';
                    }
                }
            } else {
                cardExpInput.style.borderColor = 'var(--border-color)';
                if (errEl) errEl.style.display = 'none';
            }
        });
    }

    if (cardCvvInput) {
        cardCvvInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '').slice(0, 4);
            e.target.value = val;
            const errEl = document.getElementById('cardCvvErrorMsg');
            if (val.length >= 3) {
                cardCvvInput.style.borderColor = '#00e676';
                if (errEl) errEl.style.display = 'none';
            } else {
                cardCvvInput.style.borderColor = 'var(--border-color)';
            }
        });
    }

    // 4. Temporizador Regressivo do PIX (15 Minutos)
    const timerElement = document.getElementById('pixCountdownTimer');
    if (timerElement) {
        let totalSeconds = 15 * 60;
        const interval = setInterval(() => {
            totalSeconds--;
            if (totalSeconds <= 0) {
                clearInterval(interval);
                timerElement.textContent = '00:00 - Expirado';
                return;
            }
            const mins = Math.floor(totalSeconds / 60);
            const secs = totalSeconds % 60;
            timerElement.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }, 1000);
    }

    // 5. Botão Copiar Chave PIX
    const btnCopiarPix = document.getElementById('btnCopiarPix');
    if (btnCopiarPix) {
        btnCopiarPix.addEventListener('click', () => {
            const pixCode = document.getElementById('pixCodigoTexto')?.textContent;
            if (pixCode && navigator.clipboard) {
                navigator.clipboard.writeText(pixCode.trim()).then(() => {
                    btnCopiarPix.innerHTML = '<i class="fa-solid fa-check"></i> Chave Copiada!';
                    setTimeout(() => {
                        btnCopiarPix.innerHTML = '<i class="fa-solid fa-copy"></i> Copiar Código PIX';
                    }, 3000);
                });
            }
        });
    }

    // 6. Finalização da Compra com Validação e Chamada Assíncrona
    const checkoutForm = document.getElementById('checkoutForm');
    const submitBtn = document.getElementById('btnFinalizarCompra');
    const alertBox = document.getElementById('checkoutAlertBox');

    if (checkoutForm && submitBtn) {
        submitBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            // Validações básicas de identificação
            const nome = document.getElementById('inputNome')?.value.trim();
            const cpf = document.getElementById('inputCpf')?.value.trim();
            const email = document.getElementById('inputEmail')?.value.trim();
            const telefone = document.getElementById('inputTelefone')?.value.trim();

            if (!nome || !cpf || !email || !telefone) {
                mostrarAlerta('Por favor, preencha todos os campos de identificação (Nome, CPF, E-mail e Telefone).', 'warning');
                return;
            }

            if (cpf.length < 14) {
                mostrarAlerta('Informe o CPF de demonstração no formato 000.000.000-00.', 'warning');
                return;
            }

            // Validação estrita se o método for Cartão de Crédito
            if (selectedPaymentMethod === 'CARTAO_CREDITO') {
                const cNumero = cardNumInput?.value.replace(/\D/g, '') || '';
                const cNome = cardNameInput?.value.trim() || '';
                const cValidade = cardExpInput?.value.trim() || '';
                const cCvv = cardCvvInput?.value.replace(/\D/g, '') || '';

                let cardErro = false;

                if (cNumero.length < 15) {
                    cardNumInput.style.borderColor = '#ef4444';
                    const errEl = document.getElementById('cardNumErrorMsg');
                    if (errEl) { errEl.textContent = 'Informe o número do cartão (mínimo 15 ou 16 dígitos).'; errEl.style.display = 'block'; }
                    cardErro = true;
                }

                if (cNome.length < 3) {
                    cardNameInput.style.borderColor = '#ef4444';
                    const errEl = document.getElementById('cardNomeErrorMsg');
                    if (errEl) { errEl.textContent = 'Informe o nome impresso no cartão.'; errEl.style.display = 'block'; }
                    cardErro = true;
                }

                const [month, year] = cValidade.split('/').map(Number);
                const now = new Date();
                const expired = !month || month > 12 || !year || year + 2000 < now.getFullYear() || (year + 2000 === now.getFullYear() && month < now.getMonth() + 1);
                if (cValidade.length < 5 || expired) {
                    cardExpInput.style.borderColor = '#ef4444';
                    const errEl = document.getElementById('cardExpErrorMsg');
                    if (errEl) { errEl.textContent = 'Informe a validade (MM/AA).'; errEl.style.display = 'block'; }
                    cardErro = true;
                }

                if (cCvv.length < 3) {
                    cardCvvInput.style.borderColor = '#ef4444';
                    const errEl = document.getElementById('cardCvvErrorMsg');
                    if (errEl) { errEl.textContent = 'Informe o código CVV (3 ou 4 dígitos).'; errEl.style.display = 'block'; }
                    cardErro = true;
                }

                if (cardErro) {
                    mostrarAlerta('Por favor, verifique os dados do cartão de crédito destacados em vermelho antes de prosseguir.', 'warning');
                    return;
                }
            }

            // Coleta dados dos assentos e bomboniere serializados
            const sessaoId = document.getElementById('checkoutData')?.dataset.sessaoId;
            const assentosPayloadStr = document.getElementById('checkoutData')?.dataset.assentosPayload;
            const bombonierePayloadStr = document.getElementById('checkoutData')?.dataset.bombonierePayload;

            let assentosArr = [];
            let bomboniereArr = [];

            try {
                if (assentosPayloadStr) assentosArr = JSON.parse(assentosPayloadStr);
                if (bombonierePayloadStr) bomboniereArr = JSON.parse(bombonierePayloadStr);
            } catch (err) {
                console.error('Erro ao ler payloads:', err);
            }

            if (!assentosArr || assentosArr.length === 0) {
                mostrarAlerta('Nenhum assento selecionado. Por favor, reinicie a seleção.', 'warning');
                return;
            }

            // Exibe indicador de processamento
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processando Pedido...';

            try {
                const response = await fetch('/api/finalizar-compra', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sessao_id: sessaoId,
                        nome: nome,
                        cpf: cpf,
                        email: email,
                        telefone: telefone,
                        forma_pagamento: selectedPaymentMethod,
                        assentos: assentosArr,
                        bomboniere: bomboniereArr
                    })
                });

                const data = await response.json();

                if (response.ok && data.sucesso) {
                    // Redireciona para o voucher
                    window.location.href = data.redirect_url;
                } else if (response.status === 409) {
                    // Conflito de concorrência com botão de retorno facilitado
                    mostrarAlerta(data.mensagem || 'Assentos indisponíveis.', 'danger', true, sessaoId);
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fa-solid fa-shield-halved"></i> Confirmar e Emitir Ingressos';
                } else {
                    mostrarAlerta(data.mensagem || 'Não foi possível concluir o pedido. Tente novamente.', 'danger');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fa-solid fa-shield-halved"></i> Confirmar e Emitir Ingressos';
                }
            } catch (err) {
                mostrarAlerta('Erro de conexão com o servidor. Por favor, tente novamente.', 'danger');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fa-solid fa-shield-halved"></i> Confirmar e Emitir Ingressos';
            }
        });
    }

    function mostrarAlerta(msg, tipo = 'danger', showBackButton = false, sessaoIdBack = null) {
        if (!alertBox) {
            alert(msg);
            return;
        }
        let backBtnHtml = '';
        if (showBackButton && sessaoIdBack) {
            backBtnHtml = `
                <div style="margin-top: 12px;">
                    <a href="/sessao/${sessaoIdBack}/assentos" class="btn btn-primary" style="font-size: 0.85rem; padding: 8px 16px;">
                        <i class="fa-solid fa-arrow-left"></i> Voltar e Escolher Outro Assento
                    </a>
                </div>
            `;
        }
        alertBox.innerHTML = `
            <div class="alert alert-${tipo}" style="padding: 16px 20px; border-radius: var(--radius-sm); margin-bottom: 24px; background: ${tipo === 'danger' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 197, 24, 0.15)'}; border: 1px solid ${tipo === 'danger' ? '#ef4444' : '#f5c518'}; color: #fff;">
                <div style="display: flex; align-items: flex-start; gap: 12px;">
                    <i class="fa-solid fa-triangle-exclamation" style="color: ${tipo === 'danger' ? '#ef4444' : '#f5c518'}; font-size: 1.3rem; margin-top: 2px;"></i>
                    <div style="flex: 1;">
                        <span style="font-size: 0.95rem;">${msg}</span>
                        ${backBtnHtml}
                    </div>
                </div>
            </div>
        `;
        alertBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});
