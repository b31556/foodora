function tologin(){
    var redr = window.location.pathname
    fetch('/login?redirect='+redr) // API URL
        .then(response => {
            if (!response.ok) { // Ellenőrzi, hogy a válasz sikeres volt-e
            throw new Error('Hálózati válasz nem volt megfelelő');
            }
            if (response.redirected){
                window.location.href = response.url;
            } 
            // A válasz JSON formátumban
        })
}