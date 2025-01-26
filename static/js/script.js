function navigateToRestaurant(name) {
    window.location.href = `/restaurant/${name}`;
}
function toggleMenu() {
    document.getElementById('sidebar').classList.toggle('show');
}
