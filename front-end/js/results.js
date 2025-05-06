document.addEventListener("DOMContentLoaded", function () {
    const spinner = document.getElementById('spinner');
    const fieldResponse = window.fieldResponse || {};

    // Log full fieldResponse for debugging
    console.log("Full fieldResponse:", JSON.stringify(fieldResponse, null, 2));

    if (fieldResponse.error || !fieldResponse.recommended_crops) {
        console.error("Error in field response:", fieldResponse.error || "No crops returned");
        spinner.classList.add('d-none');
        alert("Ürün önerileri alınamadı. Lütfen tekrar deneyin.");
        return;
    }

    const crops = fieldResponse.recommended_crops || [];
    const lat = Number(fieldResponse.latitude) || 40; // Fallback to 40
    const lon = Number(fieldResponse.longitude) || 40; // Fallback to 40
    const area_sqm = fieldResponse.area_sqm || 0;

    // Log all crop names for debugging
    console.log("Recommended crops:", JSON.stringify(crops, null, 2));

    // Update crop boxes
    for (let i = 1; i <= 5; i++) {
        const crop = crops[i - 1] || { crop_name: "Bilinmeyen Ürün", water_requirement_liters_per_sqm: 0, suitability_score: 0 };
        if (!crop.crop_name || typeof crop.crop_name !== 'string') {
            console.warn(`Invalid crop_name for crop ${i}:`, crop.crop_name);
            crop.crop_name = "Bilinmeyen Ürün";
        }
        const imgElement = document.getElementById(`crop-img-${i}`);
        const titleElement = document.getElementById(`crop-title-${i}`);
        const waterElement = document.getElementById(`crop-water-${i}`);
        const scoreElement = document.getElementById(`crop-score-${i}`);

        // Normalize crop name for image filename: lowercase, remove spaces, replace Turkish characters
        const normalizedCrop = crop.crop_name
            .toLowerCase()
            .replace(/ı/g, 'i')
            .replace(/ş/g, 's')
            .replace(/ğ/g, 'g')
            .replace(/ü/g, 'u')
            .replace(/ç/g, 'c')
            .replace(/ö/g, 'o')
            .replace(/\s+/g, '');
        const imgSrc = normalizedCrop ? `img/${normalizedCrop}.png` : 'img/placeholder.png';

        // Debug: Log crop name and image path
        console.log(`Crop ${i}: ${crop.crop_name} -> ${imgSrc}`);

        imgElement.src = imgSrc;
        imgElement.alt = crop.crop_name;
        imgElement.onerror = () => {
            console.warn(`Image not found: ${imgSrc}, falling back to placeholder`);
            imgElement.src = 'img/placeholder.png';
            imgElement.onerror = null; // Prevent infinite loop
        };
        titleElement.innerText = crop.crop_name;
        waterElement.innerText = `${crop.water_requirement_liters_per_sqm} L/m²`;
        scoreElement.innerText = `${crop.suitability_score}`;

        // Update onclick to show crop details in modal
        imgElement.parentElement.onclick = () => openPopup(
            imgSrc,
            crop.crop_name,
            lat,
            lon,
            area_sqm,
            fieldResponse.weather_recommendations || [] // Pass weather data
        );
    }

    // Hide loading screen
    spinner.classList.add('d-none');
});