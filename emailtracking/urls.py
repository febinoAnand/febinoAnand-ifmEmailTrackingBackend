from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InboxViewSet, TicketViewSet, EmailIDViewSet, readMailView,ReportViewSet,DepartmentViewSet,SettingViewSet,DashboardStatistics

router = DefaultRouter()
router.register('inbox', InboxViewSet,basename='inbox')
router.register('ticket', TicketViewSet, basename='ticket')
router.register('email_ids', EmailIDViewSet,basename='email_ids')
router.register('reports', ReportViewSet,basename='reports')
router.register('departments', DepartmentViewSet,basename='departments')
router.register('settings', SettingViewSet,basename='emailsettings')
urlpatterns = [
    path('readmail/', readMailView, name='read_mail'),
    path('dashboard/', DashboardStatistics.as_view(), name='dashboard_statistics'),
    path('', include(router.urls)),
]

