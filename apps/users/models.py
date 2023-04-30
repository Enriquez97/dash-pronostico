
#from django.contrib.auth.models import User
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User



class TipoUsuario(models.Model):
    
    
    name_tipo_usuario = models.CharField(max_length=50, blank=True,null=True)
    create_tipo_usuario= models.DateTimeField(auto_now_add=True,null=True)
    modified_tipo_usuario = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):

        return self.name_rubro



class Usuario(models.Model):
    #account = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    rubro_empresa=models.ForeignKey(TipoUsuario,on_delete=models.CASCADE)
    #user=models.ForeignKey(User, on_delete=models.CASCADE,default="")
    user =  models.OneToOneField(User,on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    requested_verified = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='media',blank=True,null=True)
    phone = models.CharField(max_length=20, blank=True,null=True)
    create = models.DateTimeField(auto_now_add=True,null=True)
    modified = models.DateTimeField(auto_now=True,null=True)


    def __str__(self):

        return self.username


