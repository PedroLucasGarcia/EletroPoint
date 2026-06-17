// User dropdown
const userIcon = document.getElementById('userIcon');
const userDropdown = document.getElementById('userDropdown');

if (userIcon) {
    userIcon.addEventListener('click', function(e) {
        e.stopPropagation();
        userDropdown.classList.toggle('active');
    });

    document.addEventListener('click', function() {
        userDropdown.classList.remove('active');
    });
}