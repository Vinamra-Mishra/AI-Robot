document.addEventListener('DOMContentLoaded', () => {
    // --- MOVEMENT CONTROLS ---
    const sendCommand = (command) => {
        const directionMap = {
            'move_forward': 'forward',
            'move_backward': 'backward',
            'turn_left': 'left',
            'turn_right': 'right',
            'stop': 'stop'
        };
        const direction = directionMap[command];

        if (direction) {
            fetch(`/move/${direction}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log(`Server response:`, data);
                const lastCommandEl = document.getElementById('lastCommand');
                if (lastCommandEl) {
                    lastCommandEl.textContent = command;
                }
            })
            .catch(error => {
                console.error('Error sending command:', error);
                const connectionText = document.getElementById('connectionText');
                if(connectionText) connectionText.textContent = 'Connection Lost';
                const connectionStatus = document.getElementById('connectionStatus');
                if(connectionStatus) connectionStatus.classList.add('disconnected');
            });
        }
    };

    document.querySelectorAll('.control-btn').forEach(button => {
        button.addEventListener('click', () => {
            const command = button.getAttribute('data-command');
            sendCommand(command);
        });
    });

    document.addEventListener('keydown', (event) => {
        if (event.target.id === 'textInput') return;

        let command = null;
        switch (event.key) {
            case 'ArrowUp': command = 'move_forward'; break;
            case 'ArrowDown': command = 'move_backward'; break;
            case 'ArrowLeft': command = 'turn_left'; break;
            case 'ArrowRight': command = 'turn_right'; break;
            case ' ': event.preventDefault(); command = 'stop'; break;
        }

        if (command) {
            sendCommand(command);
        }
    });

    // --- TEXT COMMUNICATION ---
    const textInput = document.getElementById('textInput');
    const sendBtn = document.getElementById('sendBtn');
    const aiResponseEl = document.getElementById('aiResponse');
    const responseTimestampEl = document.getElementById('responseTimestamp');
    const conversationHistoryEl = document.getElementById('conversationHistory');

    const addActivityEntry = (type, text) => {
        const placeholder = conversationHistoryEl.querySelector('.placeholder-text');
        if (placeholder) {
            placeholder.remove();
        }

        const entry = document.createElement('div');
        entry.className = 'activity-entry fade-in';
        const timestamp = new Date().toLocaleTimeString();

        entry.innerHTML = `
            <div class="activity-content">
                <div class="activity-type">${type}</div>
                <div class="activity-text">${text}</div>
            </div>
            <div class="activity-timestamp">${timestamp}</div>
        `;
        conversationHistoryEl.prepend(entry);
    };

    const sendText = () => {
        const text = textInput.value.trim();
        if (!text) return;

        addActivityEntry('You', text);
        textInput.value = '';
        aiResponseEl.innerHTML = '<p class="placeholder-text">AI is thinking...</p>';

        fetch('/api/send_text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                aiResponseEl.innerHTML = `<p>${data.response}</p>`;
                responseTimestampEl.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
                addActivityEntry('Robot', data.response);
            } else {
                aiResponseEl.innerHTML = `<p class="error-highlight">Error: ${data.message}</p>`;
            }
        })
        .catch(error => {
            console.error('Error sending text:', error);
            aiResponseEl.innerHTML = `<p class="error-highlight">Error: Could not connect to the server.</p>`;
        });
    };

    sendBtn.addEventListener('click', sendText);

    textInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendText();
        }
    });
});
