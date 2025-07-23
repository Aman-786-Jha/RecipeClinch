
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from apis.recipemodel.models import *
from .serializers import *
from drf_yasg import openapi
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .serializers import CustomerRecipeListSerializer





######################### Customer Signup ##################################

# Create your views here.
class CustomerSignupView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('full_name', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('profile_picture', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
            openapi.Parameter('countrycode', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, description="E.g. +91"),
            openapi.Parameter('mobile_number', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('gender', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, enum=["Male", "Female", "Other"]),
            openapi.Parameter('age', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('dob', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description="Date of Birth (YYYY-MM-DD)"),
            openapi.Parameter('address', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('confirm_password', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('password', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            201: openapi.Response(description='Created', schema=CustomerSignupSerializer),
            400: openapi.Response(description='Bad Request'),
            500: openapi.Response(description='Internal Server Error'),
        },
        operation_summary="Create a new Customer user with image upload",
        operation_description="Create a new Customer user and upload profile picture via multipart form-data.",
    )
    def post(self, request):
        try:
            serializer = CustomerSignupSerializer(data=request.data)
            if serializer.is_valid():
                user_obj = serializer.save()
                return Response({
                    'responseCode': status.HTTP_201_CREATED,
                    'responseMessage': "Account Created!",
                    'responseData': {
                        "full_name": user_obj.full_name,
                        "email": user_obj.email,
                        "uuid": user_obj.uuid,
                        "userRole": user_obj.user_type,
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("CustomerSignUpView Error -->", e)
            return Response({
                'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'responseMessage': "Something went wrong",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################## Customer Login ################################


class CustomerLoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=CustomerLoginSerializer,
        responses={
            200: openapi.Response(description='OK', schema=CustomerLoginSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            401: openapi.Response(description='Unauthorized', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def post(self, request):
        try:
            serializer = CustomerLoginSerializer(data=request.data)
            
            if serializer.is_valid():
                email = serializer.validated_data.get('email')
                password = serializer.validated_data.get('password')
                
                if StarclinchBaseUser.objects.filter(email=email).exists():
                    user=StarclinchBaseUser.objects.get(email=email)
                    
                    if user and user.check_password(password) and user.user_type == 'Customer':
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
                    
                    elif user.user_type != 'Customer':
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
            print("CustomerLoginView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': "Something went wrong! Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

##################################### Customer Logout #########################
         
class CustomerUserLogoutView(APIView):
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
            print("CustomerLogoutView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': "Something went wrong! Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

####################################### Customer recipe list #############################
        

class CustomerRecipeListView(APIView):
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
        operation_summary="Customer - Recipe List",
        operation_description="Returns a paginated list of all published recipes created by sellers."
    )
    def get(self, request):
        try:
            user = request.user
            if not (
                user.is_authenticated and user.is_active and 
                getattr(user, 'login_status', False) and 
                user.user_type == "Customer"
            ):
                return Response({
                    "ResponseCode": 401,
                    "ResponseMessage": "Unauthorized access: Only customers can access this recipe list.",
                    "ResponseBody": None
                }, status=status.HTTP_401_UNAUTHORIZED)

            page = int(request.GET.get("page", 1))
            size = int(request.GET.get("size", 10))

            recipes = Recipe.objects.select_related('created_by')\
                .filter(
                    is_published=True,
                    created_by__user_type="Seller"
                )\
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

            serializer = CustomerRecipeListSerializer(paged_data, many=True, context={'request': request})

            return Response({
                "ResponseCode": status.HTTP_200_OK,
                "ResponseMessage": "Published recipes fetched successfully.",
                "ResponseBody": serializer.data,
                "CurrentPage": page,
                "PreviousPage": paged_data.previous_page_number() if paged_data.has_previous() else None,
                "NextPage": paged_data.next_page_number() if paged_data.has_next() else None,
                "TotalPages": paginator.num_pages,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("CustomerRecipeListView Error -->", e)
            return Response({
                "ResponseCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "ResponseMessage": "Internal server error",
                "ResponseBody": {"error": str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


####################################### Customer recipe detail ########################################

class RecipeDetailCustomerView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Customer view of a published recipe by ID",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                default='Bearer ',
                description='Bearer Token'
            ),
            openapi.Parameter(
                'id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True,
                description='ID of the recipe'
            )
        ],
        responses={
            200: openapi.Response(
                description='Published recipe detail fetched successfully',
                schema=CustomerRecipeListSerializer
            ),
            401: openapi.Response(description='Unauthorized'),
            403: openapi.Response(description='Recipe is not published or missing seller'),
            404: openapi.Response(description='Recipe not found'),
            500: openapi.Response(description='Internal server error')
        }
    )
    def get(self, request, id):
        user = request.user

        if not (user.is_authenticated and user.is_active and 
                getattr(user, 'login_status', False) and 
                user.user_type == "Customer"):
            return Response({
                "responseCode": 401,
                "responseMessage": "Unauthorized access",
                "responseData": None
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Use select_related for performance
            # recipe = get_object_or_404(
            #     Recipe.objects.select_related('created_by'),
            #     id=id,
            #     is_published=True
            # )

            recipe = get_object_or_404(
                Recipe.objects.select_related('created_by').filter(
                    is_published=True,
                    created_by__isnull=False,
                    created_by__user_type="Seller"
                ),
                id=id
            )
            if not recipe:
                return Response({
                    "responseCode": 403,
                    "responseMessage": "Recipe does not have a valid seller.",
                    "responseData": None
                }, status=status.HTTP_403_FORBIDDEN)

            # if not recipe.created_by:
            #     return Response({
            #         "responseCode": 403,
            #         "responseMessage": "Recipe does not have a valid seller.",
            #         "responseData": None
            #     }, status=status.HTTP_403_FORBIDDEN)

            serializer = CustomerRecipeListSerializer(recipe, context={'request': request})
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
        


###############################  Customer rating recipe api ############################

class RateRecipeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                default='Bearer ',
                description='Bearer Token'
            ),
            openapi.Parameter(
                'id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True,
                description='ID of the recipe'
            )
        ],
        operation_description="Rate a recipe (Customer only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["score"],
            properties={
                "score": openapi.Schema(type=openapi.TYPE_INTEGER, minimum=1, maximum=5, example=4),
                "review": openapi.Schema(type=openapi.TYPE_STRING, example="Loved the taste!"),
            },
        ),
        responses={
            200: openapi.Response("Rating added/updated successfully"),
            400: openapi.Response("Bad request"),
            403: openapi.Response("Only customers can rate"),
            404: openapi.Response("Recipe not found"),
            500: openapi.Response("Internal server error"),
        },
    )
    def post(self, request, id):
        try:
            user = request.user
            if user.user_type != 'Customer':
                return Response({
                    "responseCode": 403,
                    "responseMessage": "Only customers are allowed to rate recipes.",
                    "responseData": None
                }, status=status.HTTP_403_FORBIDDEN)


            try:
                recipe = Recipe.objects.select_related('created_by').filter(
                    id=id,
                    is_published=True,
                    created_by__isnull=False,
                    created_by__user_type='Seller'
                ).first()
                if not recipe:
                    raise Recipe.DoesNotExist
            except Recipe.DoesNotExist:
                return Response({
                    "responseCode": 404,
                    "responseMessage": "Recipe not found or not allowed for rating.",
                    "responseData": None
                }, status=status.HTTP_404_NOT_FOUND)

            score = request.data.get('score')
            if not isinstance(score, int) or score < 1 or score > 5:
                return Response({
                    "responseCode": 400,
                    "responseMessage": "Score must be an integer between 1 and 5.",
                    "responseData": None
                }, status=status.HTTP_400_BAD_REQUEST)

            review = request.data.get('review', '')

            rating, created = Rating.objects.update_or_create(
                user=user,
                recipe=recipe,
                defaults={'score': score, 'review': review}
            )

            serializer = RatingSerializer(rating)

            return Response({
                "responseCode": 200,
                "responseMessage": "Recipe rated successfully",
                "responseData": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "responseCode": 500,
                "responseMessage": "Internal Server Error",
                "responseData": {"error": str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



################################ All customers recipe rating detail list ###############

from .serializers import RatingSerializer

class CustomerRatingListView(APIView):
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
                description="Customer rating list retrieved successfully.",
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
            401: "Unauthorized",
            500: "Internal Server Error"
        },
        operation_summary="Customer - Rating List",
        operation_description="Returns a paginated list of all ratings made by the authenticated customer."
    )
    def get(self, request):
        try:
            user = request.user
            if not (
                user.is_authenticated and user.is_active and
                getattr(user, 'login_status', False) and
                user.user_type == "Customer"
            ):
                return Response({
                    "ResponseCode": 401,
                    "ResponseMessage": "Unauthorized access: Only customers can access their ratings.",
                    "ResponseBody": None
                }, status=status.HTTP_401_UNAUTHORIZED)

            page = int(request.GET.get("page", 1))
            size = int(request.GET.get("size", 10))

            ratings = Rating.objects.select_related("recipe", "user", "recipe__created_by") \
                .filter(user=user).order_by('-created_at')

            paginator = Paginator(ratings, size)

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

            serializer = RatingSerializer(paged_data, many=True, context={'request': request})

            return Response({
                "ResponseCode": status.HTTP_200_OK,
                "ResponseMessage": "Customer ratings fetched successfully.",
                "ResponseBody": serializer.data,
                "CurrentPage": page,
                "PreviousPage": paged_data.previous_page_number() if paged_data.has_previous() else None,
                "NextPage": paged_data.next_page_number() if paged_data.has_next() else None,
                "TotalPages": paginator.num_pages,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "ResponseCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "ResponseMessage": "Internal server error",
                "ResponseBody": {"error": str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
