from django.urls import path
from .views import ListCourse, DetailCourse, ListEnrolledCourse, CourseChats
from rest_framework.routers import SimpleRouter


router = SimpleRouter()


urlpatterns = [
    path('<int:pk>/', DetailCourse),
    path('', ListCourse.as_view()),
    path('enrolled/', ListEnrolledCourse.as_view()),
    path('<int:pk>/chats/', CourseChats),
]

urlpatterns += router.urls