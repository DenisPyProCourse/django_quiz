from django.urls import path

from quiz.views import ExamListView, ExamDetailView, ExamResultCreateView, ExamResultDetailView, ExamResultQuestionView, \
    ExamResultUpdateView, ExamResultDeleteView

app_name = 'quiz'

urlpatterns = [
    path('', ExamListView.as_view(), name='list'),
    path('<uuid:uuid>/', ExamDetailView.as_view(), name='details'),
    path('<uuid:uuid>/result/create/', ExamResultCreateView.as_view(), name='result_create'),
    path('<uuid:uuid>/result/<uuid:res_uuid>/details/', ExamResultDetailView.as_view(), name='result_details'),
    path('<uuid:uuid>/result/<uuid:res_uuid>/update/', ExamResultUpdateView.as_view(), name='result_update'),
    path('<uuid:uuid>/result/<uuid:res_uuid>/question/<int:order_num>/', ExamResultQuestionView.as_view(),
         name='question'),
    path('<uuid:uuid>/result/<uuid:res_uuid>/delete/', ExamResultDeleteView.as_view(), name='result_delete'),
]