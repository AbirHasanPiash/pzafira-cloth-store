from rest_framework import viewsets, permissions
from .models import Address
from .serializers import AddressSerializer

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only access their own addresses
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Assign the logged-in user to the address
        serializer.save(user=self.request.user)