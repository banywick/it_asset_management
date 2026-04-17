from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'workplaces', WorkplaceViewSet)
router.register(r'computers', ComputerViewSet)
router.register(r'monitors', MonitorViewSet)
router.register(r'tvs', TVViewSet)
router.register(r'mfps', MFPViewSet)
router.register(r'ups', UPSViewSet)
router.register(r'locations', LocationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]