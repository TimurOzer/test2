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
  document.getElementById('tx-type').textContent = txData.transaction_type || 'Transfer'; // İşlem türü

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
		const data = await response.json();
		return {
		  ...data,
		  fee: data.fee || "0", // Fee bilgisi yoksa varsayılan değer
		  status: data.status || "Confirmed", // Status bilgisi yoksa varsayılan değer
		  transaction_type: data.transaction_type || "Transfer", // İşlem türü yoksa varsayılan değer
		  metadata: data.metadata || {} // Metadata yoksa boş bir obje
		};
	  } catch (error) {
		console.error(`Error fetching block data:`, error);
		return null;
	  }
	}

async function visualizeBlockchain() {
    container.innerHTML = '';

    // Genesis bloğunu çek
    const genesisBlock = await fetchBlockData('genesis_block.json');
    if (genesisBlock && Object.keys(genesisBlock).length > 0) {
        createBlockRow([genesisBlock], 'genesis-row');
    } else {
        console.error('Genesis block not found or invalid.');
    }

    let i = 1;
    while (true) {
        try {
            // Alpha, Security ve Beta bloklarını aynı anda çek
            const [alphaBlock, securityBlock, betaBlock] = await Promise.all([
                fetchBlockData(`alpha${i}.json`),
                fetchBlockData(`security${i}.json`),
                fetchBlockData(`beta${i}.json`)
            ]);

            // Eğer bloklar boş değilse görüntüle
            if (alphaBlock && Object.keys(alphaBlock).length > 0) {
                createBlockRow([alphaBlock], `alpha-${i}`);
            }
            if (securityBlock && Object.keys(securityBlock).length > 0) {
                createBlockRow([securityBlock], `security-${i}`);
            }
            if (betaBlock && Object.keys(betaBlock).length > 0) {
                createBlockRow([betaBlock], `beta-${i}`);
            }

            // Eğer tüm bloklar boşsa döngüyü sonlandır
            if (!alphaBlock && !securityBlock && !betaBlock) {
                console.log(`Blok seti ${i} tamamen boş. Döngü sonlandırılıyor.`);
                break;
            }

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

		console.log('Created block element:', block); // Blok elementini konsola yazdır
		return block;
	}

	function formatContent(data) {
		return Object.entries(data).map(([key, value]) => {
			// Eğer değer boşsa veya null ise, "N/A" olarak göster
			if (value === null || value === "" || (typeof value === "object" && Object.keys(value).length === 0)) {
				value = "N/A";
			}

			// Eğer değer bir obje ise, JSON formatında göster
			if (typeof value === "object" && value !== null) {
				value = JSON.stringify(value, null, 2);
			}

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
								fee: data.fee || 0, // Fee bilgisi yoksa varsayılan değer
								timestamp: data.timestamp,
								status: data.status || 'Confirmed' // Varsayılan durum
							})}'>View</button>
						</div>
					</div>
				`;
			}

			// Metadata alanını özel bir şekilde göster
			if (key === 'metadata') {
				return `
					<div class="metadata-container">
						<strong>Metadata:</strong>
						<div class="metadata-content">
							${Object.entries(value).map(([metaKey, metaValue]) => `
								<div class="metadata-field">
									<strong>${metaKey}:</strong> ${metaValue}
								</div>
							`).join('')}
						</div>
					</div>
				`;
			}

			// Akıllı kontrat bilgilerini göster
			if (key === 'smart_contract') {
				return `
					<div class="smart-contract-container">
						<strong>Smart Contract:</strong>
						<div class="smart-contract-content">
							${Object.entries(value).map(([scKey, scValue]) => `
								<div class="smart-contract-field">
									<strong>${scKey}:</strong> ${scValue}
								</div>
							`).join('')}
						</div>
					</div>
				`;
			}

			// Özel alanlar için dikdörtgen bölümler oluştur
			const specialFields = {
				fee: ['fee'],
				network: ['network'],
				block_size: ['block_size'],
				block_height: ['block_height'],
				tags: ['tags'],
				priority: ['priority'],
				code: ['address', 'id', 'nonce', 'max_supply', 'recipient', 'amount', 'tag', 'airdrop', 'mining_reserve']
			};
			// Eğer alan özel bir alansa, özelleştirilmiş dikdörtgen bölüm oluştur
			for (const [fieldType, fields] of Object.entries(specialFields)) {
				if (fields.includes(key)) {
					return `
						<div class="${fieldType}-field">
							<strong>${key}:</strong>
							<span>${value}</span>
						</div>
					`;
				}
			}
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

// Token ekonomisi verilerini güncelleme
async function updateTokenEconomics() {
  try {
    // Toplam arzı güncelle
    const totalSupply = await fetchTotalSupply();
    document.getElementById('total-supply').textContent = totalSupply;

    // Dolaşımdaki arzı güncelle
    const circulatingSupply = await fetchCirculatingSupply();
    document.getElementById('circulating-supply').textContent = circulatingSupply;

    // Stake edilen tokenleri güncelle
    const stakedTokens = await fetchStakedTokens();
    document.getElementById('staked-tokens').textContent = stakedTokens;

    // Token fiyatını güncelle
    const tokenPrice = await fetchTokenPrice();
    document.getElementById('token-price').textContent = `$${tokenPrice}`;
  } catch (error) {
    console.error('Token ekonomisi verileri güncellenirken hata:', error);
  }
}

// Örnek API çağrıları (Bu fonksiyonları kendi backend'inize göre uyarlayın)
async function fetchTotalSupply() {
  const response = await fetch('/api/token/total-supply');
  const data = await response.json();
  return data.totalSupply;
}

async function fetchCirculatingSupply() {
  const response = await fetch('/api/token/circulating-supply');
  const data = await response.json();
  return data.circulatingSupply;
}

async function fetchStakedTokens() {
  const response = await fetch('/api/token/staked-tokens');
  const data = await response.json();
  return data.stakedTokens;
}

async function fetchTokenPrice() {
  const response = await fetch('/api/token/price');
  const data = await response.json();
  return data.price;
}

// Sayfa yüklendiğinde ve belirli aralıklarla token ekonomisi verilerini güncelle
document.addEventListener('DOMContentLoaded', () => {
  updateTokenEconomics();
  setInterval(updateTokenEconomics, 30000); // Her 30 saniyede bir güncelle
});

// Quiz butonlarına tıklama olayı
document.addEventListener('click', (event) => {
  const quizButton = event.target.closest('.quiz-button');
  if (quizButton) {
    const quizId = quizButton.dataset.quiz;
    startQuiz(quizId);
  }
});

// Quiz başlatma fonksiyonu
function startQuiz(quizId) {
  const questions = {
    1: [
      {
        question: "What is a blockchain?",
        options: ["A type of cryptocurrency", "A decentralized digital ledger", "A centralized database"],
        answer: 1
      },
      {
        question: "What is the main benefit of blockchain?",
        options: ["Speed", "Transparency", "Centralization"],
        answer: 1
      }
    ],
    2: [
      {
        question: "What consensus mechanism does Baklava Blockchain use?",
        options: ["Proof of Work", "Proof of Stake", "Proof of Baklava"],
        answer: 2
      }
    ],
    3: [
      {
        question: "What is a token?",
        options: ["A digital asset", "A physical coin", "A type of blockchain"],
        answer: 0
      }
    ]
  };

  const quizQuestions = questions[quizId];
  if (quizQuestions) {
    let score = 0;
    quizQuestions.forEach((q, index) => {
      const userAnswer = prompt(`${index + 1}. ${q.question}\n\nOptions:\n${q.options.join('\n')}`);
      if (userAnswer == q.answer) {
        score++;
      }
    });
    alert(`You scored ${score} out of ${quizQuestions.length}!`);
  } else {
    alert('Quiz not found!');
  }
}

// Paylaşım butonlarına tıklama olayı
document.addEventListener('click', (event) => {
  const shareButton = event.target.closest('.share-button');
  if (shareButton) {
    const url = shareButton.dataset.url;
    const text = shareButton.dataset.text || 'Check out this on Baklava Blockchain!';

    if (shareButton.classList.contains('twitter')) {
      shareOnTwitter(url, text);
    } else if (shareButton.classList.contains('facebook')) {
      shareOnFacebook(url);
    } else if (shareButton.classList.contains('linkedin')) {
      shareOnLinkedIn(url);
    }
  }
});

// Twitter'da paylaşma fonksiyonu
function shareOnTwitter(url, text) {
  const twitterUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;
  window.open(twitterUrl, '_blank');
}

// Facebook'ta paylaşma fonksiyonu
function shareOnFacebook(url) {
  const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
  window.open(facebookUrl, '_blank');
}

// LinkedIn'de paylaşma fonksiyonu
function shareOnLinkedIn(url) {
  const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
  window.open(linkedinUrl, '_blank');
}

function updateShareButtons(blockHash) {
  const shareUrl = `https://baklava-blockchain.com/block/${blockHash}`;
  const shareButtons = document.querySelectorAll('.share-button');
  shareButtons.forEach(button => {
    button.dataset.url = shareUrl;
  });
}

// Tema değiştirme butonu
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');

// Kullanıcının tercih ettiği temayı kontrol et
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
  document.body.classList.add('dark-mode');
  themeIcon.src = 'image/dark-mode-icon.png';
}

