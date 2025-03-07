document.addEventListener("DOMContentLoaded", async function() {
    const container = document.getElementById("blockchain-container");

    async function fetchJSON(file) {
        try {
            const response = await fetch(`data/${file}`);
            return await response.json();
        } catch (error) {
            console.error(`Error fetching ${file}:`, error);
            return null;
        }
    }

    async function loadBlockchainData() {
        container.innerHTML = "";

        // JSON dosyalarını oku
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

        // 1️⃣ Genesis bloğu
        let genesisRow = document.createElement("div");
        genesisRow.className = "row";
        container.appendChild(genesisRow);

        if (blocks["genesis_block"]) {
            let genesisBlock = createBlock("Genesis Block", blocks["genesis_block"]);
            genesisRow.appendChild(genesisBlock);
            lastBetaHash = blocks["genesis_block"].block_hash;
        }

        // 2️⃣ Zinciri oluştur
        while (blocks[`alpha${alphaIndex}`] || blocks[`security${securityIndex}`]) {
            let alphaRow = document.createElement("div");
            alphaRow.className = "row";
            container.appendChild(alphaRow);

            if (blocks[`alpha${alphaIndex}`]) {
                alphaRow.appendChild(createBlock(`Alpha ${alphaIndex}`, blocks[`alpha${alphaIndex}`]));
                alphaIndex++;
            }

            if (blocks[`security${securityIndex}`]) {
                alphaRow.appendChild(createBlock(`Security ${securityIndex}`, blocks[`security${securityIndex}`]));
                securityIndex++;
            }

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
        block.innerHTML = `<strong>${title}</strong><br><pre>${JSON.stringify(data, null, 2)}</pre>`;
        return block;
    }

    loadBlockchainData();
});
