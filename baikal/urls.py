from django.conf.urls import url
from django.contrib import admin

from baikal.views import IndexView
from paikkala.printing.views import PrintView
from paikkala.views import InspectionView, RelinquishView, ReservationView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^relinquish/(?P<pk>\d+)/$', RelinquishView.as_view(require_same_user=False), name='relinquish'),
    url(r'^reserve/(?P<pk>\d+)/$', ReservationView.as_view(template_name='generic_form.html'), name='reserve'),
    url(r'^inspect/(?P<pk>\d+)/(?P<key>.+?)/$', InspectionView.as_view(require_same_user=False, template_name='inspect.html'), name='inspect'),
    url(r'^print/(?P<pk>\d+)/$', PrintView.as_view(template_name='generic_form.html'), name='print'),
    url(r'^$', IndexView.as_view()),
]
