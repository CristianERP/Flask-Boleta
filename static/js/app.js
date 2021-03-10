$(document).ready(function () { 
    setValues();

});

function precioTotal(){
    cantidad = document.getElementById('cantidad').value;
    precio = document.getElementById('precio').value;

    precioT = cantidad * precio;

    return document.getElementById('total').value = document.getElementById('cantidad').value * document.getElementById('precio').value;
}

function setValues(){
    let precio = parseFloat(document.getElementById('precio').value, 10);
    return [document.getElementById('precio').setAttribute('value', precio), document.getElementById('total').setAttribute('value', precio)]
}


