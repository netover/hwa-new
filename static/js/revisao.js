document.addEventListener('DOMContentLoaded', () => {
    const reviewList = document.getElementById('review-list');
    const statusMessage = document.getElementById('status-message');
    const filterStatus = document.getElementById('filter-status');
    const searchQuery = document.getElementById('search-query');
    const applyFiltersBtn = document.getElementById('apply-filters');

    const metricPending = document.getElementById('metric-pending');
    const metricApproved = document.getElementById('metric-approved');
    const metricRejected = document.getElementById('metric-rejected');

    async function loadAudits(status = 'pending', query = '') {
        reviewList.innerHTML = '';
        statusMessage.textContent = 'Carregando revisões...';
        try {
            let url = `/api/audit/flags?status=${status}`;
            if (query) {
                url += `&query=${encodeURIComponent(query)}`;
            }
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const items = await response.json();

            if (items.length === 0) {
                statusMessage.textContent = 'Nenhuma revisão encontrada com os filtros aplicados.';
                return;
            }

            reviewList.innerHTML = items.map((item, index) => `
                <div class="review-item" id="item-${item.memory_id}">
                    <p><span class="label">ID da Memória:</span> ${item.memory_id}</p>
                    <p><span class="label">Status:</span> ${item.status}</p>
                    <p><span class="label">Pergunta do Usuário:</span></p>
                    <pre>${escapeHtml(item.user_query)}</pre>
                    <p><span class="label">Resposta do Agente:</span></p>
                    <pre>${escapeHtml(item.agent_response)}</pre>
                    <p><span class="label">Motivo da Sinalização (IA):</span> ${escapeHtml(item.ia_audit_reason || 'N/A')} (Confiança: ${item.ia_audit_confidence || 'N/A'})</p>
                    <p><span class="label">Criado em:</span> ${new Date(item.created_at).toLocaleString()}</p>
                    ${item.reviewed_at ? `<p><span class="label">Revisado em:</span> ${new Date(item.reviewed_at).toLocaleString()}</p>` : ''}
                    <div class="actions">
                        ${item.status === 'pending' ? `
                            <button class="approve-btn" data-id="${item.memory_id}">Aprovar</button>
                            <button class="reject-btn" data-id="${item.memory_id}">Rejeitar</button>
                        ` : ''}
                    </div>
                    <div class="status"></div>
                </div>
            `).join('');
            statusMessage.textContent = '';

        } catch (error) {
            statusMessage.textContent = 'Erro ao carregar revisões.';
            console.error(error);
        }
    }

    async function loadMetrics() {
        try {
            const response = await fetch('/api/audit/metrics'); // New endpoint for metrics
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const metrics = await response.json();
            metricPending.textContent = metrics.pending;
            metricApproved.textContent = metrics.approved;
            metricRejected.textContent = metrics.rejected;
        } catch (error) {
            console.error('Erro ao carregar métricas:', error);
            metricPending.textContent = 'N/A';
            metricApproved.textContent = 'N/A';
            metricRejected.textContent = 'N/A';
        }
    }

    applyFiltersBtn.addEventListener('click', () => {
        const status = filterStatus.value;
        const query = searchQuery.value;
        loadAudits(status, query);
    });

    reviewList.addEventListener('click', async (event) => {
        if (event.target.matches('.approve-btn') || event.target.matches('.reject-btn')) {
            const memoryId = event.target.dataset.id;
            const action = event.target.matches('.approve-btn') ? 'approve' : 'reject';
            const itemDiv = document.getElementById(`item-${memoryId}`);
            const statusDiv = itemDiv.querySelector('.status');

            // Disable buttons
            itemDiv.querySelector('.actions').innerHTML = '';
            statusDiv.textContent = 'Processando...';

            try {
                const response = await fetch('/api/audit/review', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        memory_id: memoryId,
                        action: action,
                    }),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Falha na requisição');
                }

                const result = await response.json();
                statusDiv.textContent = `Ação '${result.status}' concluída com sucesso.`;
                // Reload audits and metrics after successful review
                loadAudits(filterStatus.value, searchQuery.value);
                loadMetrics();

            } catch (error) {
                statusDiv.textContent = `Erro: ${error.message}`;
                console.error(error);
            }
        }
    });

    function escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') return '';
        return unsafe
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
     }

    // Initial load
    loadAudits();
    loadMetrics();
});
