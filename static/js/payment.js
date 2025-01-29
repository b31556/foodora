async function dopayment() {
    var response = await fetch('/dopayment', {
        method: 'POST'
    })
    if (response.status == 200) {
        window.location.href = "/track-order";
    }
    else {
        alert(response.text);
    }
}