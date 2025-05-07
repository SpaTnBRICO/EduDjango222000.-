from django.urls import path
from .import views


urlpatterns = [
    path('',views.home, name="home"),
    path('create_slides/',views.create_slides, name="create_slides"),
    path('manage_slides/',views.manage_slides, name="manage_slides"),
    path('logos/',views.logo, name="logo"),

    path('create_logos/',views.create_logos, name="create_logos"),
    path('deactivate_logo/<int:logo_id>/',views.deactivate_logo, name="deactivate_logo"),
    path('set_active_logo/<int:logo_id>/',views.set_active_logo, name="set_active_logo"),
    path('delete_logo/<int:logo_id>/',views.delete_logo, name="delete_logo"),
    path('news/',views.news, name="news"),
    path('create_news/',views.create_news, name="create_news"),
    path('technews/<int:id>/',views.news_details, name="technews"),
    path('events/',views.events, name="events"),
    path('create_events/',views.create_events, name="create_events"),
    path('blogs/',views.blogs, name="blogs"),
    path('create_blogs/', views.create_blogs, name="create_blogs"),
    path('blog_details/<int:id>/', views.blog_details, name="blog_details"),
    path('contact/us/',views.contact, name="contact"),
    path('email_inbox/',views.email_inbox, name="email_inbox"),
    path('email_compose/',views.email_compose, name="email_compose"),
    path('email_sentbox/',views.email_sentbox, name="email_sentbox"),
    path('email_read/<int:id>/',views.email_read, name="email_read"),
    path('read_messages/',views.read_messages, name="read_messages"),
    path('email_reply/<int:id>/',views.email_reply, name="email_reply"),
    path('email_replies', views.email_replies, name='email_replies'),
    path('departments/',views.view_departments, name="view_departments"),
    path('edit_department/<int:id>/',views.edit_department, name="edit_department"),
    path('delete_department/<int:id>/', views.delete_department, name="delete_department"),
    path('create_course/',views.create_course, name="create_course"),
    path('add_unit/<int:id>/',views.add_unit, name="add_unit"),
    path('edit_course/<int:id>/',views.edit_course, name="edit_course"),
    path('create_department/',views.create_department, name="create_department"),
    path('courses/',views.view_course, name="view_course"),
    path('delete_course/<int:id>/',views.delete_course, name="delete_course"),
    path('techsols/courses/', views.view_cos, name="view_cos"),
    path('techsols/courses/apply/<int:id>/', views.cos_apply, name="cos_apply"),
    path('course_details/<int:course_id>/',views.course_details, name="course_details"),
    path('fee_payment/',views.fee_payment_view, name="fee_payment"),
    path('fee_statement/',views.GenerateFeeStatement, name="fee_statement"),
    path('all_students/',views.all_students, name="all_students"),
    path('student_details/<int:student_id>/',views.student_details, name="student_details"),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('update_student_bio/', views.update_student_bio, name='update_student_bio'),
    #path('payment-receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
    path('payment_receipt/<int:payment_id>/', views.payment_receipt_pdf, name='payment_receipt_pdf'),
    path('g_assignment/',views.g_post_assignment, name="g_post_assignment"),
    path('get-courses/<int:department_id>/', views.get_courses_by_department, name='get_courses_by_department'),
    path('get-levels/<int:course_id>/', views.get_levels_by_course, name='get_levels_by_course'),
    path('view_posted_assignments/', views.view_posted_assignments, name='view_posted_assignments'),
    path('delete_g_assignment/<int:id>/', views.delete_g_assignment, name='delete_gassignment'),
    # URL for creating a note
    path('create-note/', views.create_note, name='create_note'),
    path('notes/', views.view_posted_notes, name='view_posted_notes'),
    path('delete_notes/<int:id>/', views.delete_notes, name='delete_notes'),

    # URL for creating a tutorial
    path('create-tutorial/', views.create_tutorial, name='create_tutorial'),
    path('tutorial/', views.view_posted_tutorials, name='view_posted_tutorials'),
    path('delete_tutorial/<int:id>/', views.delete_tutorial, name='delete_tutorial'),

    #Quizes
    path('quiz_list/', views.quiz_list, name='quiz_list'),  # List of quizzes
    path('create/', views.create_quiz, name='create_quiz'),
    path('add_questions/<int:quiz_id>/', views.add_questions, name='add_questions'),
    path('delete_quiz/<int:id>/', views.delete_quiz, name='delete_quiz'),
    path('take/<int:quiz_id>/', views.take_quiz, name='take_quiz'),  # Take quiz
    path('results/', views.quiz_result, name='quiz_result'),  # View quiz results
    path('result/', views.results, name='results'),

    path('enter_cat_scores/<int:cat_id>/', views.enter_cat_scores, name="marks_entry"),
    path('create_cat/', views.create_cat, name="create_cat"),
    path('ajax/get-units/', views.get_units_by_course, name='get_units_by_course'),
    path('cat_list/', views.cat_list_view, name="cat_list_view"),
    path('cat_results/', views.marks_view, name="marks_view"),
    path('cat_approval/<int:cat_id>/', views.cat_approval, name="cat_approval"),
    path('cat_submission/<int:cat_id>/', views.cat_submission, name="cat_submission"),

    # Edit quiz URL
    path('quiz/edit/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),

    # Edit question URL
    path('question/edit/<int:question_id>/', views.edit_question, name='edit_question'),

    #Mpesa
    path('accesstoken/', views.get_access_token, name='get_access_token'),
    path('stkpush/', views.initiate_stk_push, name='initiate_stk_push'),
    path('query/', views.query_stk_status, name='query_stk_status'),


    


    
]

