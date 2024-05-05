from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import ClienteForm, ListaCorrectivaForm, ListaPreventivaForm, TareaForm
from .models import Cliente, Tarea, ListaCorrectiva, ListaPreventiva, Planillas, PlanillaCliente
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.forms.models import model_to_dict

# Create your views here.


def loginlubricentro(request):

    if request.method == 'GET':
        return render(request, 'login.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return render(request, 'login.html', {
                'form': AuthenticationForm,
                'error': 'Username or Password is incorrect'
            })
        else:
            login(request, user)
            return redirect('clientes')


@login_required
def clientes(request):
    todos_los_clientes = Cliente.objects.all()
    clientes_con_info = []

    for cliente in todos_los_clientes:
        tareas = Tarea.objects.filter(cliente=cliente.id).order_by('-fecha').first()
        ultima_visita = None
        if tareas:
            ultima_visita = tareas.fecha

        clientes_con_info.append({
            'cliente': cliente,
            'ultima_visita': ultima_visita,
        })

    return render(request, 'cliente.html', {
        'clientes': clientes_con_info
    })


def detalles_cliente(request):
    if request.method == 'GET' and 'cliente_id' in request.GET:
        cliente_id = request.GET['cliente_id']
        cliente = Cliente.objects.get(id=cliente_id)
        tareas = Tarea.objects.filter(cliente=cliente)

        tarea_proxima = tareas.filter(proxservicio__gte=timezone.now().date()).order_by('proxservicio').first()
        detalles_tareas = []

        # Agregar primero las tareas próximas y luego las pasadas a la lista de detalles de tareas
        if tarea_proxima:
            tipo_servicio = tarea_proxima.planilla.lista_tipo if tarea_proxima.planilla else ''

            detalle_tarea_proxima = {
                'id': tarea_proxima.id,
                'fecha': tarea_proxima.fecha,
                'servicio': tipo_servicio,
                'kilometros': tarea_proxima.kilometros,
                'proxservicio': tarea_proxima.proxservicio,
                'mecanico': tarea_proxima.mecanico.username if tarea_proxima.mecanico else ''
            }
            detalles_tareas.append(detalle_tarea_proxima)

        # Aquí puedes preparar los detalles del cliente para enviar de vuelta al frontend
        detalles_cliente = {
            'nombre': cliente.nombre,
            'patente': cliente.patente,
            'modelo': cliente.modelo,
            'numero': cliente.numero,
            'tarea_proxima': tarea_proxima.proxservicio if tarea_proxima else None  
            # Agrega más campos si los necesitas
        }
        return render(request, 'detalles_cliente.html', {'cliente': detalles_cliente})
    else:
        return JsonResponse({'error': 'ID de cliente no proporcionado'}, status=400)


def tareas_cliente(request):
    if request.method == 'GET' and 'cliente_id' in request.GET:
        cliente_id = request.GET['cliente_id']
        cliente = get_object_or_404(Cliente, id=cliente_id)
        
        # Obtener todas las tareas del cliente
        tareas = Tarea.objects.filter(cliente=cliente)

        # Obtener las tareas próximas a la fecha actual y ordenarlas por proxservicio ascendente
        tareas_proximas = tareas.filter(proxservicio__gte=timezone.now().date()).order_by('proxservicio')

        # Obtener las tareas pasadas y ordenarlas por proxservicio descendente
        tareas_pasadas = tareas.filter(proxservicio__lt=timezone.now().date()).order_by('-proxservicio')

        detalles_tareas = []

        # Agregar primero las tareas próximas y luego las pasadas a la lista de detalles de tareas
        for tarea in tareas_proximas:
            tipo_servicio = tarea.planilla.lista_tipo if tarea.planilla else ''

            detalle = {
                'id': tarea.id,
                'fecha': tarea.fecha,
                'servicio': tipo_servicio,
                'kilometros': tarea.kilometros,
                'proxservicio': tarea.proxservicio,
                'mecanico': tarea.mecanico.username if tarea.mecanico else ''
            }
            detalles_tareas.append(detalle)

        for tarea in tareas_pasadas:
            tipo_servicio = tarea.planilla.lista_tipo if tarea.planilla else ''

            detalle = {
                'id': tarea.id,
                'fecha': tarea.fecha,
                'servicio': tipo_servicio,
                'kilometros': tarea.kilometros,
                'proxservicio': tarea.proxservicio,
                'mecanico': tarea.mecanico.username if tarea.mecanico else ''
            }
            detalles_tareas.append(detalle)

        return JsonResponse({'tareas': detalles_tareas})
    else:
        return JsonResponse({'error': 'ID de cliente no proporcionado'}, status=400)

