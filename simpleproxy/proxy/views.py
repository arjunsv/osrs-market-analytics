from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ViewDoesNotExist
import requests

# Create your views here.
def proxy(request):
	other = requests.get(request.GET['other'])
	return HttpResponse(other.text)