# from rest_framework.response import Response
# from rest_framework.exceptions import AuthenticationFailed
# from .serializers import UserSerializer
# from .models import User
# import jwt, datetime
# from rest_framework import status
# from rest_framework import viewsets, pagination


# class RegisterView(viewsets.ModelViewSet):
#     """
#     Create a new user.
#     """

#     queryset = User.objects.none()
#     serializer_class = UserSerializer

#     def create(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# class LoginView(viewsets.ModelViewSet):
#     """
#     User Login.
#     """

#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def login(self, request):
#         """
#         User Login.

#         Returns:
#             {"jwt": token} in json format and in cookie.
#         """
#         email = request.data["email"]
#         password = request.data["password"]

#         user = self.get_queryset().filter(email=email).first()

#         if user is None:
#             raise AuthenticationFailed("User not found!")

#         if not user.check_password(password):
#             raise AuthenticationFailed("Incorrect password!")

#         payload = {
#             "id": user.id,
#             "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=180),
#             "iat": datetime.datetime.utcnow(),
#         }

#         token = jwt.encode(payload, "secret", algorithm="HS256")

#         response = Response()

#         response.set_cookie(key="jwt", value=token, httponly=True)
#         response.data = {"jwt": token}
#         return response


# class UserView(viewsets.ModelViewSet):
#     """
#     Check Authentication and Retrieve User.
#     """

#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def retrieve(self, request):
#         """
#         Retrieve Login User data after checking authentication.
#         """
#         user = request.user
#         serializer = self.serializer_class(user)
#         return Response(serializer.data)


# class LogoutView(viewsets.ModelViewSet):
#     """
#     User Logout and Delete Cookie.
#     """

#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def logout(self, request):
#         """
#         User Logout and Delete Cookie.

#         Note: request body is not required.
#         """
#         response = Response()
#         response.delete_cookie("jwt")
#         response.data = {"message": "success"}
#         return response


# class UserViewSet(viewsets.ModelViewSet):
#     """
#     User CRUD
#     """

#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def list(self, request):
#         """
#         List Users.
#         """

#         user = self.get_queryset()
#         serializer = self.serializer_class(user, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk):
#         """
#         Retrieve user by id.
#         """

#         user = self.get_queryset().filter(id=pk).first()
#         serializer = self.serializer_class(user)
#         return Response(serializer.data)

#     def update(self, request, pk):
#         """
#         Update User.
#         """
#         user = self.get_queryset().filter(id=pk).first()
#         if user is not None:
#             if request.user.id != user.id:
#                 return Response(
#                     "You are not authorized to update this data",
#                     status=status.HTTP_403_FORBIDDEN,
#                 )
#         serializer = self.serializer_class(user, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def destroy(self, request, pk):
#         """
#         Delete User.
#         """
#         user = self.get_queryset().filter(id=pk).first()
#         if user is not None:
#             if request.user.id != user.id:
#                 return Response(
#                     "You are not authorized to delete this user",
#                     status=status.HTTP_403_FORBIDDEN,
#                 )
#         user.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class UserPagination(pagination.PageNumberPagination):
#     """
#     Pagination class for User objects.

#     This class defines the page size for paginated responses.

#     Attributes:
#         page_size (int): The number of users to display per page.
#             Default is 10.
#     """

#     page_size = 10


# class UserSearch(viewsets.ModelViewSet):
#     """
#     Search Users and list them by pagination pages.
#     """

#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     pagination_class = UserPagination

#     def list(self, request, string):
#         """
#         Search users and list them by pagination pages(10 by 10).

#         Note: the input string search can be near from the actual string.
#         """

#         queryset = (
#             self.get_queryset().filter(name__icontains=string)
#             | self.get_queryset().filter(name__trigram_similar=string)
#             | self.get_queryset().filter(name__unaccent=string)
#         )
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)

#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
