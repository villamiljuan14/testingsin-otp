from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from django.db.models import Q, Avg
import tablib
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import (
    Vehiculo, Ruta, ParadaRuta, EstadoVehiculo, EstadoRuta, 
    PrioridadRuta, MetricaRuta
)
from .forms import VehiculoForm, RutaForm
from .permissions import IsAdminUser, IsFleetManager, IsConductor

# ── VISTAS DE DASHBOARD (Bento Grid) ──

class VehiculoListView(LoginRequiredMixin, ListView):
    model = Vehiculo
    template_name = 'dashboard/vehiculos.html'
    context_object_name = 'vehiculos'
    ordering = 'placa'

    def get_paginate_by(self, queryset):
        per_page = int(self.request.GET.get('per_page', 10))
        return per_page if per_page in [5, 10, 15, 20] else 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        estado = self.request.GET.get('estado')
        if query:
            queryset = queryset.filter(Q(placa__icontains=query) | Q(modelo__icontains=query) | Q(marca__icontains=query))
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = {
            'total': Vehiculo.objects.count(),
            'disponibles': Vehiculo.objects.filter(estado=EstadoVehiculo.DISPONIBLE).count(),
            'en_ruta': Vehiculo.objects.filter(estado=EstadoVehiculo.EN_RUTA).count(),
            'mantenimiento': Vehiculo.objects.filter(estado=EstadoVehiculo.MANTENIMIENTO).count(),
        }
        per_page = int(self.request.GET.get('per_page', 10))
        items_por_pagina = per_page if per_page in [5, 10, 15, 20] else 10
        query_string = self.request.GET.copy()
        query_string.pop('page', None)
        context.update({
            'estados': EstadoVehiculo.choices,
            'stats': stats,
            'current_q': self.request.GET.get('q', ''),
            'current_estado': self.request.GET.get('estado', ''),
            'items_por_pagina': items_por_pagina,
            'query_params': query_string.urlencode(),
        })
        return context

class VehiculoCreateView(LoginRequiredMixin, CreateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'dashboard/vehiculo_form.html'
    success_url = reverse_lazy('vehiculos_list')

class VehiculoUpdateView(LoginRequiredMixin, UpdateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'dashboard/vehiculo_form.html'
    success_url = reverse_lazy('vehiculos_list')

class VehiculoDeleteView(LoginRequiredMixin, DeleteView):
    model = Vehiculo
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('vehiculos_list')

class ExportVehiculosView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        vehiculos = Vehiculo.objects.all()
        headers = ('ID', 'Placa', 'Marca', 'Modelo', 'Año', 'Tipo', 'Capacidad (kg)', 'Volumen (m³)', 'Estado')
        rows = []
        for v in vehiculos:
            rows.append((
                v.id, v.placa, v.marca, v.modelo, v.anio,
                v.tipo_vehiculo, float(v.capacidad_peso_kg), float(v.capacidad_volumen_m3),
                v.get_estado_display(),
            ))
        file_format = kwargs.get('file_format', 'pdf')
        from apps.core.views import render_to_pdf, export_dataset
        import tablib
        if file_format == 'pdf':
            return render_to_pdf(list(headers), rows, "REPORTE DE VEHÍCULOS", "vehiculos_reporte.pdf")
        dataset = tablib.Dataset(*rows, headers=list(headers))
        return export_dataset(dataset, file_format, 'vehiculos')


class ExportRutasView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        rutas = Ruta.objects.select_related('vehiculo', 'conductor').all()
        headers = ('ID', 'Nombre', 'Código', 'Conductor', 'Vehículo', 'Fecha Programada', 'Estado')
        rows = []
        for r in rutas:
            rows.append((
                r.id, r.nombre, r.codigo_ruta,
                r.conductor.email if r.conductor else '—',
                r.vehiculo.placa if r.vehiculo else '—',
                r.fecha_programada.strftime('%Y-%m-%d') if r.fecha_programada else '—',
                r.get_estado_display(),
            ))
        file_format = kwargs.get('file_format', 'pdf')
        from apps.core.views import render_to_pdf, export_dataset
        import tablib
        if file_format == 'pdf':
            return render_to_pdf(list(headers), rows, "REPORTE DE RUTAS", "rutas_reporte.pdf")
        dataset = tablib.Dataset(*rows, headers=list(headers))
        return export_dataset(dataset, file_format, 'rutas')

class RutaListView(LoginRequiredMixin, ListView):
    model = Ruta
    template_name = 'dashboard/rutas.html'
    context_object_name = 'rutas'
    ordering = '-creado_en'

    def get_paginate_by(self, queryset):
        per_page = int(self.request.GET.get('per_page', 10))
        return per_page if per_page in [5, 10, 15, 20] else 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('hub_origen', 'creado_por')
        query = self.request.GET.get('q')
        status_filter = self.request.GET.get('status')
        if query:
            queryset = queryset.filter(Q(nombre__icontains=query) | Q(codigo_ruta__icontains=query))
        if status_filter:
            queryset = queryset.filter(estado=status_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = {
            'total': Ruta.objects.count(),
            'programadas': Ruta.objects.filter(estado=EstadoRuta.PLANIFICADA).count(),
            'en_proceso': Ruta.objects.filter(estado=EstadoRuta.EN_CURSO).count(),
            'completadas': Ruta.objects.filter(estado=EstadoRuta.COMPLETADA).count(),
        }
        per_page = int(self.request.GET.get('per_page', 10))
        items_por_pagina = per_page if per_page in [5, 10, 15, 20] else 10
        query_string = self.request.GET.copy()
        query_string.pop('page', None)
        context.update({
            'estados': EstadoRuta.choices,
            'stats': stats,
            'current_q': self.request.GET.get('q', ''),
            'current_status': self.request.GET.get('status', ''),
            'items_por_pagina': items_por_pagina,
            'query_params': query_string.urlencode(),
        })
        return context

class RutaCreateView(LoginRequiredMixin, CreateView):
    model = Ruta
    form_class = RutaForm
    template_name = 'dashboard/ruta_form.html'
    success_url = reverse_lazy('rutas_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Ruta'
        context['button_text'] = 'Crear Ruta'
        return context

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        import random
        from django.utils import timezone
        form.instance.codigo_ruta = f"RUTA-{timezone.now().year}-{random.randint(1000, 9999)}"
        return super().form_valid(form)

class RutaUpdateView(LoginRequiredMixin, UpdateView):
    model = Ruta
    form_class = RutaForm
    template_name = 'dashboard/ruta_form.html'
    success_url = reverse_lazy('rutas_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Ruta'
        context['button_text'] = 'Actualizar Ruta'
        return context

class RutaDeleteView(LoginRequiredMixin, DeleteView):
    model = Ruta
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('rutas_list')

# ── API VIEWSETS (Modular Logic) ──

class RutaViewSet(viewsets.ModelViewSet):
    queryset = Ruta.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser() | IsFleetManager()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        ruta = self.get_object()
        ruta.estado = 'COMPLETADA'
        ruta.save()
        return Response({'status': 'Ruta completada'})
