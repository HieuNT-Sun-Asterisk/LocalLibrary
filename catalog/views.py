from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


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
    paginate_by = 1
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    def get_queryset(self):
        return Book.objects.all()[:5] # Get 5 books containing the title war

class BookDetailView(LoginRequiredMixin,generic.DetailView):
    model = Book
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    

class AuthorListView(PermissionRequiredMixin,generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    def get_queryset(self):
        return Author.objects.all()[:5]

class AuthorDetailView(generic.DetailView):
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
