from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from .models import Ticket, Comment
from .forms import TicketForm, CommentForm

class HelpdeskAccessMixin(PermissionRequiredMixin):
    permission_required = 'core.access_helpdesk'
    raise_exception = True


class TicketListView(LoginRequiredMixin, HelpdeskAccessMixin, ListView):
    model = Ticket
    template_name = 'helpdesk/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on role
        if user.is_client():
            queryset = queryset.filter(created_by=user)
        elif user.is_collaborator():
            # Collaborators see tickets they created or are assigned to
            queryset = queryset.filter(Q(created_by=user) | Q(assigned_to=user))
        # Managers/Admins see all
        
        return queryset.order_by('-created_at')

class TicketCreateView(LoginRequiredMixin, HelpdeskAccessMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'helpdesk/ticket_form.html'
    success_url = reverse_lazy('helpdesk:ticket_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class TicketDetailView(LoginRequiredMixin, HelpdeskAccessMixin, DetailView):
    model = Ticket
    template_name = 'helpdesk/ticket_detail.html'

    def get_queryset(self):
        """Restrict ticket visibility based on user role/ownership."""
        base_qs = super().get_queryset()
        user = self.request.user
        if user.is_client():
            return base_qs.filter(created_by=user)
        if user.is_collaborator():
            return base_qs.filter(Q(created_by=user) | Q(assigned_to=user))
        return base_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        comments = self.object.comments.all().order_by('created_at')
        if not (self.request.user.is_manager() or self.request.user.is_superuser):
            comments = comments.filter(is_internal=False)
        context['comments'] = comments
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = self.object
            comment.author = request.user
            # Clients cannot make internal comments
            if request.user.is_client():
                comment.is_internal = False
            comment.save()
            return redirect('helpdesk:ticket_detail', pk=self.object.pk)
        return self.render_to_response(self.get_context_data(comment_form=form))


class TicketUpdateView(LoginRequiredMixin, HelpdeskAccessMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'helpdesk/ticket_form.html'
    success_url = reverse_lazy('helpdesk:ticket_list')

    def get_queryset(self):
        # Permitir edição apenas para staff/gestores ou criador
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.is_staff or user.is_manager():
            return qs
        return qs.filter(created_by=user)

    def form_valid(self, form):
        # Na edição, atualizar a instância normalmente
        return super().form_valid(form)
