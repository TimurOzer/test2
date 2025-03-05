async function loadGenesisBlock() {
    const genesisResponse = await fetch('data/genesis_block.json');
    const genesisBlock = await genesisResponse.json();
    
    const container = document.getElementById('blocks-container');
    container.innerHTML = '';

    // Genesis Block'u ekle
    const genesisElement = document.createElement('div');
    genesisElement.classList.add('block', 'genesis');
    genesisElement.innerHTML = `
        <h2>Genesis Blok</h2>
        <p><strong>Token Adresi:</strong> ${genesisBlock.token_address}</p>
        <p><strong>Max Arz:</strong> ${genesisBlock.max_supply}</p>
        <p><strong>Zaman:</strong> ${new Date(genesisBlock.timestamp * 1000).toLocaleString()}</p>
        <p><strong>Önceki Hash 1:</strong> ${genesisBlock.prev_hash_1}</p>
        <p><strong>Önceki Hash 2:</strong> ${genesisBlock.prev_hash_2}</p>
        <p><strong>Nonce:</strong> ${genesisBlock.nonce}</p>
        <p><strong>Blok Hash:</strong> ${genesisBlock.block_hash}</p>
        <p><strong>Security Hash:</strong> ${genesisBlock.security_hash}</p>
    `;
    container.appendChild(genesisElement);
}