def buscar_cliente(request):
    query = request.GET.get('q')
    clientes_filtrados = []

    if query:
        clientes_filtrados = (Cliente.objects.filter(
            nombre__icontains=query) | Cliente.objects.filter(
            modelo__icontains=query) | Cliente.objects.filter(
            patente__icontains=query)).distinct()

    clientes_con_info_filtrados = []
    for cliente in clientes_filtrados:
        cliente_dict = model_to_dict(cliente)
        tareas = Tarea.objects.filter(cliente=cliente.id).order_by('-fecha').first()
        ultima_visita = None
        if tareas:
            ultima_visita = tareas.fecha

        cliente_dict['ultima_visita'] = ultima_visita
        clientes_con_info_filtrados.append(cliente_dict)

    if not query:  # Si la consulta está vacía, devolver todos los clientes con última visita
        clientes_con_info_filtrados = list(Cliente.objects.all().values())
        for cliente in clientes_con_info_filtrados:
            cliente['ultima_visita'] = None  # Añadir la clave 'ultima_visita' con valor None por defecto

            tareas = Tarea.objects.filter(cliente=cliente['id']).order_by('-fecha').first()
            if tareas:
                cliente['ultima_visita'] = tareas.fecha

    return JsonResponse(clientes_con_info_filtrados, safe=False)



def guardar_cliente(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        numero = request.POST.get('numero')
        patente = request.POST.get('patente')
        vehiculo = request.POST.get('vehiculo')

        cliente_nuevo = Cliente(
            nombre=nombre, numero=numero, patente=patente, modelo=vehiculo)

        print(cliente_nuevo.modelo)

        cliente_nuevo.save()
        return JsonResponse({'message': 'Cliente guardado correctamente'})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def editar_cliente(request):
    if request.method == 'POST':
        cliente_id = request.GET.get('cliente_id')
        if cliente_id is None:
            return JsonResponse({'error': 'ID del cliente no proporcionado'}, status=400)

        try:
            cliente = Cliente.objects.get(id=cliente_id)
        except Cliente.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)

        # Obtener los campos actualizados del cliente del cuerpo de la solicitud PATCH
        nombre = request.POST.get('nombre')
        numero = request.POST.get('numero')
        patente = request.POST.get('patente')
        modelo = request.POST.get('modelo')

        # Actualizar los campos del cliente solo si se proporcionaron nuevos valores
        if nombre:
            cliente.nombre = nombre
        if numero:
            cliente.numero = numero
        if patente:
            cliente.patente = patente
        if modelo:
            cliente.modelo = modelo

        cliente.save()  # Guardar los cambios en el cliente

        return JsonResponse({'message': 'Cliente actualizado correctamente'})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def guardar_tarea(request):
    if request.method == 'POST':
        cliente_id = request.POST['cliente_id']
        cliente = Cliente.objects.get(id=cliente_id)
        fecha = request.POST.get('fecha')
        proxservicio = request.POST.get('proxservicio')
        selectServicio = request.POST.get('servicio')
        print(selectServicio)
        mecanico_id = request.POST['mecanico']
        mecanico = User.objects.get(id=mecanico_id)
        kilometros = request.POST.get('kilometros')
        print(cliente_id)

        tarea_nueva = Tarea(cliente=cliente, fecha=fecha, planilla=crear_planilla(
            cliente_id, selectServicio), kilometros=kilometros, proxservicio=proxservicio, mecanico=mecanico)

        tarea_nueva.save()
        return JsonResponse({'message': 'Tarea guardada correctamente'})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def eliminar_tarea_cliente(request):
    if request.method == 'DELETE' and 'tarea_cliente_id' in request.GET:
        tarea_cliente_id = request.GET['tarea_cliente_id']
        tarea = get_object_or_404(Tarea, id=tarea_cliente_id)
        tarea.delete()
        return JsonResponse({'success': 'Tarea del cliente eliminada correctamente'})
    else:
        return JsonResponse({'error': 'ID de tarea no proporcionado o método incorrecto'}, status=400)
    
def eliminar_cliente(request):
    if request.method == 'DELETE' and 'cliente_id' in request.GET:
        cliente_id = request.GET['cliente_id']
        cliente = get_object_or_404(Cliente, id=cliente_id)
        cliente.delete()
        return JsonResponse({'success': 'Cliente eliminado correctamente'})
    else:
        return JsonResponse({'error': 'ID de cliente no proporcionado o método incorrecto'}, status=400)


def crear_planilla(cliente_id, selectServicio):
    cliente = Cliente.objects.get(id=cliente_id)
    planilla = None

    if selectServicio == 'Servicio Correctivo':
        planilla = Planillas(cliente=cliente, lista_tipo=selectServicio)
        try:
            planilla.save()
        except IntegrityError as e:
            # Manejar la excepción de clave única u otros errores de integridad
            print(f"Error al guardar la planilla correctiva: {e}")
    else:
        planilla = Planillas(cliente=cliente, lista_tipo=selectServicio)
        try:
            planilla.save()
        except IntegrityError as e:
            # Manejar la excepción de clave única u otros errores de integridad
            print(f"Error al guardar la planilla preventiva: {e}")

    return planilla


def planilla_correctiva(request):
    items = ListaCorrectiva.objects.all()
    print(items)  # Obtener todas las tareas guardadas
    if request.method == 'POST':
        form = ListaCorrectivaForm(request.POST)
        print(form)
        if form.is_valid():
            print(form)
            form.save()
            # Puedes redirigir a una página de éxito
            return redirect('planilla_correctiva')
    else:
        form = ListaCorrectivaForm()
    return render(request, 'planillaCorrectiva.html', {'items': items})


