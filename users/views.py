from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from .models import User
from .serializers import UserProfileSerializer, AdminUserSerializer
from .permissions import IsOwner, IsAdmin


class ActivateUserView(APIView):
    """
    Handles account activation via email verification link.

    This view is triggered when a user clicks the activation link sent to their email after registration.
    It decodes the user ID from the URL, verifies the token using Django's default_token_generator,
    and activates the user's account if the token is valid.

    URL Format:
        /auth/activate/<uid>/<token>/

    Methods:
        GET: Verifies token and activates the user account if valid.

    Responses:
        200 OK: Account activated successfully.
        400 Bad Request: Invalid or expired activation link.
    """
    def get(self, request, uid, token):
        try:
            uid = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Account activated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Activation link is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)



class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    Allows a user to view, update, or delete their profile.

    - Regular users can only manage their own profile.
    - Admins can manage any user's profile through separate endpoint.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        return self.request.user
    

class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Admin-only viewset for managing all users.

    Admins can:
    - List users
    - Retrieve individual user
    - Update user data
    - Delete users
    - Create new users
    """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]



class LogoutView(APIView):
    """
    Handles secure logout by blacklisting the refresh token.

    The client must send a valid refresh token in the request body.
    Once blacklisted, the refresh token becomes unusable.

    Method: POST
    URL: /auth/logout/

    Returns:
        204 No Content on success
        400 Bad Request if token is missing or invalid
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)