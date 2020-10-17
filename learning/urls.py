from django.urls import path
from .views import ListCourse, DetailCourse
from rest_framework.routers import SimpleRouter

router = SimpleRouter()


urlpatterns = [
    path('<int:pk>/', DetailCourse.as_view()),
    path('', ListCourse.as_view()),
]

urlpatterns += router.urls