// Tema değiştirme işlevselliği
themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark-mode');
  const isDarkMode = document.body.classList.contains('dark-mode');
  localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
  themeIcon.src = isDarkMode ? 'image/dark-mode-icon.png' : 'image/light-mode-icon.png';
});

// Blok karşılaştırma işlevselliği
const block1Select = document.getElementById('block1-select');
const block2Select = document.getElementById('block2-select');
const compareButton = document.getElementById('compare-button');
const block1Details = document.getElementById('block1-details');
const block2Details = document.getElementById('block2-details');

// Blok seçeneklerini doldurma
function populateBlockSelects(blocks) {
  blocks.forEach(block => {
    const option = document.createElement('option');
    option.value = block.block_hash;
    option.textContent = `Block ${block.block_hash.slice(0, 6)}...${block.block_hash.slice(-4)}`;
    block1Select.appendChild(option.cloneNode(true));
    block2Select.appendChild(option.cloneNode(true));
  });
}

// Blok detaylarını gösterme
function showBlockDetails(block, container) {
  container.innerHTML = `
    <h3>Block Details</h3>
    <p><strong>Hash:</strong> ${block.block_hash}</p>
    <p><strong>Previous Hash:</strong> ${block.previous_hash}</p>
    <p><strong>Timestamp:</strong> ${new Date(block.timestamp * 1000).toLocaleString()}</p>
    <p><strong>Nonce:</strong> ${block.nonce}</p>
    <p><strong>Transactions:</strong> ${block.transactions ? block.transactions.length : 0}</p>
  `;
}

