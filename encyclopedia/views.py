#from lib2to3.pytree import _Results
from django import forms
from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
import markdown2
import random
from . import util

class WikiForm(forms.Form):
    title = forms.CharField(label='Title', max_length=256)
    content = forms.CharField(label='Content', widget=forms.Textarea)

    def clean(self):
        titles = util.list_entries()
        title = self.cleaned_data.get("title")
        for i in titles:
                if title == i:
                    raise ValidationError("An entry with that name already exists")
        return title

class EditForm(forms.Form):
    content = forms.CharField(label=False, widget=forms.Textarea)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "titles": util.list_entries()
    })

def entry(request, title):
    if title == 'random':
        entries = util.list_entries()
        title = entries[random.randint(0, (len(entries)-1))]
        return HttpResponseRedirect(reverse('entry', args=(title,)))
    try:
        content = markdown2.markdown(util.get_entry(title))
    except:
        content = ""
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": content
    })

def search(request):
    titles = util.list_entries()
    partial_matches = []
    q = request.GET['q']
    for title in titles:
        if q.casefold() == title.casefold():
            return HttpResponseRedirect(reverse('entry', args=(q,)))
        elif q.casefold() in title.casefold():
            partial_matches.append(title)
    return render(request, "encyclopedia/search_results.html", {
        "results": partial_matches
    })

def create(request):
    if request.method == 'POST':
        form = WikiForm(request.POST) # request.POST contains all the submitted data
        if form.is_valid():
        # if valid, this will return True and place data in 'cleaned_data'
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            # Save the entry is all is good:
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('entry', args=(title,)))
        
        return render(request, "encyclopedia/create.html", {
            "form": form
        })

    # If request is GET, render template with empty form:
    else:
        form = WikiForm()
        return render(request, "encyclopedia/create.html", {
            "form": form
        })

def edit(request, title):
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('entry', args=(title,)))
        else:
            print("form not valid")
            return render(request, "encyclopedia/edit.html", {
            "form": form,
            "title": title,
            "content": form.errors
            })
#need to fix this part. 'if content, pass to form, else entry doesn't exist, redirect to entry page 
    else:
        content = util.get_entry(title)
        if content:
            form = EditForm(initial={'content': content})
            return render(request, "encyclopedia/edit.html", {
                "form": form,
                "title": title
                })
        else:
            return HttpResponseRedirect(reverse('entry', args=(title,)))
