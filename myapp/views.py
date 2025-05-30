from django.shortcuts import redirect, render
from .forms import ExpenseForm
from .models import Expense
import datetime
from django.db.models import Sum


# Create your views here.
def index(request):
    category = request.GET.get("category")
    category_sum = Expense.objects.filter(
        category=request.GET.get("category")
    ).aggregate(total_sum=Sum("amount"))["total_sum"]

    filter_by_category = (
        Expense.objects.values("category")  # Группировка по категории и дате
        .annotate(
            total=Sum("amount")
        )  # Суммирование по каждой категории для каждой даты
        .order_by("category")  # Сортировка по дате
    )

    print(filter_by_category)

    expenses = Expense.objects.all()
    if request.method == "POST":
        expense = ExpenseForm(request.POST)
        if expense.is_valid():
            expense.save()
            return redirect("index")

    last_year = datetime.date.today() - datetime.timedelta(days=365)
    yearly_sum = (
        Expense.objects.filter(date__gt=last_year).aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0
    )

    last_month = datetime.date.today() - datetime.timedelta(days=30)
    monthly_sum = (
        Expense.objects.filter(date__gt=last_month).aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0
    )

    last_week = datetime.date.today() - datetime.timedelta(days=7)
    weekly_sum = (
        Expense.objects.filter(date__gt=last_week).aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0
    )
    daily_sums = (
        Expense.objects.filter()
        .values("date")
        .order_by("date")
        .annotate(sum=Sum("amount"))
    )

    form = ExpenseForm()

    return render(
        request,
        "myapp/index.html",
        {
            "form": form,
            "expenses": expenses,
            "yearly_sum": yearly_sum,
            "monthly_sum": monthly_sum,
            "weekly_sum": weekly_sum,
            "daily_sums": daily_sums,
            "category_sum": category_sum,
            "category": category,
            "filter_by_category": filter_by_category,
        },
    )


def edit(request, id):
    expense = Expense.objects.get(id=id)
    form = ExpenseForm(instance=expense)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect("index")
    return render(request, "myapp/edit.html", {"form": form})


def delete(request, id):
    expense = Expense.objects.get(id=id)
    form = ExpenseForm(instance=expense)
    if request.method == "GET":
        return render(request, "myapp/delete.html", {"form": form})
    if request.method == "POST":
        expense.delete()
        return redirect("index")
