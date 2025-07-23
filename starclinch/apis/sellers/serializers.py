from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apis.recipemodel.models import *
from apis.recipemodel.choices import * 
from datetime import datetime
from starclinch.schedulers.scheduler import *
from apis.recipemodel.celery_tasks import save_resized_image_task
from rest_framework import serializers
from apis.recipemodel.models import Recipe
from django.core.exceptions import ValidationError
from django.db import transaction

class SellerSignupSerializer(serializers.ModelSerializer):
    full_name=serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        error_messages={
            'required': 'Full name is required.',
        }         
    )
    profile_picture=serializers.ImageField(
        required=False,   
        error_messages={
            'invalid_image': 'Invalid image format. Please upload a valid image file.',
        }
    )
    countrycode = serializers.CharField(
        required=False,
        error_messages={
            'required': 'Country code is required.',
            'blank': 'Country code cannot be blank',
        }
    )
    mobile_number=serializers.CharField(
        required=False,
        error_messages={
            'required': 'Mobile number is required.',
            'min_value': 'Mobile number must be at least 10 digits long.',
            'blank': 'Mobile number cannot be blank',
        }      
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=False,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.',
            'blank': 'Email cannot be blank',
        }
    )
    
    password = serializers.CharField(
        required=False,
        allow_blank=False,
        error_messages={
            'required': 'Password is required.',
            'min_length': 'Password must be at least 6 characters long.',
        },
        write_only=True,
        min_length=6  
    )
    confirm_password = serializers.CharField(
        required=False,
        allow_blank=False,
        error_messages={
            'required': 'Confirm Password is required.',
        },
        write_only=True
    )
    age = serializers.IntegerField(
        required=False,
        error_messages={
            'required': 'Age is required.',
            'min_value': 'Age must be a positive integer.',
        },
        min_value=0  
    )
    gender = serializers.ChoiceField(
        choices=USER_GENDER_CHOICES,
        required=False,
        error_messages={
            'required': 'gender is required.',
        },
    )
   
    dob = serializers.DateField(
        required=False,
        error_messages={
            'required': 'Date of Birth is required.',
        }
    )
    address = serializers.CharField(
        required=False,
        error_messages={
            'required': 'Address is required.',
        }
    )
    user_type = serializers.CharField(
        default = 'Seller',
        read_only = True
    )
    uuid = serializers.UUIDField(
        read_only = True
    )
    class Meta:
        model=StarclinchBaseUser
        fields=['full_name','profile_picture','countrycode','mobile_number','email','gender','age','dob','address','user_type','uuid','confirm_password','password']
        
    def validate(self, data):
        countrycode = data.get('countrycode')
        mobile_number = data.get('mobile_number')
        email = data.get('email')


        if StarclinchBaseUser.objects.filter(countrycode="+"+countrycode,mobile_number=mobile_number).exists():
            raise serializers.ValidationError("This mobile number has already been registered.")


        if StarclinchBaseUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email has already been registered.")


        confirm_password = data.get('confirm_password')
        password = data.get('password')
        if password and confirm_password and confirm_password != password:
            raise serializers.ValidationError("The password fields do not match.")

        return data

    def create(self,validated_data):
        
        countrycode = validated_data.get('countrycode', None)

        if countrycode and not countrycode.startswith('+'):
            countrycode = '+' + countrycode
        
        
        user = StarclinchBaseUser.objects.create(
            user_type="Seller",
            full_name=validated_data.get('full_name'),
            countrycode=countrycode,
            mobile_number=str(validated_data.get('mobile_number')),
            email=validated_data.get('email'),
            gender=validated_data.get('gender',None),
            age=validated_data.get('age',None),
            dob=validated_data.get('dob',None),
            address=validated_data.get('address',None),      
        )
        user.set_password(validated_data.get('password'))
        user.is_active=True
        user.email_account_otp_verify=False
        user.save()
        profile_picture_data = validated_data.pop('profile_picture', None)
        if profile_picture_data:
            self.schedule_profile_picture_task(user, profile_picture_data)
        
        
        return user

    def schedule_profile_picture_task(self, user, profile_picture_data):
        # Read profile picture data
        file_data = profile_picture_data.read()
        filename = profile_picture_data.name

        # Schedule task to set profile picture
        create_model_instance_scheduler(
            file_data=file_data,
            filename=filename,
            attribute="profile_picture",
            instance=user
        )
    


class SellerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Invalid email format. Please enter a valid email address.',
            'blank': 'Email cannot be blank',
        }
    )
    password = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Password is required.',
            'blank': 'Password cannot be blank',
        },
        write_only=True
    )

    class Meta:
        fields = ['email', 'password']






class RecipeCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    image = serializers.ImageField(required=False)
    is_published = serializers.BooleanField(default=False)

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty or only whitespace.")
        return value

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        return value

    def create(self, validated_data):
        image_data = validated_data.pop('image', None)
        user = self.context['request'].user

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated.")

        if getattr(user, 'user_type', None) != "Seller":
            raise serializers.ValidationError("Only sellers can create recipes.")

        try:
            with transaction.atomic():
                recipe = Recipe.objects.create(
                    title=validated_data['title'],
                    description=validated_data['description'],
                    is_published=validated_data.get('is_published', False),
                    created_by=user
                )
                if image_data:
                    file_data = image_data.read()
                    filename = image_data.name
                    attribute = "image"  

                    save_resized_image_task.delay(
                        file_data,
                        filename,
                        attribute,
                        recipe.__class__.__name__,
                        str(recipe.id)
                    )

        except Exception as e:
            raise serializers.ValidationError(f"Unexpected error while creating recipe: {str(e)}")

        return recipe





from django.utils.timezone import localtime

class RecipeListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'image_url', 'is_published', 'created_at', 'created_by_name']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_created_by_name(self, obj):
        return obj.created_by.full_name if obj.created_by else None

    def get_created_at(self, obj):
        return localtime(obj.created_at).strftime('%d-%m-%Y %I:%M %p')
    



class RecipeSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        required=False,
        allow_blank=False,
        error_messages={
            'required': 'Title is required.',
            'blank': 'Title cannot be blank.'
        }
    )
    description = serializers.CharField(
        required=False,
        allow_blank=False,
        error_messages={
            'required': 'Description is required.',
            'blank': 'Description cannot be blank.'
        }
    )
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        error_messages={
            'invalid_image': 'Invalid image format. Please upload a valid image file.'
        }
    )
    is_published = serializers.BooleanField(required=False)

    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'image', 'is_published', 'created_by']
        read_only_fields = ['id', 'created_by']

    def get_created_by(self, obj):
        return obj.created_by.full_name if obj.created_by else None

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.is_published = validated_data.get('is_published', instance.is_published)

        image_file = validated_data.get('image', None)
        if image_file:
            file_data = image_file.read()
            filename = image_file.name
            create_model_instance_scheduler(
                file_data=file_data,
                filename=filename,
                attribute='image',
                instance=instance
            )

        instance.save()
        instance.refresh_from_db() 
        return instance


    





    


