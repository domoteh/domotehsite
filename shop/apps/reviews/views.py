from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from apps.catalog.models import Product

from .forms import QuestionForm, ReviewForm
from .models import Question, Review


@login_required
@require_POST
def add_review(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=product_id)
    if Review.objects.filter(product=product, user=request.user).exists():
        reviews = product.reviews.filter(is_approved=True)
        return render(request, "reviews/partials/review_list.html", {"reviews": reviews, "product": product})

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()

    reviews = product.reviews.filter(is_approved=True)
    return render(request, "reviews/partials/review_list.html", {"reviews": reviews, "product": product})


@login_required
@require_POST
def add_question(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=product_id)
    form = QuestionForm(request.POST)
    if form.is_valid():
        q = form.save(commit=False)
        q.product = product
        q.user = request.user
        q.save()

    questions = product.questions.all()
    return render(request, "reviews/partials/question_list.html", {"questions": questions, "product": product})
