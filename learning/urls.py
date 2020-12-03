from django.urls import path
from .views import ListCourse, ListCourseCategory, DetailCourse, DetailCourseUnenroll, ListEnrolledCourse, CourseChats, Payment, PaymentConfirm
from rest_framework.routers import SimpleRouter


router = SimpleRouter()


urlpatterns = [
    path('', ListCourse.as_view()),
    path('<int:pk>/', DetailCourse),
    path('<int:pk>/unenroll/', DetailCourseUnenroll),
    path('<int:pk>/pay/', Payment),
    path('<int:pk>/pay/confirm/', PaymentConfirm),
    path('categories/', ListCourseCategory.as_view()),
    path('enrolled/', ListEnrolledCourse.as_view()),
    path('<int:pk>/chats/', CourseChats),
]

urlpatterns += router.urls