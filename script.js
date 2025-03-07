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

        let lastBetaHash = null;
        let alphaIndex = 1;
        let securityIndex = 1;
        let betaIndex = 1;

        // Blokları dikey olarak çiz
        let currentRow = document.createElement("div");
        currentRow.className = "row";
        container.appendChild(currentRow);

        // Genesis bloğu
        if (blocks["genesis_block"]) {
            const genesisBlock = createBlock("Genesis Block", blocks["genesis_block"]);
            currentRow.appendChild(genesisBlock);
            lastBetaHash = blocks["genesis_block"].block_hash;
        }

        // Alpha ve Security bloklarını sırasıyla ekle
        while (blocks[`alpha${alphaIndex}`] || blocks[`security${securityIndex}`]) {
            let newRow = document.createElement("div");
            newRow.className = "row";
            container.appendChild(newRow);

            if (blocks[`alpha${alphaIndex}`]) {
                newRow.appendChild(createBlock(`Alpha ${alphaIndex}`, blocks[`alpha${alphaIndex}`]));
                alphaIndex++;
            }

            if (blocks[`security${securityIndex}`]) {
                newRow.appendChild(createBlock(`Security ${securityIndex}`, blocks[`security${securityIndex}`]));
                securityIndex++;
            }

            // Beta ekle
            let betaRow = document.createElement("div");
            betaRow.className = "row";
            container.appendChild(betaRow);

            if (blocks[`beta${betaIndex}`]) {
                betaRow.appendChild(createBlock(`Beta ${betaIndex}`, blocks[`beta${betaIndex}`]));
                lastBetaHash = blocks[`beta${betaIndex}`].block_hash;
                betaIndex++;
            }
        }
    }

    function createBlock(title, data) {
        const block = document.createElement("div");
        block.className = "block";

        // Başlık
        const blockHeader = document.createElement("div");
        blockHeader.className = "block-header";
        blockHeader.innerText = title;
        block.appendChild(blockHeader);

        // İçerik
        const blockContent = document.createElement("div");
        blockContent.className = "block-content";
        blockContent.innerHTML = formatBlockContent(data);
        block.appendChild(blockContent);

        return block;
    }

    // JSON içeriğini daha okunabilir hale getir
    function formatBlockContent(data) {
        let content = "";
        
        for (let key in data) {
            if (typeof data[key] === "object") {
                content += `<strong>${key}</strong>:<pre>${JSON.stringify(data[key], null, 2)}</pre><br>`;
            } else {
                content += `<strong>${key}</strong>: ${data[key]}<br>`;
            }
        }
        return content;
    }

    loadBlockchainData();
});
