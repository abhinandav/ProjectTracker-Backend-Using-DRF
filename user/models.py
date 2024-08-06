from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager


class MyAccountManager(BaseUserManager):
    def create_user(self,username,email,password=None):
        if not email:
            raise ValueError('User must have a email address')
            
        user = self.model(
            email = self.normalize_email(email),
            username = username,
        )
        user.set_password(password)
        user.save(using=self._db)  
        return user
    
    def create_superuser(self,username,email,password):
        user = self.create_user(email=self.normalize_email(email),
                                username=username,
                                password=password,
                                )
        user.is_active = True
        user.is_superuser = True
        user.is_email_verified = True
        user.is_staff = True
        
        user.save(using=self._db)
        return user
            

class User(AbstractBaseUser):
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100,unique=True)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = MyAccountManager()
    
    def __str__(self):
        return self.username
    
    def has_perm(self,perm,obj=None):
        return self.is_superuser
    
    def has_module_perms(self,add_label):
        return True
    

class Project(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  
    created_date = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return self.title
    

class Todo(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed')
    ]

    id = models.AutoField(primary_key=True) 
    description = models.TextField()  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending') 
    created_date = models.DateField(auto_now_add=True)  
    updated_date = models.DateTimeField(auto_now=True)  
    project = models.ForeignKey(Project, related_name='todos', on_delete=models.CASCADE)  

    def __str__(self):
        return f"{self.description} of {self.project.title}"




