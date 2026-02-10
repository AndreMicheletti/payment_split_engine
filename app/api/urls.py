from rest_framework import routers, serializers, viewsets

router = routers.DefaultRouter()


def register_routes():
    from .views import PaymentsViewSet

    router.register(r"v1", PaymentsViewSet, basename="v1")
    return router
