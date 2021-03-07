
$(document).ready(function () { 
    setValues();
  });

function precioTotal(){
    cantidad = document.getElementById('cantidad').value;
    precio = document.getElementById('precio').value;

    precioT = cantidad * precio;

    return document.getElementById('precioTotal').setAttribute('value', precioT) ;
}

function setValues(){
    let precio = parseFloat(document.getElementById('precio').value, 10);
    return [document.getElementById('precio').setAttribute('value', precio), document.getElementById('precioTotal').setAttribute('value', precio)]
}


