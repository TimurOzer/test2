document.addEventListener("DOMContentLoaded", async function () {
    const container = document.getElementById("blockchain-container");
    const searchButton = document.getElementById("search-button");
    const blockInput = document.getElementById("block-input");

    // Kopyalama olayı için event delegation
    container.addEventListener('click', (event) => {
        const target = event.target.closest('[data-copy]');
        if (target) {
            const value = target.dataset.copy;
            navigator.clipboard.writeText(value)
                .then(() => showNotification('✓ Copied to clipboard!'))
                .catch(() => showNotification('⚠️ Failed to copy!'));
        }
    });

    // Bildirim göster
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'copy-notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 2000);
    }

    // Fetch JSON data
    async function fetchBlockData(file) {
        try {
            const response = await fetch(`data/${file}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching block data:', error);
            return null;
        }
    }

    // Blockchain visualization
    async function visualizeBlockchain() {
        container.innerHTML = '';
        const blocks = {
            genesis: await fetchBlockData('genesis_block.json'),
            alpha: await Promise.all([1, 2].map(i => fetchBlockData(`alpha${i}.json`))),
            security: await Promise.all([1, 2].map(i => fetchBlockData(`security${i}.json`))),
            beta: await Promise.all([1, 2].map(i => fetchBlockData(`beta${i}.json`)))
        };

        // Create blockchain structure
        createBlockRow([blocks.genesis], 'genesis-row');
        
        for (let i = 0; i < 2; i++) {
            createBlockRow([blocks.alpha[i], blocks.security[i]], `layer-${i+1}`);
            createBlockRow([blocks.beta[i]], `beta-${i+1}`);
        }
    }

    function createBlockRow(blockData, rowClass) {
        const row = document.createElement('div');
        row.className = `block-row ${rowClass}`;
        
        blockData.forEach(data => {
            if (data) {
                const block = createBlockElement(data);
                row.appendChild(block);
            }
        });
        
        container.appendChild(row);
    }

    function createBlockElement(data) {
        const block = document.createElement('div');
        block.className = 'block';
        
        const header = document.createElement('div');
        header.className = 'block-header';
        header.textContent = data.blockName || 'Baklava Block';
        
        const content = document.createElement('div');
        content.className = 'block-content';
        content.innerHTML = formatContent(data);

        block.appendChild(header);
        block.appendChild(content);
        return block;
    }

    function formatContent(data) {
        return Object.entries(data).map(([key, value]) => {
            const specialFields = {
                hash: ['hash', 'merkleroot', 'signature', 'token_address', 'security_data', 'block_hash', 'prev_hash_1', 'prev_hash_2'],
                timestamp: ['timestamp', 'time', 'date'],
                code: ['address', 'id', 'nonce', 'max_supply', 'recipient', 'amount', 'tag']
            };

            // Hash Benzeri Alanlar
            if (specialFields.hash.some(f => key.toLowerCase().includes(f))) {
                const formattedValue = typeof value === 'string' ? value : JSON.stringify(value);
                return `
                    <div class="copy-field" data-copy="${formattedValue}">
                        <strong>${key}:</strong>
                        <span class="short-value">${formattedValue.slice(0, 6)}...${formattedValue.slice(-4)}</span>
                        <span class="copy-hint">Click to copy</span>
                    </div>
                `;
            }

            // Timestamp Alanları
            if (specialFields.timestamp.includes(key.toLowerCase())) {
                const date = new Date(value * 1000).toLocaleString();
                return `
                    <div class="copy-field" data-copy="${value}">
                        <strong>${key}:</strong>
                        <span>${date}</span>
                        <span class="copy-hint">Click to copy Unix time</span>
                    </div>
                `;
            }

            // Kod Benzeri Alanlar (max_supply, nonce, recipient, amount, tag)
            if (specialFields.code.some(f => key.toLowerCase().includes(f))) {
                return `
                    <div class="copy-field">
                        <strong>${key}:</strong>
                        <span>${value}</span>
                    </div>
                `;
            }

            // Normal alanlar
            return `<div class="data-field"><strong>${key}:</strong> ${value}</div>`;
        }).join('');
    }

    // Arama fonksiyonu
    searchButton.addEventListener('click', async () => {
        const searchTerm = blockInput.value.trim().toLowerCase();
        if (!searchTerm) return;

        // Sayfanın ilgili bloğuna kaydırma işlemi
        const blockElement = document.querySelector(`.${searchTerm}`);
        if (blockElement) {
            blockElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            alert('No block found matching the search term.');
        }
    });

    // İlk yükleme
    visualizeBlockchain();
});
