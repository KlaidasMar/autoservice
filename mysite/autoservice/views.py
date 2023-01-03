from django.shortcuts import (render,
                              get_object_or_404,
                              reverse,
                              redirect)
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.views.generic.edit import FormMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import (Paslauga,
                     Uzsakymas,
                     Automobilis,
                     UzsakymoEilute)
from .forms import (UzsakymoKomentarasForm,
                    UserUpdateForm,
                    ProfileUpdateForm,
                    MyUzsakymasCreateForm)


# Create your views here.
def index(request):
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    kontekstas = {
        'paslaugu_kiekis': Paslauga.objects.all().count(),
        'atliktu_uzsakymu_kiekis': Uzsakymas.objects.filter(statusas__exact='i').count(),
        'automobiliu_kiekis': Automobilis.objects.all().count(),
        'num_visits': num_visits,
    }
    return render(request, 'index.html', context=kontekstas)


def automobiliai(request):
    paginator = Paginator(Automobilis.objects.all(), 3)
    page_number = request.GET.get('page')
    puslapiuoti_automobiliai = paginator.get_page(page_number)
    kontekstas = {
        'automobiliai': puslapiuoti_automobiliai,
    }
    return render(request, 'automobiliai.html', context=kontekstas)


def automobilis(request, automobilis_id):
    kontekstas = {
        'automobilis': get_object_or_404(Automobilis, pk=automobilis_id)
    }
    return render(request, 'automobilis.html', context=kontekstas)


def search(request):
    query = request.GET.get('query')
    search_results = Automobilis.objects.filter(
        Q(kliento_vardas__icontains=query) | Q(modelis__gamintojas__icontains=query) | Q(
            modelis__modelis__icontains=query) | Q(valstybinis_nr__icontains=query) | Q(vin_kodas__icontains=query))
    return render(request, 'search.html', {'automobiliai': search_results, 'query': query})


@csrf_protect
def register(request):
    if request.method == "POST":
        # pasiimame reikšmes iš registracijos formos
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        # tikriname, ar sutampa slaptažodžiai
        if password == password2:
            # tikriname, ar neužimtas username
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Vartotojo vardas {username} užimtas!')
                return redirect('register')
            else:
                # tikriname, ar nėra tokio pat email
                if User.objects.filter(email=email).exists():
                    messages.error(request, f'Vartotojas su el. paštu {email} jau užregistruotas!')
                    return redirect('register')
                else:
                    # jeigu viskas tvarkoje, sukuriame naują vartotoją
                    User.objects.create_user(username=username, email=email, password=password)
                    messages.info(request, f'Vartotojas {username} užregistruotas!')
                    return redirect('login')
        else:
            messages.error(request, 'Slaptažodžiai nesutampa!')
            return redirect('register')
    return render(request, 'registration/register.html')


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.info(request, f"Profilis atnaujintas")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'profile.html', context)


class UzsakymasListView(generic.ListView):
    model = Uzsakymas
    paginate_by = 4


class UzsakymasDetailView(generic.DetailView, FormMixin):
    model = Uzsakymas
    form_class = UzsakymoKomentarasForm

    def get_success_url(self):
        return reverse('uzsakymas', kwargs={'pk': self.object.id})

    # standartinis post metodo perrašymas, naudojant FormMixin, galite kopijuoti tiesiai į savo projektą.
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.uzsakymas = self.object
        form.instance.vartotojas = self.request.user
        form.save()
        return super().form_valid(form)


class MyUzsakymasListView(LoginRequiredMixin, generic.ListView):
    model = Uzsakymas
    paginate_by = 4

    def get_queryset(self):
        return Uzsakymas.objects.filter(vartotojas=self.request.user)


class MyUzsakymasCreateView(LoginRequiredMixin, generic.CreateView):
    model = Uzsakymas
    # fields = ['automobilis', 'terminas']
    success_url = '/autoservice/manouzsakymai/'
    template_name = 'manouzsakymas_form.html'
    form_class = MyUzsakymasCreateForm

    def form_valid(self, form):
        form.instance.vartotojas = self.request.user
        form.save()
        return super().form_valid(form)


class MyUzsakymasUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Uzsakymas
    fields = ['automobilis', 'terminas']
    success_url = '/autoservice/manouzsakymai/'
    template_name = 'manouzsakymas_form.html'

    # form_class = MyUzsakymasCreateForm

    def form_valid(self, form):
        form.instance.vartotojas = self.request.user
        form.save()
        return super().form_valid(form)

    def test_func(self):
        uzsakymas = self.get_object()
        return self.request.user == uzsakymas.vartotojas


class MyUzsakymasDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Uzsakymas
    success_url = '/autoservice/manouzsakymai/'
    template_name = "manouzsakymas_delete.html"

    def test_func(self):
        uzsakymas = self.get_object()
        return self.request.user == uzsakymas.vartotojas


class MyUzsakymoEiluteCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = UzsakymoEilute
    fields = ['paslauga', 'kiekis']
    template_name = 'uzsakymoeilute_form.html'

    def get_success_url(self):
        return reverse('uzsakymas', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        form.instance.uzsakymas = Uzsakymas.objects.get(pk=self.kwargs['pk'])
        form.save()
        return super().form_valid(form)

    def test_func(self):
        uzsakymas = Uzsakymas.objects.get(pk=self.kwargs['pk'])
        atsakymas = self.request.user == uzsakymas.vartotojas
        return atsakymas


class MyUzsakymoEiluteDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = UzsakymoEilute
    template_name = "uzsakymoeilute_delete.html"

    def get_success_url(self):
        return reverse('uzsakymas', kwargs={'pk': self.kwargs['pk2']})

    def test_func(self):
        uzsakymas = Uzsakymas.objects.get(pk=self.kwargs['pk2'])
        atsakymas = self.request.user == uzsakymas.vartotojas
        return atsakymas


class MyUzsakymoEiluteUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = UzsakymoEilute
    fields = ['paslauga', 'kiekis']
    template_name = 'uzsakymoeilute_form.html'

    def get_success_url(self):
        return reverse('uzsakymas', kwargs={'pk': self.kwargs['pk2']})

    def form_valid(self, form):
        form.instance.uzsakymas = Uzsakymas.objects.get(pk=self.kwargs['pk2'])
        form.save()
        return super().form_valid(form)

    def test_func(self):
        uzsakymas = Uzsakymas.objects.get(pk=self.kwargs['pk2'])
        atsakymas = self.request.user == uzsakymas.vartotojas
        return atsakymas