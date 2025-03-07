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

    // Blok verilerini yükle
    async function fetchBlockData(file) {
        try {
            const response = await fetch(`data/${file}`);
            if (!response.ok) throw new Error(`HTTP error! ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Error loading ${file}:`, error);
            return null;
        }
    }

    // Blockchain görselleştirme
    async function visualizeBlockchain() {
        container.innerHTML = '';
        
        const blocks = {
            genesis: await fetchBlockData('genesis_block.json'),
            alpha: await Promise.all([1, 2].map(i => fetchBlockData(`alpha${i}.json`))),
            security: await Promise.all([1, 2].map(i => fetchBlockData(`security${i}.json`))),
            beta: await Promise.all([1, 2].map(i => fetchBlockData(`beta${i}.json`)))
        };

        // Blokları oluştur
        createBlock('genesis', blocks.genesis);
        [0, 1].forEach(i => {
            createBlockRow([
                blocks.alpha[i],
                blocks.security[i],
                blocks.beta[i]
            ]);
        });
    }

    function createBlock(type, data) {
        if (!data) return;
        
        const block = document.createElement('div');
        block.className = `block ${type}`;
        block.innerHTML = `
            <div class="block-header">${data.blockName || 'Baklava Block'}</div>
            <div class="block-content">${formatContent(data)}</div>
        `;
        container.appendChild(block);
    }

    function createBlockRow(blocks) {
        const row = document.createElement('div');
        row.className = 'block-row';
        blocks.forEach(block => {
            if (block) {
                const div = document.createElement('div');
                div.className = 'block';
                div.innerHTML = `
                    <div class="block-header">${block.blockName}</div>
                    <div class="block-content">${formatContent(block)}</div>
                `;
                row.appendChild(div);
            }
        });
        container.appendChild(row);
    }

    // İçerik formatlama
    function formatContent(data) {
        return Object.entries(data).map(([key, value]) => {
            // Hash ve adresler
            if (['hash','token_address','security_data'].some(k => key.toLowerCase().includes(k))) {
                return `
                    <div class="copy-field" data-copy="${value}">
                        <strong>${key}:</strong>
                        <span class="short-value">${value.slice(0,6)}...${value.slice(-4)}</span>
                        <span class="copy-hint">Click to copy</span>
                    </div>
                `;
            }
            
            // Timestamp
            if (key.toLowerCase() === 'timestamp') {
                const date = new Date(value * 1000).toLocaleString();
                return `
                    <div class="copy-field" data-copy="${value}">
                        <strong>${key}:</strong>
                        <span>${date}</span>
                        <span class="copy-hint">Click to copy Unix time</span>
                    </div>
                `;
            }

            // Normal alanlar
            return `<div class="data-field"><strong>${key}:</strong> ${value}</div>`;
        }).join('');
    }

    // Arama fonksiyonu
    searchButton.addEventListener('click', async () => {
        const term = blockInput.value.trim();
        if (term) alert('Search feature coming soon!');
    });

    // İlk yükleme
    visualizeBlockchain();
});