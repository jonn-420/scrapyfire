from django.shortcuts import render
from firescraper import scraper
def home(request):
	scraper.start_main_loop(False)
	return render(request,'index.html')

def pry(request):
	scraper.start_main_loop(True)
	return render(request,'index.html')
