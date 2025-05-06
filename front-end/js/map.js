
document.addEventListener("DOMContentLoaded", function () {
    
    const map = L.map('map').setView([39.93, 32.85], 6); // Ankara civarı koordinatlar

    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> ekibi'
    }).addTo(map);

    
    let marker;

    
    map.on('click', function(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        
        if (marker) {
            map.removeLayer(marker);
        }

        
        marker = L.marker([lat, lng]).addTo(map);

        
        marker.bindPopup("<strong>Burayı Seçtiniz</strong><br>Enlem: " + lat.toFixed(6) + "<br>Boylam: " + lng.toFixed(6))
               .openPopup();

        
        console.log("Tıklanan Konum:", {
            latitude: lat.toFixed(6),
            longitude: lng.toFixed(6)
        });

        
        const infoDiv = document.getElementById("coordinates-info");
        if (infoDiv) {
            infoDiv.innerHTML = `
                <p><strong>Tıklanan Konum:</strong><br>
                Enlem: ${lat.toFixed(6)}<br>
                Boylam: ${lng.toFixed(6)}
                </p>
            `;
        }
    });
});