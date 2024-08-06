from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import *
from .models import *
from .email import send_otp_via_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate,logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics







class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=email, password=password)

        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        elif not user.is_active:
            return Response({'error': 'Blocked'}, status=status.HTTP_403_FORBIDDEN)
        
         
        else:
            if not user.is_staff:
                refresh = RefreshToken.for_user(user)
                refresh['username'] = str(user.username)

                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                content = {
                    'userid':user.id,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'isAdmin': user.is_superuser,
                    # 'isActive':user.is_active
                }
                return Response(content, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'This account is not a user account'}, status=status.HTTP_401_UNAUTHORIZED) 


class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                
                user = serializer.save(is_active=False) 
       
                send_otp_via_mail(user.email, user.otp)
                response_data = {
                    'message': 'OTP sent successfully.',
                    'email': user.email  
                }
                return Response(response_data, status=status.HTTP_200_OK)
            
            except Exception as e:
                print(f"Error during user registration: {e}")
                return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(APIView):
    def post(self, request):
        print('register working')
        serializer = OTPVerificationSerializer(data=request.data)
        print(serializer)
        
        if serializer.is_valid():
            print('valid serializer')
            try:
                email = serializer.validated_data.get('email')
                entered_otp = serializer.validated_data.get('otp')
                
                user = User.objects.get(email=email )
                print(user)
                
                if user.otp == entered_otp:
                    print('valid otp')
                    user.is_active = True
                    user.save()
                    return Response({'message': 'User registered and verified successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid OTP,Please Check your email and Verify'}, status=status.HTTP_400_BAD_REQUEST)
                
            except User.DoesNotExist:
                return Response({'error': 'User not found or already verified'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                print(f"Error during OTP verification: {e}")
                return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetails(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        print(user.is_superuser)
        data = UserSerializer(user).data
        content = data
        return Response(content)


class LogoutView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

class ProjectListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateProjectSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProjectDetailView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        project_id = self.kwargs['project_id']
        return generics.get_object_or_404(Project, id=project_id)


class DeleteProjectView(generics.DestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            project = self.get_object()
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

class EditProjectView(generics.UpdateAPIView):
    queryset=Project.objects.all()
    permission_classes=[IsAuthenticated]
    serializer_class=ProjectSerializer

    def update(self, request, *args, **kwargs):
        try:
            project_id=request.data.get('id')
            title=request.data.get('title')
            if not project_id or not title:
                return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
            
            project=Project.objects.get(id=project_id)
            project.title=title
            project.save()

            return Response({'message':'renamed project suceessfully'},status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateTodoView(generics.CreateAPIView):
    serializer_class = TodoSerializer


class PendingTodoListView(generics.ListAPIView):
    serializer_class = TodoSerializer

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Todo.objects.filter(project_id=project_id, status='Pending').order_by('-created_date')


class CompletedTodoListView(generics.ListAPIView):
    serializer_class = TodoSerializer

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Todo.objects.filter(project_id=project_id, status='Completed')
        # return Response({'todo':Todo.objects.filter(project_id=project_id, status='Completed'),'title':Project.objects.filter(id=project_id)})


class UpdateTodoStatusView(APIView):
    def post(self, request, todo_id):
        try:
            todo = Todo.objects.get(id=todo_id)
            todo.status = 'Completed' if todo.status == 'Pending' else 'Pending'
            todo.save()
            return Response(TodoSerializer(todo).data, status=status.HTTP_200_OK)
        except Todo.DoesNotExist:
            return Response({"error": "Todo not found"}, status=status.HTTP_404_NOT_FOUND)


class DeleteTodoView(generics.DestroyAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            todo = self.get_object()
            todo.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Todo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class EditTodoView(generics.UpdateAPIView):
    queryset=Todo.objects.all()
    permission_classes=[IsAuthenticated]
    serializer_class=TodoSerializer

    def update(self, request, *args, **kwargs):
        try:
            todo_id=request.data.get('id')
            print('id',todo_id)
            text=request.data.get('text')
            print(text)
            if not todo_id or not text:
                return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
            
            todo=Todo.objects.get(id=todo_id)
            print('sss',todo)
            todo.description=text
            todo.save()

            return Response({'message':'renamed todo suceessfully'},status=status.HTTP_200_OK)
        except Todo.DoesNotExist:
            return Response({'error': 'todo not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




























# from social_django.utils import load_strategy, psa
# from django.shortcuts import redirect
# from django.contrib.auth import login

# @psa('social:complete')
# def google_login(request):
#     token = request.data.get('token')
#     try:
#         user = request.backend.do_auth(token)
#         if user:
#             # Log the user in
#             login(request, user)
#             return redirect('/success/')
#     except Exception as e:
#         print(f"Error during Google authentication: {e}")
#     return redirect('/error/')