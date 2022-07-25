from django import forms
from django.core.exceptions import ValidationError

from quiz.models import Choice


class QuestionInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        if not (self.instance.QUESTION_MIN_LIMIT <= len(self.forms) <= self.instance.QUESTION_MAX_LIMIT):
            raise ValidationError(
                f'Кол-во вопросов должно быть в диапазоне '
                f'от {self.instance.QUESTION_MIN_LIMIT} '
                f'до {self.instance.QUESTION_MAX_LIMIT}'
            )
        lst = []
        for form in self.forms:
            lst.append(form.cleaned_data['order_num'])
        if lst[0] != 1:
            raise ValidationError(f'Нумерация вопросов должна начинаться с "1".')
        for i in range(len(lst)):
            if (lst[i] - lst[i - 1]) > 1:
                raise ValidationError(f'Список должен быть упорядочен с шагом в "1"')
            elif lst[-1] > self.instance.QUESTION_MAX_LIMIT:
                raise ValidationError(f'Количество вопросов не может быть больше {self.instance.QUESTION_MAX_LIMIT}')
        # for form in self.forms:
        #     print(form.cleaned_data['text'], form.cleaned_data['order_num'])


class ChoiceInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        # lst = []
        # for form in self.forms:
        #     if form.cleaned_data['is_correct']:
        #         lst.append(1)
        #     else:
        #         lst.append(0)

        num_correct_answers = sum(form.cleaned_data['is_correct'] for form in self.forms)
        # num_correct_answers = sum(lst)

        # num_correct_answers = sum(1 for form in self.forms if form.cleaned_data['is_correct'])

        if num_correct_answers == 0:
            raise ValidationError('Необходимо выбрать как минимум 1 вариант.')

        if num_correct_answers == len(self.forms):
            raise ValidationError('НЕ разрешено выбирать все варианты')

class ChoiceForm(forms.ModelForm):
    is_selected = forms.BooleanField(required=False)

    class Meta:
        model = Choice
        fields = ['text']



ChoicesFormSet = forms.modelformset_factory(
    model=Choice,
    form=ChoiceForm,
    extra=0)

