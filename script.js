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
        const specialFields = {
            hash: ['hash', 'merkleroot', 'signature', 'token_address', 'security_data'],
            timestamp: ['timestamp', 'time', 'date'],
            code: ['address', 'id', 'nonce']
        };

        // Hash Benzeri Alanlar
        if (specialFields.hash.some(f => key.toLowerCase().includes(f))) {
            const formattedValue = typeof value === 'string' ? value : JSON.stringify(value);
            return createSpecialField(key, formattedValue, 'hash');
        }

        // Timestamp Alanları
        if (specialFields.timestamp.includes(key.toLowerCase())) {
            return createTimestampField(value);
        }

        // Kod Benzeri Alanlar
        if (specialFields.code.some(f => key.toLowerCase().includes(f))) {
            return `<div class="code-snippet">${key}: <code>${value}</code></div>`;
        }

        // Obje ve Diğer Alanlar
        if (typeof value === 'object') {
            return `<div class="object-field"><strong>${key}:</strong><pre>${JSON.stringify(value, null, 2)}</pre></div>`;
        }

        return `<div class="regular-field"><strong>${key}:</strong> ${value}</div>`;
    }).join('');
}

function createSpecialField(key, value, type) {
    const isHex = /^[0-9a-fx]+$/i.test(value);
    const shortValue = isHex ? `${value.substring(0, 6)}...${value.slice(-4)}` : value.substring(0, 12) + '...';
    
    const specialField = document.createElement('div');
    specialField.className = `special-field ${type}`;
    specialField.dataset.full = value;

    // Create field header and content
    const fieldHeader = document.createElement('div');
    fieldHeader.className = 'field-header';
    
    const fieldKey = document.createElement('span');
    fieldKey.className = 'field-key';
    fieldKey.textContent = `${key}:`;
    
    const copyIndicator = document.createElement('span');
    copyIndicator.className = 'copy-indicator';
    copyIndicator.textContent = '📋';
    
    fieldHeader.appendChild(fieldKey);
    fieldHeader.appendChild(copyIndicator);
    
    const fieldValue = document.createElement('div');
    fieldValue.className = 'field-value';
    fieldValue.textContent = shortValue;

    // Full value overlay
    const fullValueOverlay = document.createElement('div');
    fullValueOverlay.className = 'full-value-overlay';
    
    const fullValueContent = document.createElement('div');
    fullValueContent.className = 'full-value-content';
    
    const fullValueText = document.createElement('span');
    fullValueText.textContent = value;
    
    const copyButton = document.createElement('button');
    copyButton.className = 'copy-button';
    copyButton.dataset.value = value;
    copyButton.textContent = 'Copy Full Value';

    fullValueContent.appendChild(fullValueText);
    fullValueContent.appendChild(copyButton);
    fullValueOverlay.appendChild(fullValueContent);

    specialField.appendChild(fieldHeader);
    specialField.appendChild(fieldValue);
    specialField.appendChild(fullValueOverlay);

    // Add event listener for the special field
    specialField.addEventListener('click', handleSpecialClick);

    return specialField;
}

function createTimestampField(timestamp) {
    const date = new Date(timestamp * 1000);
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        fractionalSecondDigits: 3
    };
    
    return `
        <div class="timestamp-field" data-raw="${timestamp}">
            <div class="human-time">${date.toLocaleString('en-US', options)}</div>
            <div class="raw-time">Unix: ${timestamp}</div>
        </div>
    `;
}

// Yeni click handler
function handleSpecialClick(event) {
    const field = event.currentTarget;
    const fullValue = field.dataset.full;
    
    navigator.clipboard.writeText(fullValue).then(() => {
        showCopyNotification('✓ Value copied to clipboard!');
    }).catch(err => {
        showCopyNotification('⚠️ Failed to copy!');
    });
}

function showCopyNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'copy-notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 2000);
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