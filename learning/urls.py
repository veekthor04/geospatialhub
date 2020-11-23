from django.urls import path
from .views import ListCourse, ListCourseCategory, DetailCourse, ListEnrolledCourse, CourseChats, Payment
from rest_framework.routers import SimpleRouter


router = SimpleRouter()


urlpatterns = [
    path('', ListCourse.as_view()),
    path('<int:pk>/', DetailCourse),
    path('<int:pk>/buy', Payment),
    path('categories/', ListCourseCategory.as_view()),
    path('enrolled/', ListEnrolledCourse.as_view()),
    path('<int:pk>/chats/', CourseChats),
]

urlpatterns += router.urls