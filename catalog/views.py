from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from catalog.forms import RenewBookModelForm
from django.contrib.auth.decorators import permission_required
import datetime
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.models import Author

class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    fields = '__all__'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    fields = '__all__'

class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    success_url = reverse_lazy('books')

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    # The 'all()' is implied by default.    
    num_authors = Author.objects.count()
    context = {
    'num_books': num_books,
    'num_instances': num_instances,
    'num_instances_available': num_instances_available,
    'num_authors': num_authors,
    'num_visits': num_visits,
    }
    return render(request, 'index.html', context=context)


class BookListView(LoginRequiredMixin,generic.ListView):
    model = Book
    paginate_by = 10
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    
class BookDetailView(LoginRequiredMixin,generic.DetailView):
    model = Book
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author

def book_detail_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'catalog/book_detail.html', context={'book': book})

class AllLoanedBooksListView(PermissionRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan """
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10
    def get_queryset(self):
        return BookInstance.objects.all().order_by('due_back')

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

        
