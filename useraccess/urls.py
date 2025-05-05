from django.urls import path
from . import views



urlpatterns = [
    path('signin/', views.user_login, name="signin"),
    path('otp/', views.otp_view, name="otp"),
    path('signout/', views.user_logout, name="signout"),
    path('signup/', views.user_register, name="create_account"),
    path('otp_view_activate_account/', views.otp_view_activate_account, name="otp_view_activate_account"),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('password_reset_done/', views.password_reset_done, name='password_reset_done'),
    path('set_new_password/<uidb64>/<token>/', views.set_new_password, name='set_new_password'),
    path('userprofile/', views.user_profile, name='user_profile'),  # URL to view the profile
    path('userprofile/edit/', views.edit_user_profile, name='edit_user_profile'),  # URL to edit the profile
    path('profile', views.profile, name='profile'),
    path('profile_csv', views.profile_csv, name='profile_csv'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('update_user/<id>/', views.update_user, name='update_user'),
    path('delete_user/<id>/', views.delete_user, name='delete_user'),
    path('deactivate_user/<id>/', views.deactivate_user, name='deactivate_user'),
    path('activate_user/<id>/', views.activate_user, name='activate_user'),
    path('techusers/', views.ShowUsers, name="ShowUsers"),
    path('view_full_profile/<int:id>/', views.view_full_profile, name="view_full_profile"),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('confirm_letter/', views.confirm_letter, name='confirm_letter'),
    path('letter_csv', views.letter_csv, name='letter_csv'),

    #########
    # View for applying to a course
    path('apply/', views.apply_for_course, name='apply_for_course'),
    # These are the dynamic routes for fetching courses and levels
    path('get-courses/<int:department_id>/', views.get_courses_by_department, name='get_courses'),
    path('get-levels/<int:course_id>/', views.get_levels_by_course, name='get_levels'),
    
    path('add_teacher/', views.add_teacher, name='add_teacher'),
    
    # View for successful application submission
    path('apply/success/', views.apply_success, name='apply_success'),

    # Account activation URL (used for email confirmation)
    #path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),

    path('activate/<uidb64>/<token>/', views.ActivateAccountView.as_view(), name='activate_account'),

    # Student Dashboard (only accessible after login)
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('baseadmin/', views.baseadmin, name='baseadmin'),

]