def planilla_preventiva(request):
    items = ListaPreventiva.objects.all()  # Obtener todas las tareas guardadas
    if request.method == 'POST':
        form = ListaPreventivaForm(request.POST)
        if form.is_valid():
            print(form)
            form.save()
            # Puedes redirigir a una página de éxito
            return redirect('planilla_preventiva')
    else:
        form = ListaPreventivaForm()
    return render(request, 'planillaPreventiva.html', {'items': items})


def planilla_personal(request):
    if request.method == 'POST':
        tarea_id = request.POST.get('tarea_id')
        planilla_id = Planillas.objects.get(id=tarea_id)

        # Obtener todos los items enviados en el formulario
        items_post = {k: v for k, v in request.POST.items() if k.startswith('item_')}

        for item_key, item_value in items_post.items():
            cambio = request.POST.get(f'cambio_{item_key.split("_")[-1]}', False)
            checkbox = request.POST.get(f'check_{item_key.split("_")[-1]}', False)
            observaciones = request.POST.get(f'observaciones_{item_key.split("_")[-1]}', '')

            # Verificar si hay PlanillaCliente existentes para este item y esta planilla
            planilla_clientes = PlanillaCliente.objects.filter(planillaId=planilla_id, nombre=item_value)

            if planilla_clientes.exists():
                # Si hay PlanillaCliente existentes, actualizar la primera encontrada
                planilla_cliente = planilla_clientes.first()
                planilla_cliente.cambio = cambio == 'on'
                planilla_cliente.checkbox = checkbox == 'on'
                planilla_cliente.observaciones = observaciones
                planilla_cliente.save()
            else:
                # Si no hay PlanillaCliente existentes, crear uno nuevo
                PlanillaCliente.objects.create(
                    planillaId=planilla_id,
                    nombre=item_value,
                    cambio=cambio == 'on',
                    checkbox=checkbox == 'on',
                    observaciones=observaciones
                )

        return redirect('clientes')
    else:
        cliente_id = request.GET.get('cliente_id')
        cliente = Cliente.objects.get(id=cliente_id)
        fechaTarea = request.GET.get('fecha')
        kmsTarea = request.GET.get('kms')
        tarea_id = request.GET.get('tarea_id')
        
        if PlanillaCliente.objects.filter(planillaId=tarea_id):
            items = PlanillaCliente.objects.filter(planillaId=tarea_id)
            return render(request, 'planilla.html', {'items': items, 'cliente': cliente, 'fecha': fechaTarea, 'kms': kmsTarea})
        else:
            selectServicio = request.GET.get('servicio')
            itemsCorrectivos = ListaCorrectiva.objects.all()
            itemsPreventivos = ListaPreventiva.objects.all()
            listaItems = []
            

            if selectServicio == 'Servicio Correctivo':
                for item in itemsCorrectivos:                    
                    listaItems.append(item)

                return render(request, 'planilla.html', {'items': listaItems, 'cliente': cliente, 'fecha': fechaTarea, 'kms': kmsTarea})
            else:
                for item in itemsPreventivos:
                    listaItems.append(item)

                return render(request, 'planilla.html', {'items': listaItems, 'cliente': cliente, 'fecha': fechaTarea, 'kms': kmsTarea})


def detalle_cliente_planilla(request):
    cliente_id = request.GET['cliente_id']
    cliente = Cliente.objects.get(id=cliente_id)
    # Aquí puedes preparar los detalles del cliente para enviar de vuelta al frontend
    detalles_cliente = {
        'nombre': cliente.nombre,
        'patente': cliente.patente,
        'modelo': cliente.modelo,
        'numero': cliente.numero,
        # Agrega más campos si los necesitas
    }
    return detalles_cliente


def eliminar_item_correctiva(request):
    if request.method == 'DELETE' and 'item_id' in request.GET:
        item_id = request.GET['item_id']
        item = get_object_or_404(ListaCorrectiva, id=item_id)
        item.delete()
        return JsonResponse({'success': 'Item eliminado correctamente'})
    else:
        return JsonResponse({'error': 'ID de item no proporcionado o método incorrecto'}, status=400)


def eliminar_item_preventiva(request):
    if request.method == 'DELETE' and 'item_id' in request.GET:
        item_id = request.GET['item_id']
        item = get_object_or_404(ListaPreventiva, id=item_id)
        item.delete()
        return JsonResponse({'success': 'Item eliminado correctamente'})
    else:
        return JsonResponse({'error': 'ID de item no proporcionado o método incorrecto'}, status=400)


def obtener_nombres_mecanicos(request):
    if request.method == 'GET':
        # Filtrar usuarios que sean mecánicos (puedes ajustar esto según tu lógica de identificación de mecánicos)
        mecanicos = User.objects.all()

        # Obtener los nombres de los mecánicos
        nombres_mecanicos = [
            {'id': mecanico.id, 'nombre': mecanico.username} for mecanico in mecanicos]

        return JsonResponse({'mecanicos': nombres_mecanicos})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def planilla(request):
    return render(request, 'planilla.html')
