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
                .then(() => showNotification('✓ Copied!'))
                .catch(() => showNotification('⚠️ Copy failed!'));
        }
    });

    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 2000);
    }

    async function fetchBlockData(file) {
        try {
            const response = await fetch(`data/${file}`);
            if (!response.ok) throw new Error(`Failed to load ${file}`);
            return await response.json();
        } catch (error) {
            console.error(`Error loading ${file}:`, error);
            return null;
        }
    }

    async function visualizeBlockchain() {
        container.innerHTML = '';
        hashRegistry.clear();

        const blocks = {
            genesis: await fetchBlockData('genesis_block.json'),
            alpha1: await fetchBlockData('alpha1.json'),
            alpha2: await fetchBlockData('alpha2.json'),
            security1: await fetchBlockData('security1.json'),
            security2: await fetchBlockData('security2.json'),
            beta1: await fetchBlockData('beta1.json'),
            beta2: await fetchBlockData('beta2.json')
        };

        createBlockRow([blocks.genesis], 'genesis');
        createBlockRow([blocks.alpha1, blocks.security1], 'alpha-security-1');
        createBlockRow([blocks.beta1], 'beta-1');
        createBlockRow([blocks.alpha2, blocks.security2], 'alpha-security-2');
        createBlockRow([blocks.beta2], 'beta-2');
    }

    function createBlockRow(blocks, rowClass) {
        const row = document.createElement('div');
        row.className = `row ${rowClass}`;
        
        blocks.forEach(blockData => {
            if (blockData) {
                const block = createBlock(blockData);
                row.appendChild(block);
                registerHashes(blockData, block);
            }
        });
        
        container.appendChild(row);
    }

    function createBlock(data) {
        const block = document.createElement('div');
        block.className = 'block';
        
        // Ana hash'i belirle
        const mainHash = data.block_hash || data.security_hash || data.hash;
        if (mainHash) {
            block.id = mainHash.toLowerCase();
            block.dataset.mainHash = mainHash;
        }

        const header = document.createElement('div');
        header.className = 'header';
        header.textContent = data.blockName || determineBlockType(data);
        
        const content = document.createElement('div');
        content.className = 'content';
        content.innerHTML = generateContent(data);

        block.appendChild(header);
        block.appendChild(content);
        return block;
    }

    function determineBlockType(data) {
        if (data.security_data) return "Security Block";
        if (data.prev_alpha_hash) return "Beta Block";
        if (data.token_address) return "Genesis Block";
        return "Alpha Block";
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

    function generateContent(data) {
        return Object.entries(data).map(([key, value]) => {
            const isHash = key.toLowerCase().includes('hash') || 
                         key === 'security_data' || 
                         key === 'token_address';
            
            const isTimestamp = key === 'timestamp';
            const isSpecial = key === 'nonce' || key === 'max_supply';

            if (isHash) {
                return `
                    <div class="hash-field" data-copy="${value}">
                        <strong>${key}:</strong>
                        <span class="hash-value">${shortenHash(value)}</span>
                        <span class="copy-label">(copy)</span>
                    </div>
                `;
            }

            if (isTimestamp) {
                return `
                    <div class="time-field" data-copy="${value}">
                        <strong>${key}:</strong>
                        ${formatDate(value)}
                        <span class="copy-label">(copy timestamp)</span>
                    </div>
                `;
            }

            if (isSpecial) {
                return `<div class="special-field"><strong>${key}:</strong> ${value}</div>`;
            }

            return `<div class="normal-field"><strong>${key}:</strong> ${value}</div>`;
        }).join('');
    }

    function shortenHash(hash) {
        return `${hash.slice(0, 6)}...${hash.slice(-4)}`;
    }

    function formatDate(timestamp) {
        return new Date(timestamp * 1000).toLocaleString();
    }

    // Gelişmiş arama
    searchButton.addEventListener('click', () => {
        const searchTerm = blockInput.value.trim().toLowerCase();
        if (!searchTerm) return;

        const targetElement = hashRegistry.get(searchTerm) || 
                            document.getElementById(searchTerm);

        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
            targetElement.classList.add('glow');
            setTimeout(() => targetElement.classList.remove('glow'), 1500);
        } else {
            showNotification('🔍 Hash not found in blockchain!');
        }
    });

    // Başlangıç
    visualizeBlockchain();
});