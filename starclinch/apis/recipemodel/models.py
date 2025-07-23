from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from .choices import *
import random
import uuid
import string
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg 
from django.utils import timezone
# from cloudinary_storage.storage import RawMediaCloudinaryStorage
from datetime import date
from phonenumber_field.modelfields import PhoneNumberField
from io import BytesIO
from datetime import datetime
from cloudinary.models import CloudinaryField
import jwt
import datetime
import pytz
from django.core.exceptions import ValidationError
import requests 
from .choices import *
from .model_manager import *


class CommonTimePicker(models.Model):
    """
    An abstract model in Django that provides two fields, `created_at` and `updated_at`, which automatically record the date and time when an object is created or updated.
    """
    created_at = models.DateTimeField("Created Date", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("Updated Date", auto_now=True, db_index=True)
    class Meta:
        abstract = True



class Country(models.Model):
    """
    Country Model
    """
    name=models.CharField(max_length=100,blank=True,null=True, db_index=True)
    def __str__(self):
       return f"{self.name}"
    class Meta:
        ordering = ['name'] 
    
class State(models.Model):
    """
    State Model
    """
    name=models.CharField(max_length=100,blank=True,null=True, db_index=True)
    country=models.ForeignKey(Country, on_delete=models.CASCADE,related_name='states',db_index=True)
    def __str__(self):
       return f"{self.country}_{self.name}"
    class Meta:
        ordering = ['name'] 
class City(models.Model):
    """
    City Model
    """
    state=models.ForeignKey(State, on_delete=models.CASCADE,related_name='cities',db_index=True)
    name=models.CharField(max_length=100,blank=True,null=True, db_index=True)       
    def __str__(self):
       return f"{self.state}_{self.name}_{self.id}"
    class Meta:
        ordering = ['name'] 



class StarclinchBaseUser(AbstractBaseUser,CommonTimePicker):
    # user Types
    user_type = models.CharField("User Type", max_length=20, default='User', choices=USER_TYPE_CHOICES,db_index=True)
    # user details
    full_name = models.CharField("Name",max_length=255, blank=True, null=True)
    profile_picture = CloudinaryField(
        'Profile Picture',
        folder='media/starclinchuser/profile_pictures/',  
        blank=True,                   
        null=True,                   
        resource_type='image'         
    )
    mobile_number = PhoneNumberField(unique=True,db_index=True)
    countrycode = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField("Email Address", null=False, blank=False, unique=True,db_index=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    custom_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    priority = models.IntegerField(
    choices=[(i, str(i)) for i in range(1, 6)],
    default=5
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False,unique=True)
    gender = models.CharField("Gender", max_length=20, blank=True,choices=USER_GENDER_CHOICES,null=True)
    age = models.CharField("Age",max_length=100, blank=True, null= True)
    dob = models.DateField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='user_city', null=True, blank=True)
    # model flags
    is_superuser = models.BooleanField("Super User", default=False)
    is_mobile_verified = models.BooleanField("Is Mobile Verified",default=False)
    is_active = models.BooleanField("Active", default=True,db_index=True)
    is_staff = models.BooleanField("Staff Member",default=False)
    is_rejected=models.BooleanField("Rejected", default=False,db_index=True)
    is_aproved=models.BooleanField("Aproved", default=False,db_index=True)
    is_blocked = models.BooleanField("Blocked", default=False,db_index=True)
    email_verify = models.BooleanField("Email Verify", default=False)
    login_status = models.BooleanField("Login Status", default=False)
    email_account_otp_verify = models.BooleanField("email account otp Verified", default=False)
    forget_otp_verify = models.BooleanField("forget otp Verified", default=False)
    # other fields
    account_otp = models.CharField('Account OTP', max_length=4, blank=True, null=True)
    forgot_otp = models.CharField('Forgot OTP', max_length=4, blank=True, null=True)
    account_otp_created_at = models.DateTimeField(null=True, blank=True)
    forgot_otp_created_at = models.DateTimeField(null=True, blank=True)
    account_otp_resend_count = models.IntegerField(default=0)
    forgot_otp_resend_count = models.IntegerField(default=0)
    account_last_otp_resend_time = models.DateTimeField(null=True, blank=True)
    forgot_last_otp_resend_time = models.DateTimeField(null=True, blank=True)
    token_valid_after = models.DateTimeField(default=timezone.now,null=True, blank=True)
    # model manager
    objects = StarclinchUserManager()
    # rating 
    USERNAME_FIELD = 'email'
    def calculate_age(self):
        if self.dob:
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None
    def __str__(self):
        return f"{self.id}_{self.user_type}_{self.email}_{self.uuid}" 
    
    def has_perm(self, perm, obj=None):
        return self.is_staff

    def get_mobile_number(self):
        return str(self.mobile_number)
    
    def has_module_perms(self, app_label):
        return self.is_superuser 

    def get_short_name(self):
        return self.email

    def otp_creation(self):
        otp = random.randint(1000, 9999)
        print('models.py ka otp----------->',otp)
        self.otp = otp
        print('models.py ka self.otp----------->',self.otp)
        self.otp_created_at = datetime.now(pytz.utc)  
        self.otp_resend_count = 0
        self.last_otp_resend_time = datetime.now(pytz.utc)  
        self.save()
        return otp
    
    def generate_password(self):
        length = 8  
        characters = string.ascii_letters + string.digits

        password = random.choice(string.ascii_uppercase) + '@'
        password += ''.join(random.choice(characters) for i in range(length-2))
        password_list = list(password)
        random.shuffle(password_list)
        password = ''.join(password_list)

        return password


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.full_name or self.email}")
            unique_slug = base_slug
            num = 1
            while StarclinchBaseUser.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug

        if not self.custom_id:
            while True:
                generated_id = str(random.randint(7000000, 7999999))
                if not StarclinchBaseUser.objects.filter(custom_id=generated_id).exists():
                    self.custom_id = generated_id
                    break

        super().save(*args, **kwargs)
    
    @staticmethod
    def decode_jwt(token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            return StarclinchBaseUser.objects.get(uuid=user_id)
        except (jwt.DecodeError, StarclinchBaseUser.DoesNotExist):
            return None
    
        
    class Meta:
        ordering = ['-id']




class Recipe(CommonTimePicker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    image=CloudinaryField(
        folder='media/sellers/recipe/',  
        blank=True,                   
        null=True,                    
        resource_type='image'         
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="recipes",
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
    )

    is_published = models.BooleanField(default=False, db_index=True)


    def __str__(self):
        creator = self.created_by.full_name if self.created_by else "Unknown Creator"
        return f"Recipe: {self.title} by {creator}"

    

class Rating(CommonTimePicker):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="ratings",
        on_delete=models.SET_NULL,
        null=True,
        db_index=True
    )

    recipe = models.ForeignKey(
        Recipe,
        related_name="ratings",
        on_delete=models.SET_NULL,
        null=True,
        db_index=True
    )

    score = models.PositiveSmallIntegerField()
    review = models.TextField(blank=True, null=True)

    def __str__(self):
        user = self.user if self.user else "Unknown User"
        recipe = self.recipe if self.recipe else "Unknown Recipe"
        return f"{user} rated {recipe} - {self.score}"


