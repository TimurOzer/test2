async function loadBlocks() {
    const genesisResponse = await fetch('data/genesis_block.json');
    const blocksResponse = await fetch('data/blocks.json');

    const genesisBlock = await genesisResponse.json();
    const blocks = await blocksResponse.json();
    
    const container = document.getElementById('blocks-container');
    container.innerHTML = '';

    // Genesis Block'u ekle
    const genesisElement = document.createElement('div');
    genesisElement.classList.add('block', 'genesis');
    genesisElement.innerHTML = `
        <h2>Genesis Blok</h2>
        <p><strong>Hash:</strong> ${genesisBlock.hash}</p>
        <p><strong>Security Hash:</strong> ${genesisBlock.security_hash}</p>
        <p><strong>Zaman:</strong> ${genesisBlock.timestamp}</p>
        <p><strong>Adres:</strong> ${genesisBlock.address}</p>
    `;
    container.appendChild(genesisElement);

    // Normal blokları ekle
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
