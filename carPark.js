const Slot = document.getElementById('slot');

function getStatus() {
    fetch("http://158.108.182.5:50002/find")
        .then((response) => response.json())
        .then(data => console.log(data));
}


