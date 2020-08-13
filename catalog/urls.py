from django.urls import path
from . import views

urlpatterns = [

    path('', views.index, name='index'),
    # path('books/', admin.site.urls),
    # path('authors/', admin.site.urls),
    # path('book/<int: book_id>', admin.site.urls),
    # path('author/<int: author_id>', admin.site.urls)   
]




