from django.urls import path
from .views import OrderCreateView, ProposalCreateView, MainServiceListView, AvailableOrdersView

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='create_order'),
    path('proposal/', ProposalCreateView.as_view(), name='create_proposal'),
    path('services/', MainServiceListView.as_view(), name='main-service_list'),
    path('available-orders/', AvailableOrdersView.as_view(), name='available-orders'),

]