// Karşılaştırma butonuna tıklama olayı
compareButton.addEventListener('click', async () => {
  const block1Hash = block1Select.value;
  const block2Hash = block2Select.value;

  if (!block1Hash || !block2Hash) {
    alert('Please select both blocks to compare.');
    return;
  }

  const block1 = await fetchBlockDataByHash(block1Hash);
  const block2 = await fetchBlockDataByHash(block2Hash);

  if (block1 && block2) {
    showBlockDetails(block1, block1Details);
    showBlockDetails(block2, block2Details);
  } else {
    alert('Failed to fetch block details.');
  }
});

// Blok verilerini hash'e göre çekme
async function fetchBlockDataByHash(blockHash) {
  try {
    const response = await fetch(`/api/blocks/${blockHash}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Error fetching block data:`, error);
    return null;
  }
}

// Sayfa yüklendiğinde blok seçeneklerini doldur
document.addEventListener('DOMContentLoaded', async () => {
  const blocks = await fetchAllBlocks();
  populateBlockSelects(blocks);
});

// Tüm blokları çekme
async function fetchAllBlocks() {
  try {
    const response = await fetch('/api/blocks');
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Error fetching all blocks:`, error);
    return [];
  }
}

// Token swap işlevselliği
const fromTokenSelect = document.getElementById('from-token');
const toTokenSelect = document.getElementById('to-token');
const fromAmountInput = document.getElementById('from-amount');
const toAmountInput = document.getElementById('to-amount');
const swapButton = document.getElementById('swap-button');
const swapResult = document.getElementById('swap-result');

// Token swap oranları
const exchangeRates = {
  BKV: { FILO: 10, ANTEP: 5 },
  FILO: { BKV: 0.1, ANTEP: 0.5 },
  ANTEP: { BKV: 0.2, FILO: 2 },
};

// Swap işlemini simüle etme
function simulateSwap(fromToken, toToken, amount) {
  const rate = exchangeRates[fromToken][toToken];
  if (!rate) {
    swapResult.textContent = 'Invalid token pair.';
    return;
  }
  const result = amount * rate;
  toAmountInput.value = result.toFixed(2);
  swapResult.textContent = `You will receive ${result.toFixed(2)} ${toToken} for ${amount} ${fromToken}.`;
}

// Swap butonuna tıklama olayı
swapButton.addEventListener('click', () => {
  const fromToken = fromTokenSelect.value;
  const toToken = toTokenSelect.value;
  const amount = parseFloat(fromAmountInput.value);

  if (!amount || amount <= 0) {
    swapResult.textContent = 'Please enter a valid amount.';
    return;
  }

  simulateSwap(fromToken, toToken, amount);
});

// From token değiştiğinde to token'ı güncelleme
fromTokenSelect.addEventListener('change', () => {
  toTokenSelect.innerHTML = '';
  const tokens = ['BKV', 'FILO', 'ANTEP'];
  tokens.forEach(token => {
    if (token !== fromTokenSelect.value) {
      const option = document.createElement('option');
      option.value = token;
      option.textContent = token;
      toTokenSelect.appendChild(option);
    }
  });
});

// Sayfa yüklendiğinde to token'ı başlangıçta güncelle
document.addEventListener('DOMContentLoaded', () => {
  fromTokenSelect.dispatchEvent(new Event('change'));
});

// Yorum işlevselliği
const commentInput = document.getElementById('comment-input');
const submitCommentButton = document.getElementById('submit-comment');
const commentsList = document.getElementById('comments-list');

// Yorum gönderme fonksiyonu
function addComment(commentText) {
  const comment = document.createElement('div');
  comment.className = 'comment';
  comment.innerHTML = `
    <p><span class="author">Anonymous</span>: ${commentText}</p>
  `;
  commentsList.appendChild(comment);
}

// Yorum gönderme butonuna tıklama olayı
submitCommentButton.addEventListener('click', () => {
  const commentText = commentInput.value.trim();
  if (commentText) {
    addComment(commentText);
    commentInput.value = ''; // Yorum alanını temizle
  } else {
    alert('Please write a comment before submitting.');
  }
});

// Yorum alanında Enter tuşuna basıldığında yorum gönderme
commentInput.addEventListener('keypress', (event) => {
  if (event.key === 'Enter') {
    submitCommentButton.click();
  }
});

// Yorumları backend'e kaydetme
async function saveComment(blockHash, commentText) {
  try {
    const response = await fetch('/api/comments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ blockHash, commentText }),
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error saving comment:', error);
    return null;
  }
}

// Yorumları backend'den çekme
async function loadComments(blockHash) {
  try {
    const response = await fetch(`/api/comments/${blockHash}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error loading comments:', error);
    return [];
  }
}

