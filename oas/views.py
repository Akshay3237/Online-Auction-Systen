from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    # Assuming you have a CustomUser model
    user = request.user

    # Logic to retrieve other profile-related information
    # For example:
    # profile_info = user.profile

    return render(request, 'index.html', {'user': user})