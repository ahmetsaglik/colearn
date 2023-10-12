from django.urls import path, include
from django.contrib.auth import views as auth_views
from account.views import (
    registration_view,
    logout_view,
    login_view,
    account_view,
    delete_account_view,
    must_authenticate_view,
    edit_account_view,
)

urlpatterns = [
    path('register/', registration_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('login/', login_view, name='login'),
    path('account/<user_id>', account_view, name='account'),
    path('account/edit/<user_id>', edit_account_view, name='edit-account'),
    path('account/edit/<user_id>/cropImage', edit_account_view, name='crop-image'),
    path('delete-account/', delete_account_view, name='delete-account'),
    path('must-authenticate/', must_authenticate_view, name='must-authenticate'),

    # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_reset/password_change_done.html'), 
        name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_reset/password_change.html'), 
        name='password_change'),

    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_done.html'),
     name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset/password_reset_form.html'), name='password_reset'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_complete.html'),
     name='password_reset_complete'),
]