// Yorum gönderme butonuna tıklama olayı (Backend entegrasyonu ile)
submitCommentButton.addEventListener('click', async () => {
  const commentText = commentInput.value.trim();
  if (commentText) {
    const blockHash = currentBlockHash; // Mevcut blok hash'i
    const savedComment = await saveComment(blockHash, commentText);
    if (savedComment) {
      addComment(savedComment.commentText);
      commentInput.value = ''; // Yorum alanını temizle
    }
  } else {
    alert('Please write a comment before submitting.');
  }
});

// Sayfa yüklendiğinde yorumları yükle
document.addEventListener('DOMContentLoaded', async () => {
  const blockHash = currentBlockHash; // Mevcut blok hash'i
  const comments = await loadComments(blockHash);
  comments.forEach(comment => addComment(comment.commentText));
});

// Airdrop simülatörü işlevselliği
const airdropTokenSelect = document.getElementById('airdrop-token');
const airdropAmountInput = document.getElementById('airdrop-amount');
const airdropUsersInput = document.getElementById('airdrop-users');
const simulateAirdropButton = document.getElementById('simulate-airdrop');
const airdropResult = document.getElementById('airdrop-result');

// Airdrop simülasyonu fonksiyonu
function simulateAirdrop(token, amountPerUser, numberOfUsers) {
  const totalAmount = amountPerUser * numberOfUsers;
  airdropResult.textContent = `Airdropping ${totalAmount} ${token} to ${numberOfUsers} users. Each user receives ${amountPerUser} ${token}.`;
}

