// ── SCROLL LOCK HELPERS ──────────────────────────────────
// Bloqueia o scroll compensando a largura da scrollbar,
// para evitar que o layout se desloque horizontalmente.
function lockScroll() {
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    document.body.style.paddingRight = scrollbarWidth + 'px';
    document.body.classList.add("no-scroll");
}

function unlockScroll() {
    document.body.classList.remove("no-scroll");
    document.body.style.paddingRight = '';
}

// SEARCH BOX (Pesquisa dinâmica)
const searchIcon = document.getElementById("searchIcon");
const searchBox = document.getElementById("searchBox");
const searchInput = document.getElementById("searchInput");
const results = document.getElementById("results");

// Lista de produtos do site
const products = [
    // -------------------- SMARTPHONES --------------------
    // Apple
    { name: "Apple iPhone Air", link: "/smartphones/apple/iphone-air/" },
    { name: "Apple iPhone 17 Pro", link: "/smartphones/apple/iphone-17-pro/" },
    { name: "Apple iPhone 17", link: "/smartphones/apple/iphone-17/" },
    { name: "Apple iPhone 16", link: "/smartphones/apple/iphone-16/" },
    { name: "Apple iPhone 16e", link: "/smartphones/apple/iphone-16e/" },

    // Google
    { name: "Google Pixel 10 Pro XL", link: "/smartphones/google/pixel-10-pro-xl/" },
    { name: "Google Pixel 10 Pro", link: "/smartphones/google/pixel-10-pro/" },
    { name: "Google Pixel 10", link: "/smartphones/google/pixel-10/" },

    // Samsung
    { name: "Samsung Galaxy S25 Ultra", link: "/smartphones/samsung/s25-ultra/" },
    { name: "Samsung Galaxy S25 Edge", link: "/smartphones/samsung/s25-edge/" },
    { name: "Samsung Galaxy S25", link: "/smartphones/samsung/s25/" },
    { name: "Samsung Galaxy Z Fold 7", link: "/smartphones/samsung/z-fold-7/" },
    { name: "Samsung Galaxy Z Flip 7", link: "/smartphones/samsung/z-flip-7/" },

    // Xiaomi
    { name: "Xiaomi 15 Ultra", link: "/smartphones/xiaomi/15-ultra/" },
    { name: "Xiaomi 15", link: "/smartphones/xiaomi/15/" },
    { name: "Xiaomi 15T Pro", link: "/smartphones/xiaomi/15t-pro/" },
    { name: "Xiaomi 15T", link: "/smartphones/xiaomi/15t/" },
    { name: "Xiaomi Redmi Note 15 Pro Plus", link: "/smartphones/xiaomi/redmi-note-15-pro-plus/" },

    // -------------------- COMPUTADORES --------------------
    // AMD
    { name: "Gaming TrendingPC AMD Ryzen 9 5900x", link: "/computadores/amd/ryzen9-5900x/" },
    { name: "Gaming TrendingPC AMD Ryzen 7 8700f", link: "/computadores/amd/ryzen7-8700f/" },
    { name: "Gaming TrendingPC AMD Ryzen 7 5800x", link: "/computadores/amd/ryzen7-5800x/" },

    // Intel
    { name: "Daitona PC Intel Core I5-14400f", link: "/computadores/intel/core-i5-14400f/" },
    { name: "Gaming PC RACING Intel Core I5-12400f", link: "/computadores/intel/core-i5-12400f/" },

    // -------------------- PORTÁTEIS --------------------
    // Apple
    { name: "Apple Macbook Pro", link: "/portateis/apple/macbook-pro/" },
    { name: "Apple Macbook Air", link: "/portateis/apple/macbook-air/" },

    // Lenovo
    { name: "Lenovo IdeaPad Slim 5", link: "/portateis/lenovo/ideapad-slim5/" },

    // Samsung
    { name: "Samsung Galaxy Book 5 Pro 360", link: "/portateis/samsung/book5-pro-360/" },
    { name: "Samsung Galaxy Book 4", link: "/portateis/samsung/book4/" },
    { name: "Samsung Galaxy Book 3 Pro", link: "/portateis/samsung/book3-pro/" },

    // -------------------- TABLETS --------------------
    // Apple
    { name: "Apple iPad Pro", link: "/tablets/apple/ipad-pro/" },
    { name: "Apple iPad Air", link: "/tablets/apple/ipad-air/" },
    { name: "Apple iPad", link: "/tablets/apple/ipad/" },

    // Samsung
    { name: "Samsung Galaxy Tab S10 Plus", link: "/tablets/samsung/tab-s10-plus/" },
    { name: "Samsung Galaxy Tab S10 Fe", link: "/tablets/samsung/tab-s10-fe/" },

    // Xiaomi
    { name: "Xiaomi Redmi Pad 2", link: "/tablets/xiaomi/redmi-pad2/" },

    // -------------------- CONSOLAS --------------------
    // Nintendo
    { name: "Nintendo Switch 2", link: "/consolas/nintendo/switch-2/" },
    { name: "Nintendo Switch", link: "/consolas/nintendo/switch/" },

    // Sony
    { name: "PlayStation 5 Pro", link: "/consolas/sony/ps5-pro/" },
    { name: "PlayStation 5", link: "/consolas/sony/ps5/" },

    // Xbox
    { name: "Xbox Series X", link: "/consolas/xbox/series-x/" },
    { name: "Xbox Series S", link: "/consolas/xbox/series-s/" },
];

// Abrir / Fechar caixa de pesquisa
searchIcon.addEventListener("click", () => {

    // Alterna classe active
    searchBox.classList.toggle("active");

    // Se abriu → bloqueia scroll
    if (searchBox.classList.contains("active")) {
        lockScroll();

        setTimeout(() => {
            searchInput.focus();
        }, 200);

    } else {
        // Se fechou → libera scroll
        unlockScroll();
    }
});


// Pesquisa dinâmica ao digitar
searchInput.addEventListener("input", () => {

    const value = searchInput.value.toLowerCase();
    results.innerHTML = "";

    // Se estiver vazio, não mostra nada
    if (value.trim() === "") return;

    // Filtra produtos pelo texto digitado
    const filteredProducts = products.filter(product =>
        product.name.toLowerCase().includes(value)
  );

    // Caso não encontre nada
    if (filteredProducts.length === 0) {
        results.innerHTML = "<div>Nenhum produto encontrado.</div>";
        return;
    }

    // Criar lista de resultados
    filteredProducts.forEach(product => {

        const div = document.createElement("div");
        div.textContent = product.name;

        // Clique → redireciona para a página do produto
        div.addEventListener("click", () => {
            window.location.href = product.link;
        });

        results.appendChild(div);
    });
});

// Fechar pesquisa ao clicar fora
document.addEventListener("click", (e) => {

    if (!searchBox.contains(e.target) && !searchIcon.contains(e.target)) {
        searchBox.classList.remove("active");

        // Libera scroll novamente
        unlockScroll();
    }
});

// Fechar com tecla ESC
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        searchBox.classList.remove("active");
        unlockScroll();
    }
});