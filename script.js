document.addEventListener("DOMContentLoaded", function() {
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
        const genesis = await fetchJSON("genesis_block.json");
        const alpha1 = await fetchJSON("alpha1.json");
        const security1 = await fetchJSON("security1.json");
        const beta1 = await fetchJSON("beta1.json");

        // Genesis bloğunu oluştur
        if(genesis) {
            const genesisBlock = createBlock("Genesis Block", genesis);
            container.appendChild(genesisBlock);
        }
        // Alpha bloğunu oluştur
        if(alpha1) {
            const alphaBlock = createBlock("Alpha 1 Block", alpha1);
            container.appendChild(alphaBlock);
        }
        // Security bloğunu oluştur
        if(security1) {
            const securityBlock = createBlock("Security 1 Block", security1);
            container.appendChild(securityBlock);
        }
        // Beta bloğunu oluştur
        if(beta1) {
            const betaBlock = createBlock("Beta 1 Block", beta1);
            container.appendChild(betaBlock);
        }
    }

    // Her bir blok için HTML öğelerini oluşturan fonksiyon
    function createBlock(title, data) {
        const block = document.createElement("div");
        block.className = "block";

        const cube = document.createElement("div");
        cube.className = "cube";

        // Küpün 6 yüzü oluşturuluyor
        const faces = ["front", "back", "right", "left", "top", "bottom"];
        faces.forEach(face => {
            const faceDiv = document.createElement("div");
            faceDiv.className = "face " + face;
            // JSON verisini okunabilir formatta gösteriyoruz
            faceDiv.innerHTML = `<strong>${title}</strong><br><pre>${JSON.stringify(data, null, 2)}</pre>`;
            cube.appendChild(faceDiv);
        });

        block.appendChild(cube);
        return block;
    }

    loadBlockchainData();

    // Eğer verilerin anlık güncellenmesini istiyorsanız, belirli aralıklarla tekrar yükleyebilirsiniz.
    // setInterval(loadBlockchainData, 5000); // Her 5 saniyede bir güncelleme
});
