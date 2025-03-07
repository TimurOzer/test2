document.addEventListener("DOMContentLoaded", function () {
    // JSON dosyasını çekecek fonksiyon
    async function fetchBlockchainData() {
        try {
            // Burada JSON verisini bir dosyadan alıyoruz. Örneğin, "data/genesis_block.json"
            const response = await fetch('data/blockchain_data.json'); // JSON dosyasının yolu
            const data = await response.json(); // JSON verisini alıyoruz
            
            // Blockchain verileri geldiğinde, onları ekrana yazdırıyoruz
            renderBlockchainData(data);
        } catch (error) {
            console.error('Veri çekilirken bir hata oluştu:', error);
        }
    }

    // Veriyi ekranda render etme fonksiyonu
    function renderBlockchainData(data) {
        const blockchainContainer = document.getElementById('blockchain-container');
        
        data.forEach(block => {
            const blockElement = document.createElement('div');
            blockElement.classList.add('block');

            const blockHeader = document.createElement('div');
            blockHeader.classList.add('block-header');
            blockHeader.textContent = block.title;

            const blockContent = document.createElement('div');
            blockContent.classList.add('block-content');
            blockContent.innerHTML = `<pre>${JSON.stringify(block.content, null, 4)}</pre>`;

            blockElement.appendChild(blockHeader);
            blockElement.appendChild(blockContent);

            blockchainContainer.appendChild(blockElement);
        });
    }

    // Blockchain verilerini çekmeye başlıyoruz
    fetchBlockchainData();
});
