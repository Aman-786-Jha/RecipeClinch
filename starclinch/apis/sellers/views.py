
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated, IsAdminUser
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from apis.recipemodel.models import *
from .serializers import *
from drf_yasg import openapi
from django.contrib.auth import authenticate
from rest_framework.exceptions import NotFound
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, permissions
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage





######################### Seller Signup ##################################

# Create your views here.
class SellerSignupView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('full_name', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('profile_picture', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
            openapi.Parameter('countrycode', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, description="Country code e.g. +91"),
            openapi.Parameter('mobile_number', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('gender', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, enum=["Male", "Female", "Other"]),
            openapi.Parameter('age', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('dob', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description="Date of Birth (YYYY-MM-DD)"),
            openapi.Parameter('address', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('password', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('confirm_password', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            201: openapi.Response(description='Created'),
            400: openapi.Response(description='Bad Request'),
            500: openapi.Response(description='Internal Server Error'),
        },
        operation_summary="Create a new Seller user with image uploads",
        operation_description="This endpoint creates a new Seller user. You can upload profile image and form data using multipart/form-data.",
    )
    def post(self, request):
        try:
            serializer = SellerSignupSerializer(data=request.data)
            if serializer.is_valid():
                user_obj = serializer.save()
                return Response(
                    {
                        'responseCode': status.HTTP_201_CREATED,
                        'responseMessage': f"Account Created!",
                        'responseData': {
                            "full_name": user_obj.full_name,
                            "email": user_obj.email,
                            "uuid": user_obj.uuid,
                            "userRole": user_obj.user_type,
                        }
                    },
                    status=status.HTTP_201_CREATED
                )

            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except serializers.ValidationError as e:
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': str(e.detail),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            print("SellerSignUpView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': "Something went wrong",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class SellerLoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=SellerLoginSerializer,
        responses={
            200: openapi.Response(description='OK', schema=SellerLoginSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            401: openapi.Response(description='Unauthorized', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def post(self, request):
        try:
            serializer = SellerLoginSerializer(data=request.data)
            
            if serializer.is_valid():
                email = serializer.validated_data.get('email')
                password = serializer.validated_data.get('password')
                
                if StarclinchBaseUser.objects.filter(email=email).exists():
                    user=StarclinchBaseUser.objects.get(email=email)
                    
                    if user and user.check_password(password) and user.user_type == 'Seller':
                        refresh = RefreshToken.for_user(user)
                        access_token = str(refresh.access_token)
                        refresh_token = str(refresh)
                        user.is_active=True
                        user.login_status=True
                        user.save()
                        return Response(
                            {
                                'responseCode': status.HTTP_200_OK,
                                'responseMessage': "Login successful",
                                'responseData': {
                                    "full_name": user.full_name,
                                    "email": user.email,
                                    "uuid": user.uuid,
                                    'access_token': access_token,
                                    'refresh_token': refresh_token
                                }
                            },
                            status=status.HTTP_200_OK
                        )
                    
                    elif user.user_type != 'Seller':
                        return Response(
                            {
                                'responseCode': status.HTTP_400_BAD_REQUEST,
                                'responseMessage': "You are not allowed to perform this action.",
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    return Response(
                        {
                            'responseCode': status.HTTP_401_UNAUTHORIZED,
                            'responseMessage': "Invalid credentials",
                        },
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                return Response(
                        {
                            'responseCode': status.HTTP_401_UNAUTHORIZED,
                            'responseMessage': "User Is not Valid",
                        },
                        status=status.HTTP_401_UNAUTHORIZED
                    )
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': [f"{error[1][0]}" for error in dict(serializer.errors).items()][0],
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            

        except serializers.ValidationError as e:
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': [f"{error[1][0]}" for error in dict(e).items()][0],
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print("SellerLoginView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': "Something went wrong! Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
         
class SellerUserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                default='Bearer ',
                description='Bearer Token',
            ),
        ],
        responses={
            200: openapi.Response(description='OK'),
            401: openapi.Response(description='Unauthorized', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def post(self, request):
        try:
            user = request.user

            if not user.login_status:
                return Response(
                    {
                        'responseCode': status.HTTP_400_BAD_REQUEST,
                        'responseMessage': "User already logged out",
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


            user.login_status = False
            user.is_active = False
            user.token_valid_after = timezone.now()
            try:
                refresh = RefreshToken.for_user(user)
                refresh.blacklist()
            except Exception as e:
                print("Token revoke error in forgot password -->", e)
            user.save()

            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': "Logout successful",
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print("SellerLogoutView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': "Something went wrong! Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


################# Add Recipe ######################



class RecipeCreateView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                default='Bearer ',
                description='Bearer Token',
            ),
            openapi.Parameter(
                name='title',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description='Recipe Title',
            ),
            openapi.Parameter(
                name='description',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description='Recipe Description',
            ),
            openapi.Parameter(
                name='image',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=False,
                description='Recipe Image (optional)',
            ),
            openapi.Parameter(
                name='is_published',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_BOOLEAN,
                required=False,
                description='Publish immediately? (true/false)',
            ),
        ],
        responses={
            201: openapi.Response(
                description='Recipe created successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            400: openapi.Response(
                description='Validation failed',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            401: openapi.Response(
                description='Unauthorized',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'error': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            )
        },
        operation_summary="Add New Recipe (Seller only)",
        operation_description="Sellers can create recipes with title, description, and optional image.",
    )
    def post(self, request):
        try:
            user = request.user
            if not (
                user.is_authenticated and user.is_active and 
                getattr(user, 'login_status', False) and 
                user.user_type == "Seller"
            ):
                return Response({
                    "responseCode": 401,
                    "responseMessage": "Unauthorized access: Only sellers can create recipes.",
                    "responseData": []
                }, status=status.HTTP_401_UNAUTHORIZED)

            serializer = RecipeCreateSerializer(data=request.data, context={'request': request})
            if not serializer.is_valid():
                return Response({
                    "responseCode": 400,
                    "responseMessage": "Validation error",
                    "responseData": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            recipe = serializer.save(created_by=user)

            return Response({
                "responseCode": 201,
                "responseMessage": "Recipe created successfully",
                "responseData": {
                    "recipe_id": recipe.id,
                    "title": recipe.title,
                    "is_published": recipe.is_published
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("SellerRecipeCreateView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': "Something went wrong",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

################################### Seller recipe list ###########################


class SellerRecipeListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                default='Bearer ',
                description='Bearer Token',
            ),
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Page number"),
            openapi.Parameter(name='size', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Page size"),
        ],
        responses={
            200: openapi.Response(
                description="Recipe list retrieved successfully.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'ResponseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'ResponseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'ResponseBody': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                        'CurrentPage': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'PreviousPage': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                        'NextPage': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                        'TotalPages': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        },
        operation_summary="Seller's Recipe List",
        operation_description="Returns a paginated list of recipes created by the authenticated seller."
    )
    def get(self, request):
        try:
            user = request.user
            if not (
                user.is_authenticated and user.is_active and 
                getattr(user, 'login_status', False) and 
                user.user_type in ["Seller"]
            ):
                return Response({
                    "ResponseCode": 401,
                    "ResponseMessage": "Unauthorized access: Only sellers can create recipes.",
                    "ResponseBody": []
                }, status=status.HTTP_401_UNAUTHORIZED)

            page = int(request.GET.get("page", 1))
            size = int(request.GET.get("size", 10))

            recipes = Recipe.objects.select_related('created_by')\
                .filter(created_by=request.user)\
                .exclude(created_by__isnull=True)\
                .order_by('-created_at')

            paginator = Paginator(recipes, size)

            try:
                paged_data = paginator.page(page)
            except PageNotAnInteger:
                return Response({
                    "ResponseCode": status.HTTP_400_BAD_REQUEST,
                    "ResponseMessage": "Invalid page number.",
                    "ResponseBody": None
                }, status=status.HTTP_400_BAD_REQUEST)
            except EmptyPage:
                return Response({
                    "ResponseCode": status.HTTP_200_OK,
                    "ResponseMessage": "Page not found.",
                    "ResponseBody": [],
                    "CurrentPage": page,
                    "TotalPages": paginator.num_pages,
                    "PreviousPage": None,
                    "NextPage": None,
                }, status=status.HTTP_200_OK)

            serializer = RecipeListSerializer(paged_data, many=True, context={'request': request})

            return Response({
                "ResponseCode": status.HTTP_200_OK,
                "ResponseMessage": "Recipes fetched successfully.",
                "ResponseBody": serializer.data,
                "CurrentPage": page,
                "PreviousPage": paged_data.previous_page_number() if paged_data.has_previous() else None,
                "NextPage": paged_data.next_page_number() if paged_data.has_next() else None,
                "TotalPages": paginator.num_pages,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("SellerRecipeListView Error -->", e)
            return Response({
                "ResponseCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "ResponseMessage": "Internal server error",
                "ResponseBody": {"error": str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################# Recipe detail api view ####################################


class RecipeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get recipe detail by ID",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=False,
                default='Bearer ',
                description='Bearer Token'
            ),
            openapi.Parameter(
                'id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True,
                description='ID of the recipe',
            ),
        ],
        responses={
            200: openapi.Response(
                description='Recipe detail fetched successfully',
                schema=RecipeListSerializer
            ),
            404: openapi.Response(description='Recipe not found'),
            500: openapi.Response(description='Internal Server Error'),
        }
    )
    def get(self, request, id):
        try:
            user = request.user
            print('user------------>', user)
            
            if not (
                user.is_authenticated and user.is_active and 
                getattr(user, 'login_status', False) and 
                user.user_type in ["Seller"]
            ):
                return Response({
                    "responseCode": 401,
                    "responseMessage": "Unauthorized access",
                    "responseData": None
                }, status=status.HTTP_401_UNAUTHORIZED)

            recipe = get_object_or_404(Recipe, id=id)  
            print('recipe.seller-------->',recipe.created_by)
            if recipe.created_by != user:

                return Response({
                    "ResponseCode": status.HTTP_403_FORBIDDEN,
                    "ResponseMessage": "You can only view your own recipes.",
                    "ResponseBody": None
                }, status=status.HTTP_403_FORBIDDEN)
            serializer = RecipeListSerializer(recipe, context={'request': request})

            return Response({
                "responseCode": 200,
                "responseMessage": "Recipe detail fetched successfully.",
                "responseData": serializer.data
            }, status=status.HTTP_200_OK)

        except Recipe.DoesNotExist:
            return Response({
                "responseCode": 404,
                "responseMessage": "Recipe not found",
                "responseData": None
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "responseCode": 500,
                "responseMessage": "Internal Server Error",
                "responseData": {"error": str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################################### recipe update view ########################

class RecipeUpdateAPIView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', in_=openapi.IN_HEADER, type=openapi.TYPE_STRING, required=True, default='Bearer ', description='Bearer Token'),
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
            openapi.Parameter(
                name='is_published',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_BOOLEAN,
                required=False,
                description='Publish immediately? (true/false)',
            ),
        ]
    )
    def put(self, request, recipe_id):
        try:
            user = request.user
            if not (
                user.is_authenticated and 
                user.is_active and 
                getattr(user, 'login_status', False) and 
                user.user_type == "Seller"
            ):
                return Response({
                    "ResponseCode": status.HTTP_403_FORBIDDEN,
                    "ResponseMessage": "Unauthorized access. Only sellers can update their recipes.",
                    "ResponseBody": None
                }, status=status.HTTP_403_FORBIDDEN)

            recipe = get_object_or_404(Recipe, id=recipe_id)

            if recipe.created_by != user:

                return Response({
                    "ResponseCode": status.HTTP_403_FORBIDDEN,
                    "ResponseMessage": "You can only update your own recipes.",
                    "ResponseBody": None
                }, status=status.HTTP_403_FORBIDDEN)
            
            print('reques.data--------->', request.data)

            serializer = RecipeSerializer(recipe, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "ResponseCode": status.HTTP_200_OK,
                    "ResponseMessage": "Recipe updated successfully.",
                    "ResponseBody": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({
                "ResponseCode": status.HTTP_400_BAD_REQUEST,
                "ResponseMessage": "Validation failed.",
                "ResponseBody": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Recipe Update Exception:", str(e))
            return Response({
                "ResponseCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "ResponseMessage": "Something went wrong.",
                "ResponseBody": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###################################### recipe delete view ################################

class RecipeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete - Recipe",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
                default='Bearer '
            ),
            openapi.Parameter(
                'recipe_id',
                openapi.IN_PATH,
                description="UUID of the recipe to delete",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response('Recipe deleted successfully.'),
            403: openapi.Response('Unauthorized access.'),
            404: openapi.Response('Recipe not found.'),
            500: openapi.Response('Internal server error.')
        }
    )
    def delete(self, request, recipe_id):
        try:
            user = request.user
            if not (
                user.is_authenticated
                and user.is_active
                and getattr(user, 'login_status', False)
                and (
                    user.user_type == "Seller"  
                )
            ):
                return Response({
                    'ResponseCode': status.HTTP_403_FORBIDDEN,
                    'ResponseMessage': 'Unauthorized access.',
                    'ResponseBody': None
                }, status=status.HTTP_403_FORBIDDEN)

            recipe = get_object_or_404(Recipe, id=recipe_id)


            if recipe.created_by != user:
                return Response({
                    'ResponseCode': status.HTTP_403_FORBIDDEN,
                    'ResponseMessage': 'You are not allowed to delete this recipe.',
                    'ResponseBody': None
                }, status=status.HTTP_403_FORBIDDEN)

            recipe.delete()

            return Response({
                'ResponseCode': status.HTTP_200_OK,
                'ResponseMessage': 'Recipe deleted successfully.',
                'ResponseBody': None
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("Recipe Delete Error--------------->:", e)
            return Response({
                'ResponseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'ResponseMessage': 'Something went wrong.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
