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
