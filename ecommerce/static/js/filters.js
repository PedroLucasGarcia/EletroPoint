/* FILTROS DOS PRODUTOS */

// Selects
const brandSelect = document.getElementById("brand");
const sortSelect = document.getElementById("sort");
const categorySelect = document.getElementById("category");

// Todos os produtos
const allProducts = document.querySelectorAll(".containers");

// Container onde os produtos são exibidos
const container = document.querySelector(".section-container");

// Eventos
brandSelect.addEventListener("change", applyFilters);
sortSelect.addEventListener("change", applyFilters);
categorySelect.addEventListener("change", applyFilters);

/* Aplica filtro e ordenação */
function applyFilters() {

    const brand = brandSelect.value;
    const sort = sortSelect.value;
    const category = categorySelect.value;

    allProducts.forEach(product => {

        const matchBrand = brand === "all" || 
            product.classList.contains(`produto-${brand}`);

        const matchCategory = category === "all" || 
            product.classList.contains(`categoria-${category}`);

        if (matchBrand && matchCategory) {
            product.style.display = "flex";
        } else {
            product.style.display = "none";
        }
    });

    // Produtos visíveis após filtro
    const visibleProducts = Array.from(allProducts)
        .filter(product => product.style.display !== "none");

    // Ordenação
    visibleProducts.sort((a, b) => {
        const priceA = getPriceValue(a);
        const priceB = getPriceValue(b);

        if (sort === "price-asc") return priceA - priceB;
        if (sort === "price-desc") return priceB - priceA;

        return 0;
    });

    // Reinsere na nova ordem
    visibleProducts.forEach(product => {
        container.appendChild(product);
    });
}

/* Extrai valor numérico do preço */
function getPriceValue(product) {
    const text = product.querySelector(".price").textContent;

    return parseFloat(
        text.replace("Desde", "").replace("€", "").trim()
    );
}