from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'departments', DepartmentViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'workplaces', WorkplaceViewSet)
router.register(r'computers', ComputerViewSet)
router.register(r'monitors', MonitorViewSet)
router.register(r'tvs', TVViewSet)
router.register(r'mfps', MFPViewSet)
router.register(r'ups', UPSViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'battery-history', BatteryHistoryViewSet)
router.register(r'global-search', GlobalSearchViewSet, basename='global-search')
router.register(r'cartridges', CartridgeViewSet)
router.register(r'cartridge-movements', CartridgeMovementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]