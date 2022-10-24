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

# Form for creating new entries
class NewForm(forms.Form):
    title = forms.CharField(label='Title', max_length=256)
    content = forms.CharField(label='Content', widget=forms.Textarea)
    
    # Custom form validation that will raise an error if entry already exists
    def clean_title(self):
        titles = util.list_entries()
        title = self.cleaned_data['title']
        for i in titles:
                if title.casefold() == i.casefold():
                    raise ValidationError("An entry with that name already exists")
        return title

# Form for editing entries
class EditForm(forms.Form):
    content = forms.CharField(label=False, widget=forms.Textarea)

# Index page
def index(request):
    return render(request, "encyclopedia/index.html", {
        "titles": util.list_entries()
    })

# Entry page
def entry(request, title):
    try:
        content = markdown2.markdown(util.get_entry(title))
    except:
        content = ""
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": content
    })

# Random function will redirect to a random entry
def random_entry(request):
    entries = util.list_entries()
    title = entries[random.randint(0, (len(entries)-1))] 
    return HttpResponseRedirect(reverse('entry', args=(title,)))

# Search page
def search(request):
    titles = util.list_entries()
    partial_matches = []
    q = request.GET['q']
    for title in titles:
        # A match will redirect to that entry's page
        if q.casefold() == title.casefold():
            return HttpResponseRedirect(reverse('entry', args=(q,)))
        # A partial match will get added to a list, which is passed to the template
        elif q.casefold() in title.casefold():
            partial_matches.append(title)
    # If no partial matches, the template will display 'no matches'
    return render(request, "encyclopedia/search_results.html", {
        "results": partial_matches
    })

# Create New page
def create(request):
    if request.method == 'POST':
        form = NewForm(request.POST) # request.POST contains all the submitted data
        if form.is_valid():
        # if valid, this will return True and place data in 'cleaned_data'
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            # Save the entry if all is good:
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('entry', args=(title,)))
        
        return render(request, "encyclopedia/create.html", {
            "form": form
        })

    # If request is GET, render template with empty form:
    else:
        form = NewForm()
        return render(request, "encyclopedia/create.html", {
            "form": form
        })

def edit(request, title):
    if request.method == 'POST':
        # Get the submitted data and check it's valid
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            # Save the entry and redirect to its page 
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('entry', args=(title,)))
        else:
            return render(request, "encyclopedia/edit.html", {
            "form": form,
            "title": title,
            })
    else:
        # If request is GET, display the pre-populated form
        content = util.get_entry(title)
        if content:
            form = EditForm(initial={'content': content})
            return render(request, "encyclopedia/edit.html", {
                "form": form,
                "title": title
                })
        else:
            return HttpResponseRedirect(reverse('entry', args=(title,)))
