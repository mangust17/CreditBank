from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    TemplateView, ListView, DetailView, 
    CreateView, UpdateView, DeleteView
)
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import (
    User, CreditApplication, Document, 
    CreditHistory, Notification, Report
)
from .forms import (
    UserRegistrationForm, UserLoginForm, 
    CreditApplicationForm, DocumentUploadForm, 
    ReportForm
)
from .mixins import ClientRequiredMixin, ReferrerRequiredMixin, AdminRequiredMixin
from django.contrib.auth import login, logout
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
import os
import mimetypes
import urllib.parse


class IndexView(TemplateView):
    template_name = 'main/index.html'

class UserLoginView(LoginView):
    template_name = 'main/login.html'
    form_class = UserLoginForm
    
    def get_success_url(self):
        user = self.request.user
        if user.role == 'client':
            return reverse_lazy('client_dashboard')
        elif user.role == 'referrer':
            return reverse_lazy('referrer_dashboard')
        elif user.role == 'admin':
            return reverse_lazy('admin_dashboard')
        return reverse_lazy('index')

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        return super().form_invalid(form)

class RegisterView(CreateView):
    template_name = 'main/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

class ClientDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'main/client/dashboard.html'
    
    def test_func(self):
        return self.request.user.role == 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = self.request.user.applications.all()[:5]
        context['notifications'] = self.request.user.notifications.filter(is_read=False)[:5]
        return context

class ClientApplicationCreateView(LoginRequiredMixin, CreateView):
    model = CreditApplication
    form_class = CreditApplicationForm
    template_name = 'main/client/application_form.html'
    success_url = reverse_lazy('client_applications')

    def form_valid(self, form):
        form.instance.client = self.request.user
        response = super().form_valid(form)
        
        files = {
            'passport': ('passport', 'Паспорт'),
            'income': ('income', 'Справка о доходах'),
            'employment': ('employment', 'Справка с места работы')
        }
        
        for field, (doc_type, doc_name) in files.items():
            if self.request.FILES.get(field):
                Document.objects.create(
                    application=self.object,
                    doc_type=doc_type,
                    file=self.request.FILES[field]
                )
        
        messages.success(self.request, 'Заявка успешно создана и отправлена на рассмотрение')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме')
        return super().form_invalid(form)

class ClientApplicationListView(ClientRequiredMixin, ListView):
    model = CreditApplication
    template_name = 'main/client/application_list.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return CreditApplication.objects.filter(client=self.request.user)


class ReferrerDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'main/referrer/dashboard.html'
    
    def test_func(self):
        return self.request.user.role == 'referrer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_applications'] = CreditApplication.objects.filter(status='pending')
        context['reports'] = Report.objects.filter(referrer=self.request.user)[:5]
        return context

class ReferrerApplicationListView(ReferrerRequiredMixin, ListView):
    model = CreditApplication
    template_name = 'main/referrer/application_list.html'
    context_object_name = 'applications'

    def get_queryset(self):
        status = self.request.GET.get('status', '')
        queryset = CreditApplication.objects.all()
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')

class ReferrerApplicationDetailView(LoginRequiredMixin, UpdateView):
    model = CreditApplication
    template_name = 'main/referrer/application_detail.html'
    fields = ['status']
    
    def get_success_url(self):
        return reverse_lazy('referrer_application_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        status = form.cleaned_data['status']
        
        Notification.objects.create(
            user=self.object.client,
            title='Обновление статуса заявки',
            message=f'Статус вашей заявки №{self.object.id} изменен на "{self.object.get_status_display()}"'
        )
        
        messages.success(self.request, 'Статус заявки успешно обновлен')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.documents.all()
        return context

class ReferrerReportCreateView(ReferrerRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'main/referrer/report_form.html'
    success_url = reverse_lazy('referrer_dashboard')

    def form_valid(self, form):
        form.instance.referrer = self.request.user
        return super().form_valid(form)

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'main/admin/dashboard.html'
    
    def test_func(self):
        return self.request.user.role == 'admin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_users'] = User.objects.all().order_by('-date_joined')[:10]
        context['total_users'] = User.objects.count()
        context['total_applications'] = CreditApplication.objects.count()
        context['active_referrers'] = User.objects.filter(role='referrer', is_active=True).count()
        return context

class AdminUserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'main/admin/user_list.html'
    context_object_name = 'users'

class AdminUserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    template_name = 'main/admin/user_form.html'
    fields = ['username', 'email', 'role', 'is_active']
    success_url = reverse_lazy('admin_user_list')


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'main/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 10 

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class DocumentUploadView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentUploadForm
    template_name = 'main/document_upload.html'

    def form_valid(self, form):
        application_id = self.kwargs.get('application_id')
        form.instance.application_id = application_id
        return super().form_valid(form)

@require_POST
def mark_notification_read(request, pk):
    notification = Notification.objects.get(pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'ok'})

@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user).update(is_read=True)
    return JsonResponse({'status': 'ok'})

def user_logout(request):
    logout(request)
    return redirect('login')

def download_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    file_path = document.file.path
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            # Читаем содержимое файла
            file_content = file.read()
            
        # Получаем оригинальное имя файла и кодируем его для URL
        filename = os.path.basename(document.file.name)
        encoded_filename = urllib.parse.quote(filename)
        
        # Создаем response
        response = HttpResponse(file_content)
        
        # Устанавливаем заголовки для принудительного скачивания
        response['Content-Type'] = 'application/force-download'
        response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'
        response['X-Sendfile'] = file_path
        response['Content-Length'] = os.path.getsize(file_path)
        
        # Добавляем заголовки для предотвращения кэширования
        response['Cache-Control'] = 'private'
        response['Pragma'] = 'private'
        response['Expires'] = '0'
        
        return response
    else:
        messages.error(request, 'Файл не найден')
        return redirect('referrer_application_detail', pk=document.application.id)