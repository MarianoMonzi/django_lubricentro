document.addEventListener('DOMContentLoaded', function () {
    const abrir = document.getElementById('open');
    const cerrar = document.getElementById('close');
    const popup = document.getElementById('popup');
    const overlay = document.getElementById('overlay');

    abrir.onclick = function () {
        popup.style.display = 'block';
        overlay.style.display = 'block';
    };

    cerrar.onclick = function () {
        popup.style.animation = 'slideUp 0.5s ease';
        setTimeout(function () {
            popup.style.display = 'none';
            overlay.style.display = 'none';
            popup.style.animation = 'slideDown 0.5s ease';
            window.location.reload();  // Redireccionar o recargar la página
        }, 250);
    };

    overlay.onclick = function () {
        popup.style.animation = 'slideUp 0.5s ease';
        setTimeout(function () {
            popup.style.display = 'none';
            overlay.style.display = 'none';
            popup.style.animation = 'slideDown 0.5s ease';
            window.location.reload();  // Redireccionar o recargar la página
        }, 250);
    };





    

    

    


});

$(document).ready(function () {
    // Cargar nombres de mecánicos al cargar la página
    $.ajax({
        type: 'GET',
        url: '/obtener_nombres_mecanicos/',
        success: function (response) {
            var select = document.getElementById('selectMecanico');


            if (select) {
                select.innerHTML = '<option value="">Selecciona un mecánico...</option>';

                response.mecanicos.forEach(function (mecanico) {
                    var option = document.createElement('option');
                    option.value = mecanico.id; // Puedes usar el ID si lo necesitas
                    option.textContent = mecanico.nombre;
                    select.appendChild(option);
                });
            }




        },
        error: function (xhr, status, error) {
            alert('Error al cargar nombres de mecánicos');
        }
    });
});

function cargarDetallesCliente(clienteId) {
    $.ajax({
        type: 'GET',
        url: '/detalles_cliente/',
        data: { cliente_id: clienteId },
        success: function (response) {
            // Actualizar el contenido del popup con los detalles del cliente
            $('#detalleClienteContainer').html(response);

            $.ajax({
                type: 'GET',
                url: '/tareas_cliente/',
                data: { cliente_id: clienteId },
                success: function (response) {
                    $('#tbody-tareas').empty(); // Vaciar el contenido existente antes de agregar nuevas tareas

                    response.tareas.forEach(function (tarea) {
                        console.log(tarea)
                        var fila = `<tr data-tarea_cliente-id="${tarea.id}">
                        <td>${tarea.fecha}</td>
                        <td>${tarea.servicio}</td>
                        <td>${tarea.kilometros}</td>
                        <td>${tarea.proxservicio}</td>
                        <td>${tarea.mecanico}</td>
                        <td><a href="/planilla/?servicio=${tarea.servicio}&cliente_id=${clienteId}&fecha=${tarea.fecha}&kms=${tarea.kilometros}&tarea_id=${tarea.id}"><i class="ri-file-list-2-line"></i></a><i class="ri-close-circle-line" ></i></td>
                        </tr>`;
                        $('#tbody-tareas').append(fila);
                    });
                },
                error: function (xhr, status, error) {
                    alert('Error al cargar los detalles de las tareas');
                }
            });

            $('#popupUser').fadeIn();
            $('#overlay').fadeIn();
        },
        error: function (xhr, status, error) {
            alert('Error al cargar los detalles del cliente');
        }
    });
}

// Evento para abrir el popup del cliente al hacer clic en su nombre
$(document).on('click', '.openUser', function() {
    var clienteId = $(this).data('cliente-id');
    cargarDetallesCliente(clienteId);
});

$(document).ready(function () {
    $('#nuevoClienteForm').submit(function (e) {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/guardar_cliente/',
            data: $(this).serialize(),
            success: function (response) {
                $('#nuevoClienteForm')[0].reset();
                $('#popup').hide();
                
                // Agregar el ID del cliente al input hidden
                $('#clienteIdInput').val(response.cliente_id);
                console.log($('#clienteIdInput').val());
                
                // Abre el popup de detalles del cliente
                $('#detalleClienteContainer').load('/detalles_cliente/?cliente_id=' + response.cliente_id);
                $('#popupUser').fadeIn();
                $('#overlay').fadeIn();
            },
            error: function (xhr, status, error) {
                alert('Error al guardar el cliente');
            }
        });
    });

    $('#nuevaTareaForm').submit(function (e) {

        e.preventDefault();
        var selectServicio = $('#selectServicio').val();
        console.log('La opción es:', selectServicio);

        $.ajax({
            type: 'POST',
            url: '/guardar_tarea/',
            data: $(this).serialize(),
            success: function (response) {
                alert('Tarea guardada correctamente');
                console.log(selectServicio)
                location.reload();
                $('#nuevaTareaForm')[0].reset();
                $('#popup').hide();
            },
            error: function (xhr, status, error) {
                alert('Error al guardar Tarea');
                console.log(xhr.responseText);
            }
        });
    });
})