async function atstart(restaurant) {
    const response = await fetch(`/getbasketcount/${restaurant}`);
    if (response.status == 200 && !response.redirected) {
        const data = await response.text();
        document.getElementById('basket-count').innerHTML = data;
    }
}

atstart(document.location.pathname.split('/')[2]);


async function select(restaurant, thing) {
    if (!document.getElementById('popup').classList.contains('visible')){

        document.getElementById('popup').classList.add('visible');
        
        try {
            const response = await fetch(`/foodinfo/${restaurant}/${thing}`);
            
            if (response.status == 304) {
                tologin()
            }


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


        if (response.status == 200) {
            document.getElementById("popup").classList.remove("visible")
    basketCountElement=document.getElementById('basket-logo');
    if (basketCountElement.style.display === 'none' || basketCountElement.style.display === '') {
        basketCountElement.style.display = 'block';
      }
    basketCountElement.style.transform = 'scale(1.7)'; // Make it bigger
    setTimeout(() => {
      basketCountElement.style.transform = 'scale(1)'; // Reset to normal size
    }, 400); // Duration of the pop effect in milliseconds

    basketcountelem=document.getElementById('basket-count');
    basketcountelem.innerHTML=parseInt(basketcountelem.innerHTML)+1;
        }

    } catch (error) {
        console.error("Error fetching food info:", error);
        alert("Hiba történt az adatok lekérdezésekor!");
    }

    
  
}




async function basket(restaurant) {
    document.getElementById("basket").classList.add("visible")
    const response = await fetch(`/getbasket/${restaurant}`);
    if (response.redirected) {
        document.location.href = response.url;}
    if (response.status == 200) {
        const data = await response.text();
        document.getElementById('basket').innerHTML = data;
    }
}

async function resetbasket(restaurant) {
    const response = await fetch(`/resetbasket/${restaurant}`);
    atstart(restaurant);
    document.getElementById("basket").classList.remove("visible")}


async function confirmorder(restaurant) {
    try {
        const response = await fetch(`/confirmorder/${restaurant}`);
        if (response.redirected) {
            document.location.href = response.url;
        }
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
    } catch (error) {
        console.error("Error fetching food info:", error);
        alert("Hiba történt!");
    }
}