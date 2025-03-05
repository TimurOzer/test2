async function loadBlocks() {
    const response = await fetch('data/blocks.json');
    const blocks = await response.json();
    
    const container = document.getElementById('blocks-container');
    container.innerHTML = '';

    blocks.forEach(block => {
        const blockElement = document.createElement('div');
        blockElement.classList.add('block');
        blockElement.innerHTML = `
            <h3>Blok #${block.index}</h3>
            <p><strong>Hash:</strong> ${block.hash}</p>
            <p><strong>Security Hash:</strong> ${block.security_hash}</p>
            <p><strong>Önceki Hash:</strong> ${block.previous_hash}</p>
            <p><strong>Zaman:</strong> ${block.timestamp}</p>
            <p><strong>İşlemler:</strong> ${block.transactions.length} adet</p>
        `;
        container.appendChild(blockElement);
    });
}
