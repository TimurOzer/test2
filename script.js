// Sample Blockchain data (This will be fetched in a real app)
const blockData = {
    "genesis_block": {
        "hash": "0x1234567890abcdef",
        "timestamp": "2025-03-07T12:34:56Z",
        "transactions": 12,
        "miner": "0xabc123",
        "blockReward": 5
    },
    "alpha1": {
        "hash": "0xabcdef1234567890",
        "timestamp": "2025-03-07T13:00:00Z",
        "transactions": 8,
        "miner": "0xdef456",
        "blockReward": 5
    },
    // Add more blocks as needed
};

// Function to display block data
function displayBlockDetails(block) {
    const blockDetailsElement = document.getElementById("block-details");
    
    if (block) {
        blockDetailsElement.innerHTML = `
            <h2>Block Details: ${block.hash}</h2>
            <p><strong>Timestamp:</strong> ${block.timestamp}</p>
            <p><strong>Transactions:</strong> ${block.transactions}</p>
            <p><strong>Miner:</strong> ${block.miner}</p>
            <p><strong>Block Reward:</strong> ${block.blockReward} ETH</p>
        `;
    } else {
        blockDetailsElement.innerHTML = `<p>Block not found. Please check the hash/address and try again.</p>`;
    }
}

// Handle search button click
document.getElementById("search-button").addEventListener("click", () => {
    const blockHash = document.getElementById("block-input").value.toLowerCase();
    
    // In a real app, you would fetch block data from a blockchain API based on the entered hash
    if (blockData[blockHash]) {
        displayBlockDetails(blockData[blockHash]);
    } else {
        displayBlockDetails(null);
    }
});
