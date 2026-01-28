from django.urls import path
from.import views

urlpatterns=[
    path('',views.home,name='home'),
    path('login/',views.login_view,name='login'),
    path('signup/',views.signup,name='signup'),
    path('logout/',views.logout_view,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('analysis/<int:analysis_id>/',views.analysis_detail,name='analysis_detail'),
    path('analysis-history/',views.analysis_history,name='analysis_history'),
    path('delete-analysis/<int:analysis_id>/',views.delete_analysis,name='delete_analysis'),
]