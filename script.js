document.addEventListener("DOMContentLoaded", async function () {
    const container = document.getElementById("blockchain-container");
    const searchButton = document.getElementById("search-button");
    const blockInput = document.getElementById("block-input");

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
        let displayValue = value;
        const isHash = key.toLowerCase().includes('hash') || 
                      key.toLowerCase().includes('merkleroot') || 
                      key.toLowerCase().includes('signature');

        if (isHash && typeof value === 'string' && value.length > 16) {
            const shortHash = `${value.substring(0, 6)}...${value.substring(value.length - 4)}`;
            return `
                <div class="hash-container" onclick="navigator.clipboard.writeText('${value}')">
                    <strong>${key}:</strong>
                    <span class="hash-short" data-full="${value}">${shortHash}</span>
                    <span class="hash-tooltip">Click to copy!</span>
                </div>
            `;
        }
        
        if (typeof value === 'object') {
            return `<strong>${key}:</strong><pre>${JSON.stringify(value, null, 2)}</pre>`;
        }
        
        return `<strong>${key}:</strong> ${value}`;
    }).join('<br>');
}

    // Search functionality
    searchButton.addEventListener('click', async () => {
        const searchTerm = blockInput.value.trim();
        if (!searchTerm) return;

        // Implement search logic here
        alert('Search functionality coming soon!');
    });

    // Initial load
    visualizeBlockchain();
});