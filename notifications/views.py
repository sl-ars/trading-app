from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    """ API for managing notifications """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """ Returns unread notifications """
        notifications = self.get_queryset().filter(read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """ Marks all notifications as read """
        self.get_queryset().update(read=True)
        return Response({"message": "All notifications marked as read"})

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request):
        """ Marks all unread notifications as read """
        unread_notifications = Notification.objects.filter(user=request.user, read=False)
        count = unread_notifications.update(read=True)
        return Response({"message": f"{count} notifications marked as read"}, status=status.HTTP_200_OK)