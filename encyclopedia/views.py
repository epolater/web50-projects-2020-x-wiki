from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
import re
from random import randint

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})

def entry(request, title):
    entries = util.list_entries()
   
    if title in entries:
        return render(request, f"encyclopedia/entry.html", {
            "title" : title.capitalize(),
            "content" : util.convertmd(title),
            })
    else:
        return render(request, f"encyclopedia/error.html", {
            "message" : "Entry Not Found",
            })

def search(request):
    entries = util.list_entries()

    if request.method == "POST":
        title = request.POST.get("q")

        if title in entries:
            return render(request, f"encyclopedia/entry.html", {
                "title" : title,
                "content" : util.convertmd(title),
                })
        else:
            results = []
            for entry in entries:
                if re.search(rf".*{title}.*", entry, re.IGNORECASE):
                    results.append(entry)
            
            if len(results) > 0:
                return render(request, f"encyclopedia/results.html", {
                    "results" : results,
                    })
            else:
                return render(request, f"encyclopedia/error.html", {
                    "message" : "Entry Not Found",
                    })

def newpage(request):

    class NewPageForm(forms.Form):
        title = forms.CharField(label="Title", strip=True)
        entry = forms.CharField(widget=forms.Textarea, label="Entry")

    if request.method == "POST":
        form = NewPageForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            entry = form.cleaned_data["entry"]

            # Check entry if it is alredy in entries
            if title in util.list_entries():
                return render(request, f"encyclopedia/error.html", {
                    "message" : "Entry already exists",
                    })

            else:
                # Save Entry as md file
                util.save_entry(title, entry)

                # Render Entry Page
                return render(request, f"encyclopedia/entry.html", {
                    "title" : title.capitalize(),
                    "content" : util.convertmd(title),
                    })

    # Render New Page form     
    return render(request, f"encyclopedia/newpage.html", {
            "form" : NewPageForm(),
        })

def editpage(request):

    if request.method == "POST":

        title_init = request.POST.get("title")
        content_init = util.get_entry(title_init)

        class EditPageForm(forms.Form):
            title = forms.CharField(label="Title", strip=True, initial=title_init, widget=forms.HiddenInput() ) #
            content = forms.CharField(widget=forms.Textarea, label="Entry", initial=content_init)

        return render(request, f"encyclopedia/editpage.html", {
            "form" : EditPageForm(),
            "title" : title_init
            })

    else:
        return render(request, f"encyclopedia/error.html", {
            "message" : "Page Not Found",
            })

def editpage_save(request):

    if request.method == "POST":

        class EditPageForm(forms.Form):
            title = forms.CharField(label="Title", strip=True)
            content = forms.CharField(widget=forms.Textarea, label="Entry")
        
        form = EditPageForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            entry = form.cleaned_data["content"]

            # Save Entry as md file
            util.save_entry(title, entry)
            
        # Render Entry Page
        return render(request, f"encyclopedia/entry.html", {
                "title" : title,
                "content" : util.convertmd(title),
                })
    else:
        return render(request, f"encyclopedia/error.html", {
            "message" : "Page Not Found",
            })

def random(request):
    entries = util.list_entries()

    rand = randint(0, len(entries)-1)
    title = entries[rand]

    return render(request, f"encyclopedia/entry.html", {
            "title" : title.capitalize(),
            "content" : util.convertmd(title),
            })
