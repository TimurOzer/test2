document.addEventListener("DOMContentLoaded", async function() {
    const container = document.getElementById("blockchain-container");

    // JSON dosyalarını çekmek için yardımcı fonksiyon
    async function fetchJSON(file) {
        try {
            const response = await fetch(`data/${file}`);
            return await response.json();
        } catch (error) {
            console.error(`Error fetching ${file}:`, error);
            return null;
        }
    }

    // Blockchain verilerini yükle ve görselleştir
    async function loadBlockchainData() {
        container.innerHTML = ""; // Önceki verileri temizle

        // Tüm blokları al
        const files = ["genesis_block.json", "alpha1.json", "security1.json", "beta1.json", "alpha2.json", "security2.json", "beta2.json"];
        let blocks = {};

        for (let file of files) {
            let data = await fetchJSON(file);
            if (data) {
                blocks[file.replace(".json", "")] = data;
            }
        }

        // Blokları sırayla çiz
        let currentRow = document.createElement("div");
        currentRow.className = "row";
        container.appendChild(currentRow);

        // Genesis bloğunu oluştur
        if (blocks["genesis_block"]) {
            const genesisBlock = createBlock("Genesis Block", blocks["genesis_block"]);
            currentRow.appendChild(genesisBlock);
        }

        // Alpha ve Security'leri sırayla ekle
        let currentAlpha = 1;
        let currentSecurity = 1;
        let currentBeta = 1;

        while (blocks[`alpha${currentAlpha}`] || blocks[`security${currentSecurity}`]) {
            let newRow = document.createElement("div");
            newRow.className = "row";
            container.appendChild(newRow);

            if (blocks[`alpha${currentAlpha}`]) {
                newRow.appendChild(createBlock(`Alpha ${currentAlpha}`, blocks[`alpha${currentAlpha}`]));
                currentAlpha++;
            }

            if (blocks[`security${currentSecurity}`]) {
                newRow.appendChild(createBlock(`Security ${currentSecurity}`, blocks[`security${currentSecurity}`]));
                currentSecurity++;
            }

            // Beta ekle
            let betaRow = document.createElement("div");
            betaRow.className = "row";
            container.appendChild(betaRow);

            if (blocks[`beta${currentBeta}`]) {
                betaRow.appendChild(createBlock(`Beta ${currentBeta}`, blocks[`beta${currentBeta}`]));
                currentBeta++;
            }
        }
    }

    // Blokları oluşturan fonksiyon
    function createBlock(title, data) {
        const block = document.createElement("div");
        block.className = "block";
        block.innerHTML = `<strong>${title}</strong><br><pre>${JSON.stringify(data, null, 2)}</pre>`;
        return block;
    }

    loadBlockchainData();

    // Güncellemeyi otomatik yapmak için:
    // setInterval(loadBlockchainData, 5000);
});
