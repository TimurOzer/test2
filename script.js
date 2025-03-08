document.addEventListener("DOMContentLoaded", async function () {
    const container = document.getElementById("blockchain-container");
    const searchButton = document.getElementById("search-button");
    const blockInput = document.getElementById("block-input");
    const hashRegistry = new Map();

    // Kopyalama olayı
    container.addEventListener('click', (event) => {
        const target = event.target.closest('[data-copy]');
        if (target) {
            const value = target.dataset.copy;
            navigator.clipboard.writeText(value)
                .then(() => showNotification('✓ Copied to clipboard!'))
                .catch(() => showNotification('⚠️ Failed to copy!'));
        }
    });

    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'copy-notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 2000);
    }

    async function fetchBlockData(file) {
        try {
            const response = await fetch(`data/${file}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Error fetching block data:`, error);
            return null;
        }
    }

async function visualizeBlockchain() {
    container.innerHTML = '';
    hashRegistry.clear();

    // Genesis bloğunu çek
    const genesisBlock = await fetchBlockData('genesis_block.json');
    createBlockRow([genesisBlock], 'genesis-row');

    // Alpha, Security ve Beta bloklarını çek
    let i = 1;
    while (true) {
        try {
            // Alpha, Security ve Beta bloklarını aynı anda çek
            const [alphaBlock, securityBlock, betaBlock] = await Promise.all([
                fetchBlockData(`alpha${i}.json`),
                fetchBlockData(`security${i}.json`),
                fetchBlockData(`beta${i}.json`)
            ]);

            // Blokları görselleştir
            createBlockRow([alphaBlock, securityBlock], `layer-${i}`);
            createBlockRow([betaBlock], `beta-${i}`);

            i++; // Sonraki blok setine geç
        } catch (error) {
            console.error('Blok verisi çekme hatası veya dosya bulunamadı:', error);
            break; // Hata durumunda veya dosya bulunamadığında döngüyü sonlandır
        }
    }

    console.log('Tüm bloklar başarıyla çekildi ve görselleştirildi.');
}

    function createBlockRow(blockData, rowClass) {
        const row = document.createElement('div');
        row.className = `block-row ${rowClass}`;
        
        blockData.forEach(data => {
            if (data) {
                const block = createBlockElement(data);
                row.appendChild(block);
                registerHashes(data, block);
            }
        });

        container.appendChild(row);
    }

    function createBlockElement(data) {
        const block = document.createElement('div');
        block.className = 'block';

        // Hash'i belirle ve kaydet
        const mainHash = data.block_hash || data.security_hash || data.hash;
        if (mainHash) {
            block.id = mainHash.toLowerCase();
            block.dataset.mainHash = mainHash;
        }

        const header = document.createElement('div');
        header.className = 'block-header';
        header.textContent = data.blockName || "Baklava Block";

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

            if (specialFields.hash.some(f => key.toLowerCase().includes(f))) {
                return `
                    <div class="copy-field" data-copy="${value}">
                        <strong>${key}:</strong>
                        <span class="short-value">${value.slice(0, 6)}...${value.slice(-4)}</span>
                        <span class="copy-hint">Click to copy</span>
                    </div>
                `;
            }

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

            if (specialFields.code.some(f => key.toLowerCase().includes(f))) {
                return `
                    <div class="copy-field">
                        <strong>${key}:</strong>
                        <span>${value}</span>
                    </div>
                `;
            }

            return `<div class="data-field"><strong>${key}:</strong> ${value}</div>`;
        }).join('');
    }

    function registerHashes(data, element) {
        const hashFields = [
            'block_hash', 'security_hash', 'prev_alpha_hash',
            'prev_security_hash', 'security_data', 'previous_hash',
            'token_address', 'prev_hash_1', 'prev_hash_2'
        ];

        hashFields.forEach(field => {
            if (data[field]) {
                const hash = data[field].toLowerCase();
                hashRegistry.set(hash, element);
            }
        });
    }

    // Arama fonksiyonu
    searchButton.addEventListener('click', async () => {
        const searchTerm = blockInput.value.trim().toLowerCase();
        if (!searchTerm) return;

        const targetBlock = hashRegistry.get(searchTerm) || document.getElementById(searchTerm);

        if (targetBlock) {
            targetBlock.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });

            targetBlock.classList.add('highlight');
            setTimeout(() => {
                targetBlock.classList.remove('highlight');
            }, 2000);
        } else {
            showNotification('⛔ Block not found!');
        }
    });

    // İlk yükleme
    visualizeBlockchain();
});
