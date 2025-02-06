async function confirmlocation(){
    var hn = document.getElementById('hn').value;
    var search = document.getElementById('search').value;
    if (hn == "" || search == "") {
        alert("please select house number and location");
        return false;
    }

    var response = await fetch('/confirmlocation', {
        method: 'POST',
        body: JSON.stringify({
            hn: hn,
            search: search
        })
    })
    if (response.status == 200) {
        window.location.href = "/payment";
    }
    else {
        const message= await response.text()
        alert(message);
    }
}