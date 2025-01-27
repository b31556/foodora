async function select(restaurant, thing) {
    if (!document.getElementById('popup').classList.contains('visible')){

        document.getElementById('popup').classList.add('visible');
        
        try {
            const response = await fetch(`/foodinfo/${restaurant}/${thing}`);
            
            if (!response.status == 200) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.text();
            
            document.getElementById('popup').innerHTML = data
        } catch (error) {
            console.error("Error fetching food info:", error);
            alert("Hiba történt az adatok lekérdezésekor!");
        }

    }
}

async function selected(restaurant,thing) {
    try {
        // Collect all radio button selections
        const selectedChoices = {};
        document.querySelectorAll('input[type="radio"]:checked').forEach(radio => {
            selectedChoices[radio.name] = radio.value;
        });

        // Collect all checked checkboxes
        const selectedExtras = [];
    

        document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
            
            const label = document.querySelector(`label[for="${checkbox.id}"]`);
            if (label) {
                selectedExtras.push(label.textContent);
            }
        });

        // Combine data into one object
        const requestData = {
            choices: selectedChoices,
            extras: selectedExtras
        };

        // Send the data via a POST request
        const response = await fetch(`/placeorderpart/${restaurant}/${thing}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.text();
        document.getElementById('popup').innerHTML = data;
    } catch (error) {
        console.error("Error fetching food info:", error);
        alert("Hiba történt az adatok lekérdezésekor!");
    }
}