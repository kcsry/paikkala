from django.contrib import admin
from django.conf.urls import url

from baikal.views import ReservationView, IndexView

urlpatterns = [
    url('^admin/', admin.site.urls),
    url('^(?P<pk>\d+)/$', ReservationView.as_view()),
    url('^$', IndexView.as_view()),
]
