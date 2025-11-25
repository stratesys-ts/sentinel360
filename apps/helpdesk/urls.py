from django.urls import path
from .views import TicketListView, TicketCreateView, TicketDetailView, TicketUpdateView

app_name = 'helpdesk'

urlpatterns = [
    path('', TicketListView.as_view(), name='ticket_list'),
    path('create/', TicketCreateView.as_view(), name='ticket_create'),
    path('<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('<int:pk>/edit/', TicketUpdateView.as_view(), name='ticket_update'),
]
