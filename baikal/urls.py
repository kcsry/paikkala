from django.conf.urls import url
from django.contrib import admin

from baikal.views import IndexView, InspectionView
from paikkala.views import RelinquishView, ReservationView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^relinquish/(?P<pk>\d+)/$', RelinquishView.as_view(), name='relinquish'),
    url(r'^reserve/(?P<pk>\d+)/$', ReservationView.as_view(template_name='reserve.html'), name='reserve'),
    url(r'^inspect/(?P<pk>\d+)/(?P<key>.+?)/$', InspectionView.as_view(template_name='inspect.html'), name='inspect'),
    url(r'^$', IndexView.as_view()),
]