// Airdrop simülasyonu butonuna tıklama olayı
simulateAirdropButton.addEventListener('click', () => {
  const token = airdropTokenSelect.value;
  const amountPerUser = parseFloat(airdropAmountInput.value);
  const numberOfUsers = parseInt(airdropUsersInput.value);

  if (!amountPerUser || amountPerUser <= 0 || !numberOfUsers || numberOfUsers <= 0) {
    airdropResult.textContent = 'Please enter valid amounts and number of users.';
    return;
  }

  simulateAirdrop(token, amountPerUser, numberOfUsers);
});

// Blok sıralama işlevselliği
const sortCriteriaSelect = document.getElementById('sort-criteria');
const sortOrderSelect = document.getElementById('sort-order');
const sortButton = document.getElementById('sort-button');

// Blokları sıralama fonksiyonu
function sortBlocks(blocks, criteria, order) {
  return blocks.sort((a, b) => {
    let valueA, valueB;

    if (criteria === 'timestamp') {
      valueA = a.timestamp;
      valueB = b.timestamp;
    } else if (criteria === 'block_hash') {
      valueA = a.block_hash;
      valueB = b.block_hash;
    } else if (criteria === 'transaction_count') {
      valueA = a.transactions ? a.transactions.length : 0;
      valueB = b.transactions ? b.transactions.length : 0;
    }

    if (order === 'asc') {
      return valueA > valueB ? 1 : -1;
    } else {
      return valueA < valueB ? 1 : -1;
    }
  });
}

// Sıralama butonuna tıklama olayı
sortButton.addEventListener('click', async () => {
  const criteria = sortCriteriaSelect.value;
  const order = sortOrderSelect.value;

  const blocks = await fetchAllBlocks();
  const sortedBlocks = sortBlocks(blocks, criteria, order);

  // Sıralanmış blokları görselleştir
  visualizeBlockchain(sortedBlocks);
});

// Tüm blokları çekme
async function fetchAllBlocks() {
  try {
    const response = await fetch('/api/blocks');
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching all blocks:', error);
    return [];
  }
}

// Akıllı kontrat doğrulama işlevselliği
const contractCodeTextarea = document.getElementById('contract-code');
const verifyContractButton = document.getElementById('verify-contract');
const verificationResult = document.getElementById('verification-result');

// Akıllı kontrat doğrulama fonksiyonu
function verifyContract(contractCode) {
  // Basit bir güvenlik kontrolü örneği
  const vulnerabilities = [];
  if (contractCode.includes('tx.origin')) {
    vulnerabilities.push('Use of tx.origin is not recommended.');
  }
  if (contractCode.includes('block.timestamp')) {
    vulnerabilities.push('Use of block.timestamp can be manipulated.');
  }
  if (contractCode.includes('revert()')) {
    vulnerabilities.push('Unchecked revert() calls can lead to vulnerabilities.');
  }

  if (vulnerabilities.length > 0) {
    return `Potential vulnerabilities found:\n${vulnerabilities.join('\n')}`;
  } else {
    return 'No vulnerabilities found. Your contract looks safe!';
  }
}

// Doğrulama butonuna tıklama olayı
verifyContractButton.addEventListener('click', () => {
  const contractCode = contractCodeTextarea.value.trim();
  if (!contractCode) {
    verificationResult.textContent = 'Please paste your contract code.';
    return;
  }

  const result = verifyContract(contractCode);
  verificationResult.textContent = result;
});

// Gas ücreti tahmini işlevselliği
const transactionTypeSelect = document.getElementById('transaction-type');
const gasLimitInput = document.getElementById('gas-limit');
const estimateGasButton = document.getElementById('estimate-gas');
const gasResult = document.getElementById('gas-result');

