from django.shortcuts import render
from firescraper import scraper
def home(request):
	scraper.start_main_loop()
	return render(request,'index.html')
