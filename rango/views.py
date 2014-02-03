from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
#from django.shortcuts import render

from datetime import datetime

#from django.shortcuts import render
# Import the Category model
from rango.models import Category, Page, UserProfile
#from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm

from rango.bing_search import run_query

def index(request):
    context = RequestContext(request)
    
    cat_list = get_category_list()
    
    category_list = Category.objects.all()
    context_dict = {'categories': category_list}

    for category in category_list:
        category.url = encode_url(category.name)

    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list
    context_dict['cat_list'] = cat_list

    #### NEW CODE ####
    if request.session.get('last_visit'):
        # The session has a value for the last visit
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).seconds > 1:
#        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:

            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        # The get returns None, and the session does not have a value for the last visit.
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1
    #### END NEW CODE ####

    # Render and return the rendered response back to the user.
    return render_to_response('rango/index.html', context_dict, context)


def about(request):
    context = RequestContext(request)
    if request.session.get('visits'):
        visits = request.session.get('visits')
    else:
        visits = 0
    context_dict = {'visits': visits}
    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list
    
    return render_to_response('rango/about.html', context_dict, context)
#    return render(request, 'rango/about.html', {'visits': visits})
'''
    context = RequestContext(request)

    # If the visits session varible exists, take it and use it.
    # If it doesn't, we haven't visited the site so set the count to zero.
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    # remember to include the visit data
    return render_to_response('rango/about.html', {'visits': count}, context)
#    return render_to_response('rango/about.html', context_dict, context)
#    return HttpResponse("Rango Says: Here is the about page.")
'''

def category(request, category_name_url):
    # Request our context from the request passed to us.
    context = RequestContext(request)

    # Change underscores in the category name to spaces.
    # URLs don't handle spaces well, so we encode them as underscores.
    # We can then simply replace the underscores with spaces again to get the name.
    category_name = category_name_url.replace('_', ' ')

    # Create a context dictionary which we can pass to the template rendering engine.
    # We start by containing the name of the category passed by the user.
    context_dict = {'category_name': category_name}
    #context_dict = {'category_name': category_name, 'category_name_url': category_name_url}
    context_dict['category_name_url']= category_name_url
    
    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list
    
    result_list = []

    try:
        # Can we find a category with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(name=category_name)

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    if request.method == 'POST':
        if request.POST.get('query'):
            query = request.POST['query'].strip()
            if query:
                result_list = run_query(query)
#        query = request.POST['query'].strip()

#        if query:
            # Run our Bing function to get the results list!
#            result_list = run_query(query)
            
    context_dict['result_list'] = result_list

    # Go render the response and return it to the client.
    return render_to_response('rango/category.html', context_dict, context)

@login_required
def add_category(request):
    # Get the context from the request.
    form = CategoryForm()
    context = RequestContext(request)
#    return render_to_response('rango/add_category.html', {'form' : form})
#    return render(request, 'rango/add_category.html', {
#        'form': form,
#    })
    context_dict = {'form' : form }
    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('rango/add_category.html', context_dict, context)
def decode_url(item1):
    return item1.replace('_', ' ')
def encode_url(item1):
    return item1.replace(' ', '_')
#    category_name = category_name_url.replace('_', ' ')

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    category_name_url = encode_url(category_name)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            # Retrieve the associated Category object so we can add it.
            # Wrap the code in a try block - check if the category actually exists!
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                # If we get here, the category does not exist.
                # We render the add_page.html template without a context dictionary.
                # This will trigger the red text to appear in the template!
                return render_to_response('rango/add_page.html', {}, context)

            # Also, create a default value for the number of views.
            page.views = 0

            # With this, we can then save our new model instance.
            page.save()

            # Now that the page is saved, display the category instead.
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'category_name_url': category_name_url,
             'category_name': category_name, 'form': form}
    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list

    return render_to_response( 'rango/add_page.html',
            context_dict,
             context)

def register(request):
    if request.session.test_cookie_worked():
        print ">>>> TEST COOKIE WORKED!"
        request.session.delete_test_cookie()
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}
    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list
    
    # Render the template depending on the context.
    return render_to_response(
            'rango/register.html',
            context_dict,
            context)

def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user is not None:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('rango/login.html', {}, context)

@login_required
def restricted(request):
    context = RequestContext(request)
    return render_to_response('rango/restricted.html', {}, context)
#    return HttpResponse('rango/restricted.html')

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')

from rango.bing_search import run_query

def search(request):
    context = RequestContext(request)
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render_to_response('rango/search.html', {'result_list': result_list}, context)

'''
def get_category_list():
    cat_list = Category.objects.all()
#    cat_list = Category.objects.order_by('-likes')[:5]

    for category in cat_list:
        category.url = encode_url(category.name)
    return cat_list

'''
def get_category_list(max_results=0, starts_with=''):
    
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__startswith=starts_with)
    else:
        cat_list = Category.objects.all()
        
    if max_results > 0 and len(cat_list) > max_results:
        cat_list = cat_list[:max_results]
        
    # The following two lines are new.
    # We loop through each category returned, and create a URL attribute.
    # This attribute stores an encoded URL (e.g. spaces replaced with underscores).
    for cat in cat_list:
        cat.url = encode_url(cat.name)
    
    return cat_list


from django.contrib.auth.models import User

@login_required
def profile(request):
    # Like before, get the request's context.
    context = RequestContext(request)
    
    cat_list = get_category_list()
    context_dict = {}
    context_dict['cat_list'] = cat_list
    u = User.objects.get(username = request.user)
#    up = UserProfile.objects.get(user=u)

    try:
#        up = UserProfile.objects.get(user=request.user)
        up = UserProfile.objects.get(user=u)
    except:
        up = None


    context_dict['user'] = u
    context_dict['userprofile'] = up
    
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    
    return render_to_response(
            'rango/profile.html',
            context_dict,
            context)

@login_required
def track_url(request):
#    print "track_url"    
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            page_id = page_id.strip('/')
#            print "page_id = [" + page_id + "]"
            try:
                p = Page.objects.get(id=page_id)
#                print "url = " + p.url
                if p:
                    p.views += 1
                    p.save()
                    url = p.url
            except:
                pass
#    print "url = " + url                     
    return redirect(url)

@login_required
def like_category(request):
    context = RequestContext(request)
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            
            likes = category.likes + 1
            category.likes =  likes
            category.save()

    return HttpResponse(likes)

def suggest_category(request):
        context = RequestContext(request)
        cat_list = []
        starts_with = ''
        if request.method == 'GET':
                starts_with = request.GET['suggestion']

        cat_list = get_category_list(8, starts_with)

        return render_to_response('rango/category_list.html', {'cat_list': cat_list }, context)

@login_required
def auto_add_page(request):
    print "auto_add_page\n\n"
    context = RequestContext(request)
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        print "cat_id = " +   cat_id + "][" + url + "][" + title + "]\n"
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)
            if p and category:
                redirect_url = '/rango/category/' + category.name + '/'
                print "redirect url = " + redirect_url
                # return redirect("/rango/category/" + category.name + "/")
                return HttpResponse(status=200)
            # pages = Page.objects.filter(category=category).order_by('-views')

            # Adds our results list to the template context under name pages.
            # context_dict['pages'] = pages
    return redirect('rango/')
    #        http://127.0.0.1:8888/rango/category/Aeroplanes/
    # return render_to_response('rango/category.html', context_dict, context)
    # return render_to_response('rango/page_list.html', context_dict, context)




