function iniciarSeccion() {
    const usuario = {
        usuario: txtUser.value,
        password: txtPassword.value

    }

    const url = "/iniciarSeccionJson"
    fetch(url, {
        method: "POST",
        body: JSON.stringify(usuario),
        headers: {
            "Content-Type": "application/json",
        },
    })
        
        .then(respuesta => respuesta.json())
        .then(resultado => {
            console.log(resultado)
            if (resultado.estado) {
                location.href = "/listarProductos"
            } else {
                swal.fire("Iniciar Seccion", resultado.mensaje,"warning")
            }
    })
}