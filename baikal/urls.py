from django.contrib import admin
from django.conf.urls import url

from baikal.views import IndexView, InspectionView
from paikkala.views import ReservationView, RelinquishView

urlpatterns = [
    url('^admin/', admin.site.urls),
    url('^relinquish/(?P<pk>\d+)/$', RelinquishView.as_view(), name='relinquish'),
    url('^reserve/(?P<pk>\d+)/$', ReservationView.as_view(template_name='reserve.html'), name='reserve'),
    url('^inspect/(?P<pk>\d+)/(?P<key>.+?)/$', InspectionView.as_view(template_name='inspect.html'), name='inspect'),
    url('^$', IndexView.as_view()),
]
