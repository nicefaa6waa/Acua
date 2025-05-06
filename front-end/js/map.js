document.addEventListener("DOMContentLoaded", function () {
    const map = L.map('map').setView([39.93, 32.85], 6); // Ankara civarı koordinatlar

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a> ekibi'
    }).addTo(map);

    let marker;

    map.on('click', function(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        // Remove existing marker if present
        if (marker) {
            map.removeLayer(marker);
        }

        // Add new marker
        marker = L.marker([lat, lng]).addTo(map);
        marker.bindPopup("<strong>Seçilen Konum</strong><br>Enlem: " + lat.toFixed(6) + "<br>Boylam: " + lng.toFixed(6)).openPopup();

        // Update modal content
        document.getElementById('confirmLat').innerText = lat.toFixed(6);
        document.getElementById('confirmLng').innerText = lng.toFixed(6);

        // Show confirmation modal
        const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
        confirmModal.show();

        // Handle Yes button
        const yesButton = document.getElementById('confirmYes');
        yesButton.onclick = function() {
            window.open(`results.html?lat=${lat.toFixed(6)}&lng=${lng.toFixed(6)}`, '_blank');
        };
    });
});