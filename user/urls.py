from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(serializer_class=MyTokenObtainPairSerializer), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('register/',UserRegisterView.as_view(),name='register'),
    path('otp/',OTPVerificationView.as_view(),name='otp'),
    path('login/',LoginView.as_view(),name='otp'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('user-details/',UserDetails.as_view(),name='user-details'),

    path('addproject/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('project/<int:project_id>/todos/add/', CreateTodoView.as_view(), name='create-todo'),
    path('project-detail/<int:project_id>/', ProjectDetailView.as_view(), name='project-detail'),
    path('delete-project/<int:pk>/', DeleteProjectView.as_view(), name='delete-project'),
    path('edit-project/', EditProjectView.as_view(), name='edit_project'),


    path('todo-status/<int:todo_id>/', UpdateTodoStatusView.as_view(), name='todo-status'),
    path('project/<int:project_id>/todos/pending/', PendingTodoListView.as_view(), name='pending-todo-list'),
    path('project/<int:project_id>/todos/completed/', CompletedTodoListView.as_view(), name='completed-todo-list'),
    path('delete-todo/<int:pk>/', DeleteTodoView.as_view(), name='delete-todo'),
    path('edit-todo/', EditTodoView.as_view(), name='edit-todo'),


]
