# Learn by Example

I want to give a few demonstrative examples of how to build off this application.

## Creating an endpoint

The `views.py` files are where actual web endpoints lie. Let's take a look at one.

```python3
@course.route('/')
@login_required
def index():
    return render_template("course/list.html")
```

Let's walk through this line-by-line and understand all of the components.

`@course.route('/')`: This is a Flask decorator. We're basically telling the web server, "hey, if they request, in the course module, the page named `/`, please run this function and send the user the output." Many of these can be used in succession.

This works out such that when the user points their browser to `/course/`, the following decorated function will be called.

`@login_required`: This is a custom decorator. Note that this must go *after* the endpoint decorator.

This intercepts the function call and asks, "hey, is this user logged in? If so, continue. If not, abort with `403`: Unauthorized".

`def index():`: This is the name of the function. This can be anything you want, but there are cases that you need to refer to these function names programmatically, so you should name this something you can recognize.

In this case, if we wanted to redirect to this endpoint, we would call, in another function, `return redirect(url_for('course.index'))`.

`return render_templte("course/list.html")`: This is where any function logic would go. Because we always know a user will be logged in if they get to this point, there is no logic in this function.

The return indicates that whatever value is returned will be sent to the browser. (These can also be aborts/error codes, redirects, files, and more).

In this case, the page will render the file specified inside of `templates/`--- namely, `templates/course/list.html`. Let's take a look at that file next.

## Endpoint HTML

```html
{% extends "base/scaffolding.html" %}
{% block title %}List Courses{% endblock %}
{% block breadcrumb %}
{{ breadcrumb('course.index', 'Courses') | safe }}
{% if user and user.has_permission('course:create') %}
{{ breadcrumb('course.create', 'Create') | safe }}
{% endif %}
{% endblock %}
{% block content %}
<table class="table table-striped">
    <thead>
        <tr>
            <th>Course Code</th>
            <th>Block</th>
            <th>Year</th>
            <th>Repository</th>
            <th>Role</th>
            <th>View</th>
        </tr>
    </thead>
    <tbody>
    {% for enrollment in user.courses() %}
        <tr>
            <td>{{ enrollment.course.code }}</td>
            <td>{{ enrollment.course.block }}</td>
            <td>{{ enrollment.course.year }}</td>
            <td>{{ enrollment.repo }}</td>
            <td>{{ enrollment.role }}</td>
            <td>
                <a href="{{ url_for('course.view', id=enrollment.course.course_pk) }}">
                    <button type="button" class="btn btn-info">View</button>
                </a>
            </td>
        </tr>
    {% endfor %}
    </tbody>
</table>
{% endblock %}
```

There's a lot to unpack here, so I'll give an idea of the core concepts.

We use Jinja2 which is a preprocessor on our HTML, which will take HTML as well as special commands and render it into HTML **on the server side.**

You could just specify HTML code here, but Jinja2 allows us a lot of power which we take advantage of highly.

First of all, it's important to notice the `extends` at the top of the file. We're actually using other files via inheritance. Basically, if you look at the `scaffolding.html` page, you'll notice it's a skeleton of a page, and has places where you can put your content.

The three places where content is rendered into the skeleton is the three `block`s--- title, breadcrumb, and content.

### Title

The title of the page--- this is rendered at the top of the page AND as a `<title>` tag.

### Breadcrumb

We use breadcrumbs to make navigation easy. You can specify, using the breadcrumb function specified in `util.py`, another breadcrumb to add to the list, in order to help people navigate around. I'll come up with stricter standards for breadcrumbs soon.

It's worth noting that this uses an `if` statement in order to specify breadcrumbs according to some condition. The reason we can use `user` here is because it is passed to the template using a preprocessor, so don't expect all variables to be passed to your template unless you explicitly make them appear there.

The syntax for breadcrumb is `breadcrumb('end.point', 'Nice Display Name', **kwargs)` where kwargs are arguments which must be passed to the function you're referring to.

### Content

This might actually be the simplest one-- note the `for` loop, and that we can loop through a variable and print attributes using the `{{}}` notation. Learn by example here, and look at the Jinja2 docs for more information.


## Another endpoint

There are a few things I missed with this first example that I'd like to go over.

```python3
@course.route('/<id>')
@login_required
def view(id):
    user = get_session_user()
    enrollment = DerpDB.enrollment(user, id)
    if not enrollment:
        return abort(404)
    return render_template("course/view.html", enrollment=enrollment)
```

 - Note the named parameter in the string, where when they go to /course/123, this endpoint will be called.
 - `123` is passed in as an argument to the actual function, and you can use it.
 - `get_session_user()` is our way of getting the information from the user's session.
 - Database logic is included. These functions all exist in `db_helper.py`.
 - A condition is satisfied or not, and the return value is conditional on this. The `abort` returns an error 404 file not found.
 - The render template also has a named parameter. Now you can use `enrollment` as a variable in your Jinja2 template.
 

I encourage you all to learn by example as much as you can, but here should be an overview that might help you get started with working on the project.

Let me know if you have any questions!

Daniel Barnes