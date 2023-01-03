from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path('automobiliai/', views.automobiliai, name='automobiliai'),
    path('automobiliai/<int:automobilis_id>', views.automobilis, name='automobilis'),
    path('search/', views.search, name='search'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('uzsakymai/', views.UzsakymasListView.as_view(), name='uzsakymai'),
    path('uzsakymai/<int:pk>', views.UzsakymasDetailView.as_view(), name="uzsakymas"),
    path('manouzsakymai/', views.MyUzsakymasListView.as_view(), name='manouzsakymai'),
    path('manouzsakymai/new', views.MyUzsakymasCreateView.as_view(), name='manouzsakymas_new'),
    path('uzsakymai/<int:pk>/update', views.MyUzsakymasUpdateView.as_view(), name="manouzsakymas_update"),
    path('uzsakymai/<int:pk>/delete', views.MyUzsakymasDeleteView.as_view(), name="manouzsakymas_delete"),
    path('uzsakymai/<int:pk>/newline', views.MyUzsakymoEiluteCreateView.as_view(), name="manouzsakymas_newline"),
    path('uzsakymai/<int:pk2>/deleteline/<int:pk>', views.MyUzsakymoEiluteDeleteView.as_view(), name="manouzsakymas_deleteline"),
    path('uzsakymai/<int:pk2>/updateline/<int:pk>', views.MyUzsakymoEiluteUpdateView.as_view(), name="manouzsakymas_updateline"),

]