from django.shortcuts import render, redirect

from main.models import Category, Thread, Message


def index(request):
    return render(request, 'main/forum/index.html')


def category(request, category):

    if request.method == "POST":
        title = request.POST["title"]
        text = request.POST["message"]
        c = Category.objects.get(name=category)
        thread = Thread(title=title,category=c)
        thread.save()
        m = Message(text=text, user=request.user, thread=thread)
        m.save()
        return redirect("/forum/" + category + "/" + str(thread.id))


    # For now we're just going to have a developer forum
    threads = Category.objects.get(name=category).thread_set.all()

    return render(request, 'main/forum/category.html', {'category' : category, 'threads' : threads})


def thread(request, category, thread):

    if request.method == "POST":
        text = request.POST['message']
        post = Message(text=text, thread=Thread.objects.get(category__name=category,id=thread), user=request.user)
        post.save()

    t = Thread.objects.get(category__name=category, id=thread)
    t.views += 1
    t.save()
    messages = t.message_set.all()

    return render(request, 'main/forum/thread.html', {'thread' : t.title, 'category' : category, 'messages' : messages})

def newthread(request):
    return render(request, 'main/forum/newthread.html')