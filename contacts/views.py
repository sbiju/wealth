import json
from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, TemplateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.db.models import Q

from .mixins import LoginRequiredMixin
from .models import Contact, Meeting
from .forms import MeetForm, ContactForm


@login_required
def meeting_list(request):
    queryset_list = Meeting.objects.filter(user=request.user)
    context = {
        "object_list": queryset_list,
        "title": "List",

    }
    return render(request, "contacts/meeting_list.html", context)


class MeetingDetail(LoginRequiredMixin, DetailView):
    model = Meeting
    queryset = Meeting.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(MeetingDetail, self).get_context_data(*args, **kwargs)
        return context


@login_required
def meeting_create(request):
    form = MeetForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
    }
    return render(request, "contacts/meeting_form.html", context)


class MeetingUpdate(LoginRequiredMixin, UpdateView):
    model = Meeting
    fields = ['title', 'participant', 'notes', 'meeting_date']
    template_name = 'contacts/contact_form.html'


class MeetingDelete(LoginRequiredMixin, DeleteView):
    model = Meeting
    success_url = reverse_lazy('meeting_list')
    template_name = 'contacts/contact_confirm_delete.html'


class HomePageView(TemplateView):
    template_name = "home.html"


def contact_list(request):
    queryset_list = Contact.objects.filter(user=request.user)
    query = request.GET.get("q")
    if query:
        queryset = queryset_list.filter(
            Q(first_name__icontains=query)
        ).distinct()
    paginator = Paginator(queryset_list, 8)  # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)
    context = {
        "object_list": queryset,
        "title": "List",
    }
    return render(request, "contacts/contact_list.html", context)


def search_contact(request):
    query = request.GET.get('term', '')
    queryset = Contact.objects.all().order_by('first_name').filter(
        first_name__istartswith=query).distinct()[:50]
    res = [dict(id=s.pk, label=s.first_name,
                value=s.first_name, url=s.get_absolute_url())
           for s in queryset]
    return HttpResponse(json.dumps(res))


@login_required
def contact_create(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
    }
    return render(request, "contacts/contact_form.html", context)


class ContactUpdate(LoginRequiredMixin, UpdateView):
    model = Contact
    fields = ['first_name', 'last_name', 'job_title', 'email', 'company', 'notes']


class ContactDetail(LoginRequiredMixin, DetailView):
    model = Contact
    queryset = Contact.objects.all()


class ContactDelete(LoginRequiredMixin, DeleteView):
    model = Contact
    success_url = reverse_lazy('contact_list')