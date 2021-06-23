from django.contrib import admin
from django.urls import path

from baikal.views import IndexView
from paikkala.printing.views import PrintView
from paikkala.views import InspectionView, RelinquishView, ReservationView

inspection_view = InspectionView.as_view(require_same_user=False, template_name='inspect.html')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('relinquish/<int:pk>/', RelinquishView.as_view(require_same_user=False), name='relinquish'),
    path('reserve/<int:pk>/', ReservationView.as_view(template_name='generic_form.html'), name='reserve'),
    path(r'^inspect/<int:pk>/<key>/$', inspection_view, name='inspect'),
    path('print/<int:pk>/', PrintView.as_view(template_name='generic_form.html'), name='print'),
    path('', IndexView.as_view()),
]
