from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpResponse, response, JsonResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic.list import MultipleObjectMixin

from .forms import ChoicesFormSet, ChoiceForm
from .models import Exam
from .models import Question
from .models import Result


class ExamListView(ListView):
    model = Exam
    template_name = 'exams/list.html'
    context_object_name = 'exams'


class ExamDetailView(LoginRequiredMixin, DetailView, MultipleObjectMixin):
    model = Exam
    template_name = 'exams/details.html'
    context_object_name = 'exam'
    pk_url_kwarg = 'uuid'
    paginate_by = 3

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')

        return self.model.objects.get(uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(object_list=self.get_queryset(), **kwargs)
        if context['object_list']:
            max_p = []
            last_start = []
            for i in self.get_queryset():
                max_p.append(i.points())
                last_start.append(i.update_timestamp)
            context['max_points'] = max(max_p)
            context['last_start'] = max(last_start)

        return context

    def get_queryset(self):
        return Result.objects.filter(
            exam=self.get_object(),
            user=self.request.user
        ).order_by('state', '-create_timestamp')


class ExamResultCreateView(LoginRequiredMixin, CreateView):
    def post(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        result = Result.objects.create(
            user=request.user,
            exam=Exam.objects.get(uuid=uuid),
            state=Result.STATE.NEW,
            current_order_number=0
        )

        result.save()

        return HttpResponseRedirect(
            reverse(
                'quiz:question',
                kwargs={
                    'uuid': uuid,
                    'res_uuid': result.uuid,
                    # 'order_num': 1
                }
            )
        )


class ExamResultQuestionView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        # order_num = kwargs.get('order_num')
        result = Result.objects.get(uuid=kwargs.get('res_uuid'))
        question = Question.objects.get(
            exam__uuid=uuid,
            # order_num=order_num
            order_num=result.current_order_number + 1
        )

        choices = ChoicesFormSet(queryset=question.choices.all())


        return render(request, 'exams/question.html', context={'question': question, 'choices': choices})

    def post(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        res_uuid = kwargs.get('res_uuid')
        # order_num = kwargs.get('order_num')
        result = Result.objects.get(uuid=res_uuid)
        question = Question.objects.get(
            exam__uuid=uuid,
            # order_num=order_num
            order_num=result.current_order_number + 1
        )
        choices = ChoicesFormSet(data=request.POST)
        selected_choices = ['is_selected' in form.changed_data for form in choices.forms]
        if sum(selected_choices) == 0 or sum(selected_choices) == len(choices.forms):
            messages.warning(self.request, 'На вопрос есть как минимум один правильный ответ. '
                                           'Все ответы не могут быть правильными!')

            return HttpResponseRedirect(self.request.path_info)
        result.update_result(result.current_order_number + 1, question, selected_choices)

        if result.state == Result.STATE.FINISHED:
            return HttpResponseRedirect(
                reverse(
                    'quiz:result_details',
                    kwargs={
                        'uuid': uuid,
                        'res_uuid': result.uuid

                    },
                )
            )

        return HttpResponseRedirect(
            reverse(
                'quiz:question',
                kwargs={
                    'uuid': uuid,
                    'res_uuid': res_uuid
                    # 'order_num': order_num + 1
                }
            )
        )


class ExamResultDetailView(LoginRequiredMixin, DetailView):
    model = Result
    success_url = reverse_lazy('exams/details.html')
    template_name = 'results/details.html'
    context_object_name = 'result'
    pk_url_kwarg = 'uuid'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('res_uuid')

        return self.get_queryset().get(uuid=uuid)


class ExamResultUpdateView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        res_uuid = kwargs.get('res_uuid')
        user = request.user

        result = Result.objects.get(
            user=user,
            uuid=res_uuid,
            exam__uuid=uuid,
        )

        return HttpResponseRedirect(
            reverse(
                'quiz:question',
                kwargs={
                    'uuid': uuid,
                    'res_uuid': result.uuid,
                    # 'order_num': result.current_order_number + 1
                }
            )
        )


class ExamResultDeleteView(LoginRequiredMixin, DeleteView):
    model = Result

    template_name = 'exams/delete.html'
    context_object_name = 'result'
    pk_url_kwarg = 'uuid'
    success_url = reverse_lazy('quiz:details')

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('res_uuid')

        return self.get_queryset().get(uuid=uuid)

    def get_success_url(self):
        return reverse_lazy('quiz:details', kwargs={'uuid': self.kwargs['uuid']})
