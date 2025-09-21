document.addEventListener("DOMContentLoaded", () => {
    // --- Elementos do DOM ---
    const systemStatusEl = document.getElementById("system-status-content");
    const engineStatusEl = document.getElementById("engine-status-content");
    const jobStatusEl = document.getElementById("job-status-content");

    const chatWindow = document.getElementById("chat-window");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");

    let socket;
    const socketURL = `ws://${window.location.host}/api/dashboard/ws`;

    function connect() {
        console.log("Tentando conectar ao WebSocket...");
        socket = new WebSocket(socketURL);

        socket.onopen = () => {
            console.log("WebSocket conectado com sucesso.");
            if(systemStatusEl) systemStatusEl.textContent = "Conectado. Aguardando dados...";
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "dashboard_update") {
                updateDashboard(data.data);
            }
        };

        socket.onerror = (error) => {
            console.error("Erro no WebSocket:", error);
            if(systemStatusEl) systemStatusEl.textContent = "Erro na conexão.";
        };

        socket.onclose = () => {
            console.log("WebSocket desconectado. Tentando reconectar em 5 segundos...");
            if(systemStatusEl) systemStatusEl.textContent = "Desconectado. Tentando reconectar...";
            setTimeout(connect, 5000); // Tenta reconectar após 5 segundos
        };
    }

    function updateDashboard(data) {
        if (!data) return;

        // --- System Status ---
        if (systemStatusEl && data.system) {
            if (data.system.error) {
                systemStatusEl.textContent = `Erro: ${data.system.error}`;
            } else {
                systemStatusEl.textContent = `Status: ${data.system.status || 'N/A'}\nVersão: ${data.system.version || 'N/A'}`;
            }
        }

        // --- Engine Status ---
        if (engineStatusEl && data.engines) {
            if (data.engines.error) {
                engineStatusEl.textContent = `Erro: ${data.engines.error}`;
            } else {
                const engines = data.engines.engines || [];
                engineStatusEl.textContent = engines.map(e => `  - ${e.name} (${e.status})`).join('\n');
            }
        }

        // --- Job Status ---
        if (jobStatusEl && data.jobs) {
             if (data.jobs.error) {
                jobStatusEl.textContent = `Erro: ${data.jobs.error}`;
            } else {
                const jobs = data.jobs.jobs || [];
                jobStatusEl.textContent = jobs.map(j => `  - ${j.name} [${j.status}] @ ${j.workstation}`).join('\n');
            }
        }
    }

    // Inicia a conexão
    connect();

    // --- Lógica do Chat ---

    function addMessageToChat(message, sender) {
        const messageEl = document.createElement("p");
        messageEl.classList.add(`${sender}-message`);
        messageEl.textContent = message;
        chatWindow.appendChild(messageEl);
        chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll
    }

    async function handleSendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        addMessageToChat(message, "user");

        chatInput.value = ""; // Limpa o input
        chatInput.disabled = true;
        sendBtn.disabled = true;

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: message }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            addMessageToChat(data.reply, "bot");

        } catch (error) {
            console.error("Erro ao enviar mensagem:", error);
            addMessageToChat("Desculpe, ocorreu um erro ao contatar a IA.", "bot");
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    }

    sendBtn.addEventListener("click", handleSendMessage);
    chatInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            handleSendMessage();
        }
    });
});
