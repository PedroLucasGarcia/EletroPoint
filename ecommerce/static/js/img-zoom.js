// ── ZOOM DA IMAGEM ──────────────────────────────────────
const imageModal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const modalClose = document.getElementById('modalClose');
const modalPrev = document.getElementById('modalPrev');
const modalNext = document.getElementById('modalNext');
const modalDots = document.querySelectorAll('.modal-dot');

// Abre o modal com a imagem do slide ativo
function openModal() {
    updateModalImage();
    imageModal.classList.add('active');
    document.body.classList.add('no-scroll');
}

function closeModal() {
    imageModal.classList.remove('active');
    document.body.classList.remove('no-scroll');
}

// Atualiza imagem e dots do modal com base no slide atual do carousel
function updateModalImage() {
    const activeImg = document.querySelector('.item.active .carousel-img img');
    modalImage.src = activeImg.src;

    modalDots.forEach(function(dot, i) {
        dot.classList.toggle('active', i === current);
    });
}

// Clicar na imagem ativa do carousel abre o modal
document.querySelector('.carousel-list').addEventListener('click', function(e) {
    const img = e.target.closest('.item.active .carousel-img img');
    if (img) openModal();
});

// Navegação dentro do modal — reutiliza goTo() do carousel principal
modalPrev.addEventListener('click', function() {
    goTo(current - 1);
    updateModalImage();
});
modalNext.addEventListener('click', function() {
    goTo(current + 1);
    updateModalImage();
});
modalDots.forEach(function(dot, i) {
    dot.addEventListener('click', function() {
        goTo(i);
        updateModalImage();
    });
});

// Fechar modal
modalClose.addEventListener('click', closeModal);
imageModal.addEventListener('click', function(e) {
    if (e.target === imageModal) closeModal();
});
document.addEventListener('keydown', function(e) {
    if (imageModal.classList.contains('active')) {
        if (e.key === 'Escape') closeModal();
        if (e.key === 'ArrowLeft') { goTo(current - 1); updateModalImage(); }
        if (e.key === 'ArrowRight') { goTo(current + 1); updateModalImage(); }
    }
});