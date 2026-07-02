from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
import tablib

from .models import NovedadPedido
from .forms import NovedadPedidoForm

class NovedadListView(LoginRequiredMixin, ListView):
    model = NovedadPedido
    template_name = 'dashboard/novedades.html'
    context_object_name = 'novedades'
    ordering = '-fecha_novedad'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('pedido', 'usuario_reporta')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(pedido__id__icontains=query) | Q(descripcion__icontains=query))
        return queryset


class NovedadCreateView(LoginRequiredMixin, CreateView):
    model = NovedadPedido
    form_class = NovedadPedidoForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('novedades_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Registrar Novedad', 'button_text': 'Guardar Novedad'})
        return context


class NovedadUpdateView(LoginRequiredMixin, UpdateView):
    model = NovedadPedido
    form_class = NovedadPedidoForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('novedades_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': f'Editar Novedad #{self.object.id}', 'button_text': 'Guardar Cambios'})
        return context


class NovedadDeleteView(LoginRequiredMixin, DeleteView):
    model = NovedadPedido
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('novedades_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Eliminar Novedad', 'object': self.object})
        return context


class ExportNovedadesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        novedades = NovedadPedido.objects.all().select_related('pedido', 'usuario_reporta')
        headers = ('ID', 'Pedido', 'Usuario', 'Descripción', 'Fecha')
        rows = []
        for n in novedades:
            rows.append((
                n.id, f'#{n.pedido.id}', 
                f'{n.usuario_reporta.primer_nombre} {n.usuario_reporta.primer_apellido}',
                n.descripcion, n.fecha_novedad.strftime('%d/%m/%Y %H:%M')
            ))
        
        file_format = kwargs.get('file_format', 'pdf')
        if file_format == 'pdf':
            from apps.core.views import render_to_pdf
            return render_to_pdf(headers, rows, "REPORTE DE NOVEDADES", "novedades_reporte.pdf")
        from apps.core.views import export_dataset
        return export_dataset(tablib.Dataset(*rows, headers=headers), file_format, "novedades_reporte")
