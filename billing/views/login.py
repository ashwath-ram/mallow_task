from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from billing.models import Product, SalesBill, SalesBillItem
from billing.utils import send_email # Using the thread function

import math
import logging

logger = logging.getLogger(__name__)


def login_view(request):
    try:
        if request.user.is_authenticated:
            return redirect('billing_page')

        if request.method == "POST":
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                nxt_url = request.GET.get('next', 'billing_page')
                return redirect(nxt_url)
        else:
            form = AuthenticationForm()

        return render(request, 'login.html', {'form': form})
    
    except Exception as e:
        logger.exception("Exception {}".format(e.args))
        raise


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')