// Gas ücreti tahmini fonksiyonu
function estimateGasFee(transactionType, gasLimit) {
  const gasPrices = {
    transfer: 20,
    contract_call: 50,
    token_mint: 100,
  };

  const gasPrice = gasPrices[transactionType] || 0;
  const gasFee = gasPrice * gasLimit;

  return gasFee;
}

// Gas ücreti tahmini butonuna tıklama olayı
estimateGasButton.addEventListener('click', () => {
  const transactionType = transactionTypeSelect.value;
  const gasLimit = parseFloat(gasLimitInput.value);

  if (!gasLimit || gasLimit <= 0) {
    gasResult.textContent = 'Please enter a valid gas limit.';
    return;
  }

  const gasFee = estimateGasFee(transactionType, gasLimit);
  gasResult.textContent = `Estimated Gas Fee: ${gasFee} Gwei`;
});

// Ağ sağlık skoru işlevselliği
const healthScoreValue = document.getElementById('health-score-value');
const performanceScore = document.getElementById('performance-score');
const securityScore = document.getElementById('security-score');
const stabilityScore = document.getElementById('stability-score');

// Ağ sağlık skorunu güncelleme fonksiyonu
async function updateNetworkHealthScore() {
  try {
    const performance = await fetchPerformanceScore();
    const security = await fetchSecurityScore();
    const stability = await fetchStabilityScore();

    const overallScore = Math.round((performance + security + stability) / 3);

    healthScoreValue.textContent = overallScore;
    performanceScore.textContent = performance;
    securityScore.textContent = security;
    stabilityScore.textContent = stability;
  } catch (error) {
    console.error('Error updating network health score:', error);
  }
}

// Performans skorunu çekme (örnek)
async function fetchPerformanceScore() {
  const response = await fetch('/api/performance');
  const data = await response.json();
  return data.score;
}

// Güvenlik skorunu çekme (örnek)
async function fetchSecurityScore() {
  const response = await fetch('/api/security');
  const data = await response.json();
  return data.score;
}

// Stabilite skorunu çekme (örnek)
async function fetchStabilityScore() {
  const response = await fetch('/api/stability');
  const data = await response.json();
  return data.score;
}

// Sayfa yüklendiğinde ve belirli aralıklarla skoru güncelle
document.addEventListener('DOMContentLoaded', () => {
  updateNetworkHealthScore();
  setInterval(updateNetworkHealthScore, 30000); // Her 30 saniyede bir güncelle
});
// Blok ödül takipçisi işlevselliği
const totalRewards = document.getElementById('total-rewards');
const lastReward = document.getElementById('last-reward');
const rewardsTableBody = document.querySelector('#rewards-table tbody');

// Blok ödüllerini güncelleme fonksiyonu
async function updateBlockRewards() {
  try {
    const rewards = await fetchBlockRewards();
    let total = 0;
    let last = 0;

    rewardsTableBody.innerHTML = ''; // Tabloyu temizle

    rewards.forEach(reward => {
      total += reward.amount;
      last = reward.amount;

      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${reward.block_hash.slice(0, 6)}...${reward.block_hash.slice(-4)}</td>
        <td>${reward.amount}</td>
        <td>${new Date(reward.timestamp * 1000).toLocaleString()}</td>
      `;
      rewardsTableBody.appendChild(row);
    });

    totalRewards.textContent = total;
    lastReward.textContent = last;
  } catch (error) {
    console.error('Error updating block rewards:', error);
  }
}

// Blok ödüllerini çekme (örnek)
async function fetchBlockRewards() {
  const response = await fetch('/api/block-rewards');
  const data = await response.json();
  return data.rewards;
}

// Sayfa yüklendiğinde ve belirli aralıklarla ödülleri güncelle
document.addEventListener('DOMContentLoaded', () => {
  updateBlockRewards();
  setInterval(updateBlockRewards, 30000); // Her 30 saniyede bir güncelle
});

// Etkileşimli rehber işlevselliği
const steps = document.querySelectorAll('.step');

steps.forEach(step => {
  const button = document.createElement('button');
  button.textContent = 'Mark as Completed';
  button.className = 'complete-button';
  step.appendChild(button);

  button.addEventListener('click', () => {
    step.style.opacity = '0.6';
    button.textContent = 'Completed ✓';
    button.disabled = true;
  });
});