document.addEventListener("DOMContentLoaded", async function () {
    const container = document.getElementById("blockchain-container");
    const searchButton = document.getElementById("search-button");
    const blockInput = document.getElementById("block-input");
    const hashRegistry = new Map();
	
	// Modal İşlevselliği
	const modal = document.getElementById('transaction-modal');
	const closeModalBtn = document.querySelector('.close-modal');

function openTransactionModal(txData) {
  document.getElementById('tx-from').textContent = txData.sender;
  document.getElementById('tx-to').textContent = txData.recipient;
  document.getElementById('tx-amount').textContent = txData.amount;
  document.getElementById('tx-fee').textContent = txData.fee || 'N/A'; // Fee bilgisi yoksa "N/A" göster
  document.getElementById('tx-timestamp').textContent = new Date(txData.timestamp * 1000).toLocaleString();
  document.getElementById('tx-status').textContent = txData.status || 'Confirmed';

  modal.style.display = 'block';
}

// Modal'ı kapatma fonksiyonu
function closeTransactionModal() {
  modal.style.display = 'none';
}

// Modal'ı kapatma butonu
closeModalBtn.addEventListener('click', closeTransactionModal);

// Dışarı tıklayarak kapatma
window.addEventListener('click', (event) => {
  if (event.target === modal) {
    closeTransactionModal();
  }
});

// View butonuna tıklama olayı
document.addEventListener('click', (event) => {
  const viewButton = event.target.closest('.view-button');
  if (viewButton) {
    const txData = JSON.parse(viewButton.dataset.tx);
    openTransactionModal(txData);
  }
});
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

    let i = 1;
    while (true) {
        try {
            // Alpha, Security ve Beta bloklarını aynı anda çek
            const [alphaBlock, securityBlock, betaBlock] = await Promise.all([
                fetchBlockData(`alpha${i}.json`),
                fetchBlockData(`security${i}.json`),
                fetchBlockData(`beta${i}.json`)
            ]);

            // Eğer bloklar boşsa veya geçersizse döngüyü sonlandır
            if (!alphaBlock || !securityBlock || !betaBlock || 
                Object.keys(alphaBlock).length === 0 || 
                Object.keys(securityBlock).length === 0 || 
                Object.keys(betaBlock).length === 0) {
                console.log(`Blok seti ${i} boş veya geçersiz. Döngü sonlandırılıyor.`);
                break;
            }

            // Blokları görselleştir
            createBlockRow([alphaBlock, securityBlock], `layer-${i}`);
            createBlockRow([betaBlock], `beta-${i}`);

            i++; // Sonraki blok setine geç
        } catch (error) {
            console.error('Blok verisi çekme hatası:', error);
            break; // Hata durumunda döngüyü sonlandır
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
		// Transfer bilgilerini özel bir alanda göster
		if (key === 'sender' || key === 'recipient' || key === 'amount') {
		  return ''; // Bu alanları ayrıca göstermeye gerek yok, çünkü transfer bilgisi olarak göstereceğiz.
		}

		// Transfer bilgilerini özel bir alanda göster
		if (key === 'tag' && value === 'transfer') {
		  return `
			<div class="transfer-container">
			  <strong>Transfer:</strong>
			  <div class="transfer-hover-area">
				<span class="transfer-summary">${data.sender.slice(0, 6)}...${data.sender.slice(-4)} → ${data.recipient.slice(0, 6)}...${data.recipient.slice(-4)}</span>
				<button class="view-button" data-tx='${JSON.stringify({
				  sender: data.sender,
				  recipient: data.recipient,
				  amount: data.amount,
				  fee: 0, // Fee bilgisi yoksa varsayılan değer
				  timestamp: data.timestamp,
				  status: 'Confirmed' // Varsayılan durum
				})}'>View</button>
			  </div>
			</div>
		  `;
		}

		// Diğer alanlar
		const specialFields = {
		  hash: ['hash', 'merkleroot', 'signature', 'token_address', 'security_data', 'block_hash', 'prev_hash_1', 'prev_hash_2', 'recipient', 'sender'],
		  timestamp: ['timestamp', 'time', 'date'],
		  code: ['address', 'id', 'nonce', 'max_supply', 'recipient', 'amount', 'tag', 'airdrop', 'mining_reserve']
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

// Network Stats Güncelleme Fonksiyonu
async function updateNetworkStats() {
  try {
    // Blok sayısını güncelle
    const blockCount = await fetchBlockCount();
    document.getElementById('total-blocks').textContent = blockCount;

    // İşlem sayısını güncelle
    const txCount = await fetchTransactionCount();
    document.getElementById('total-txs').textContent = txCount;

    // Aktif node sayısını güncelle
    const nodeCount = await fetchActiveNodes();
    document.getElementById('active-nodes').textContent = nodeCount;
  } catch (error) {
    console.error('Ağ istatistikleri güncellenirken hata:', error);
  }
}

// Örnek API çağrıları (Bu fonksiyonları kendi backend'inize göre uyarlayın)
async function fetchBlockCount() {
  const response = await fetch('/api/blocks/count');
  const data = await response.json();
  return data.count;
}

async function fetchTransactionCount() {
  const response = await fetch('/api/transactions/count');
  const data = await response.json();
  return data.count;
}

async function fetchActiveNodes() {
  const response = await fetch('/api/nodes/active');
  const data = await response.json();
  return data.count;
}

// Sayfa yüklendiğinde ve belirli aralıklarla istatistikleri güncelle
document.addEventListener('DOMContentLoaded', () => {
  updateNetworkStats();
  setInterval(updateNetworkStats, 30000); // Her 30 saniyede bir güncelle
});

// Harita oluşturma
const map = L.map('network-map').setView([39.9334, 32.8597], 6); // Türkiye merkezli harita

// Harita katmanı ekleme
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Node'ları haritada gösterme
const nodes = [
  { name: 'Node 1', location: [41.0082, 28.9784] }, // İstanbul
  { name: 'Node 2', location: [39.9208, 32.8541] }, // Ankara
  { name: 'Node 3', location: [38.4237, 27.1428] }, // İzmir
  { name: 'Node 4', location: [36.8841, 30.7056] }, // Antalya
  { name: 'Node 5', location: [37.0000, 35.3213] }, // Adana
];
// Node bağlantılarını çizme
const connections = [
  [nodes[0].location, nodes[1].location], // İstanbul -> Ankara
  [nodes[1].location, nodes[2].location], // Ankara -> İzmir
  [nodes[2].location, nodes[3].location], // İzmir -> Antalya
  [nodes[3].location, nodes[4].location], // Antalya -> Adana
];

connections.forEach(connection => {
  L.polyline(connection, { color: '#daa520', weight: 3, dashArray: '5, 10' }).addTo(map);
});

// Özel node ikonu
const nodeIcon = L.icon({
  iconUrl: 'icons/node-icon.png', // Kendi ikonunuzu ekleyin
  iconSize: [30, 30], // İkon boyutu
  iconAnchor: [15, 15], // İkonun merkezi
});

nodes.forEach(node => {
  L.marker(node.location, { icon: nodeIcon })
    .addTo(map)
    .bindPopup(`<b>${node.name}</b><br>${node.location.join(', ')}`);
});