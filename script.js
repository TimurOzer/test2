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

        // Genesis bloğu
        if (blocks.genesis) {
            createBlockRow([blocks.genesis], 'genesis-row');
        }

        // Alpha, Security ve Beta blokları
        for (let i = 0; i < 2; i++) {
            createBlockRow([blocks.alpha[i], `alpha-row-${i + 1}`);
            createBlockRow([blocks.security[i]], `security-row-${i + 1}`);
            createBlockRow([blocks.beta[i]], `beta-row-${i + 1}`);
        }
    }

    // Blok satırı oluştur
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

    // Blok elementi oluştur
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

    // İçerik formatlama
    function formatContent(data) {
        return Object.entries(data).map(([key, value]) => {
            // Hash ve adresler
            if (['hash', 'token_address', 'security_data'].some(k => key.toLowerCase().includes(k))) {
                return `
                    <div class="copy-field" data-copy="${value}">
                        <strong>${key}:</strong>
                        <span class="short-value">${value.slice(0, 6)}...${value.slice(-4)}</span>
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