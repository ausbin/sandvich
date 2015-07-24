![picture of a sandvich](http://wiki.teamfortress.com/w/images/thumb/9/95/Sandvich.png/100px-Sandvich.png)

sandvich
========

sandvich is a simple, extensible document generator based on a pool of data and
a basic template processor.

    $ sandvich help
    usage: sandvich build [location]

installation
------------

Dependencies: a recent version of [Python 2][] and [PyYAML][] (for the default
command-line interface).

    $ git clone git://github.com/ausbin/sandvich.git sandvich
    $ cd sandvich
    # python2 setup.py install
    # install -Dm 755 bin/sandvich /usr/bin

If you use Arch, [download the PKGBUILD][PKGBUILD] and run `makepkg`. To use the
command-line interface install the `python2-yaml` package in `[community]`.

config
------

As mentioned above, sandvich is based around a data pool. In the default
interface this is initialized by a yaml file named `config.yml`. If you're not
familiar with yaml, it might be helpful to familiarize yourself with it via
[its website][yaml] or the [wikipedia article][yamlwp].

Here's an example config file:

```yaml
src: pages/
ext: .html

dest: dest/
newext: .html

templatedir: templates/
templateext: .html
template: 
  # location is evaluated to: "templates/mytemplate.html"
  name: mytemplate

hooksdir: hooks # added to sys.path
hooks:
# uses markdown to convert pages to html
- sandvich.hooks.Markdown
# hook could be stored in hooks/example.py
- example.Example

# passed as the extensions= keyword argument to markdown.markdown()
# by the builtin sandvich.hooks.Markdown hook (optional)
# see https://pythonhosted.org/Markdown/extensions/index.html
markdown-extensions:
- toc

pages: # should be provided, default is an empty list
- name: bob
  title: a tomato # just an example, below line is valid too
  has-banana: false
# can be ordered however you like
- number-of-chickens: 47
  name: larry
# last line is equivalent to:
# location: src/larry.html
  title: a cucumber
- location: src/jerry.html

# you can insert whatever you want into the data pool
arandomvalue = 8093

fruitcolors:
  banana: yellow
  apple: green
  carrot: orange
  grape: purple

pigfoods:
- bacon
- ham
- pig tail
- pork rinds
```

By the `final` hook, the data pool initialized by the above configuration would
resemble this python dictionary:

```python
{
    # prepended to each page's name if their location must be determined (default: "src/")
    "src" : "src/",
    # appended to each page's name to form its location if it wasn't specified (default: "")
    "ext" : ".html",
    # prepended to each page's name to determine its destination (default: "dest/")
    "dest" : "dest/",
    # appended to each page's name to form its destination if unspecified (default: ".html")
    "newext" : ".html",

    # prepended to template["name"] to form the location if it wasn't specified (default: "")
    "templatedir" : "templates/",
    # appended to template["name"] to form the location if it wasn't specified (default: "")
    "templateext" : ".html",
    # called by sandvich after the page and premerge hooks. arguments are a
    # string holding the contents of the template and the contents of the data
    # pool in the form of a dictionary (in that order). this defaults to
    # `sandvich.templates.process`. To modify this, use a hook.
    # `sandvich.hooks.JinjaTemplates` is a good example.
    "templatecall" : sandvich.templates.process,

    # the template the pages will be processed with
    "template" : {
        # sandwiched in between templatedir and templateext to form the location if it wasn't specified
        "name" : "mytemplate",
        # computed with templatedir+name+templateext
        "location" : "templates/mytemplate.html",   
        # the content contained by the template pulled from its location on the disk
        "content" : "<!DOCTYPE html><html><head><title>{page:title}</title><head><body>{page:content}</body></html>"
    },

    # directory holding user-created hooks (added to sys.path[0]) 
    "hooksdir" : "hooks",
    # a list of Hook classes in the form of module(s).class
    # this is processed by __main__.inithooks() to form hookobjects
    "hooks" : [
        "sandvich.hooks.Markdown",
        "example.Example"
    ],

    # nothing has changed here
    "markdown-extensions": [
        "toc"
    ],

    # instances of the objects listed in hooks (also created by __main__ rather than core.build)
    "hookobjects" : [
        sandvich.hooks.Markdown(),
        example.Example()
    ],

    #  list of pages and their respective sub-data
    "pages" : [
        {
            "name" : "bob",
            "title" : "a tomato",
            "has-banana" : True
            "location" : "src/bob.html",
            # before this page's "premerge" hook:
            #"content" : "this is the contents of the file src/bob.html"  
            # after:
            "content" : "<!DOCTYPE html><html><head><title>a tomato</title><head><body>this is the contents of the file src/bob.html</body></html>"
        },
        {
            "number-of-chickens" : 47,
            "name" : "larry",
            "title" : "a cucumber",
            "location" : "src/larry.html",
            # from disk:
            #"content" : "i am not a pickle!",
            # after being inserted into the template :
            "content" : "<!DOCTYPE html><html><head><title>a cucumber</title><head><body>i am not a pickle!</body></html>"
        },
        {
            "location" : "src/jerry.html",
            # value from disk:
            #"content" : "this is a page about jerry",
            # after being merged with the template (notice that {page:title} ends up blank here):
            "content" : "<!DOCTYPE html><html><head><title></title><head><body>this is a page about jerry</body></html>"
        }
    ],

    # all of our random data is still here!
    "arandomvalue" : 8093,
    "fruitcolors" : {
        "banana" : "yellow",
        "apple" : "green",
        "carrot" : "orange",
        "grape" : "purple"
    },
    "pigfoods" : [
        "bacon",
        "ham",
        "pig tail",
        "pork rinds"
    ],

    # set just before each "page" hook (more or less a pointer to the current page in "pages")
    "page" : {
        "location" : "src/jerry.html",
        # value from disk:
        #"content" : "this is a page about jerry",
        # after being merged with the template (notice that {page:title} ends up blank here):
        "content" : "<!DOCTYPE html><html><head><title></title><head><body>this is a page about jerry</body></html>"
    }
}
```

templates
---------

sandvich's template processor is extremely simple. It inserts values. If you're
looking for more complex logic, try using hooks.

### using jinja templates

[Jinja][] is a powerful templating language written in Python and styled after
[Django][]'s templating libraries. As a result it has many features such as 
inheritance, looping, and conditionals. If you're doing anything complicated, 
give it a try.

sandvich has builtin support for jinja. Install jinja2 and add the following
hook into `config.yml` to get started:

```yaml
hooks:
- sandvich.hooks.JinjaTemplates
```

### builtin template processor syntax

The most basic value substitution is `{ arandomvalue }`. Using the config
example above this would end up as `8093`. 

If you'd like to seek a value in a dictionary, you can use the `:` operator: 
`{ fruitcolors : banana }` results in `yellow`. `:` calls `__getitem__` with
the string you specified, so the last example would result in a call that looks
like `d.__getitem__("fruitcolors").__getitem__("banana")` (`d` is the internal
variable name for the data pool).

Trying to access an item in a list with the `:` operator will result in a blank
subsitution because the parameter to `__getitem__()` is a string (raising a 
`TypeError` that is caught by sandvich). The solution is the `#` option, which
casts the value name it is placed in front of to an integer before calling
`__getitem__()`. For example, `{ pigfoods : #0 }` results in `bacon`. 

Attributes can be accessed with the `.` operator. The tag
`{ hookobjects : #1 . exampleattribute }` would become the value of
`example.Example().exampleattribute`.  

If a value name is followed by a pair of parentheses (`()`), it will be
replaced with its return value. For example,
`{ hookobjects # 1 . examplemethod() }` would result in the return value of
`example.Example().examplemethod()`.

The `|` operator can be used for basic logic. If the preceding value chain
results in a value that is determined to be `False` by `bool()`, the next chain
of values will be evaluated. For example,
`{ fruitcolors : donkey | arandomvalue }` would result in `8093`. 
`fruitcolors["donkey"]` doesn't exist, so that value chain ends up evaluating
to `False`, causing the value of `arandomvalue` to be inserted instead. 

If the final value is deemed `False` by `bool()` or accessing it raises an 
error, then it won't be inserted into the template. `that's the { bogus }th 
fish in my basement this week!`, for example, would end up as `that's the th 
fish in my basement this week!`.

hooks
-----

Hooks are certain points in sandvich's build process in which the data pool can
be is exposed and modified. 

Here's a list of the basic process of a build and when hooks are called:

* **start** hook
    * **template** hook
        * template's location is determined and its content is loaded
    * **prepages** hook
        * loop through pages
            * the current page is loaded into `d["page"]`.
            * the page's location is determined
            * **pageload** hook
                * if `d["page"]["content"]` doesn't exist, the page's content
                  is loaded from `d["page"]["location"]`
            * **page** hook
                * the page's content is parsed for template tags
            * **premerge** hook
                * the page's content is replaced with the template's processed content
            * **postmerge** hook
                * page's destination is determined and written
            * **postpage** hook
    * **postpages** hook
* **final** hook

Hooks are implemented using hook classes. Each hook is represented by a method.
The first parameter is the data pool, a dictionary. Any modified version
returned replaces the data pool entirely. Hook classes should always subclass
`sandvich.hooks.Hook` to provide method stubs for hooks that aren't used. 

Here's an example hook that replaces every occurance of "banana" in each page
with "apple":

```python
from sandvich.hooks import Hook

class Example (Hook) :
    def page (self, d) :
        d["page"]["content"].replace("banana", "apple")

        return d
```

A list of data pool keys can be found in the [config section](#config).

If you're using the command line interface, list the names of the hook classes
in `config.yml` in the order in which you would like them to be executed. If
the module the hooks are contained in is not located in `sys.path`, add its
location to `hooksdir`. We'll assume that the above python code is located in 
`./hooks/mycustommodule.py`:

```yaml
hooksdir: hooks

hooks:
- sandvich.hooks.JustPretendThisExists
- mycustommodule.Example
```

Those will be found and initialized by `__main__.inithooks()` and put into 
`d["hookobjects"]` like so:

```python
{
    # ...
    "hooksdir" : "customhooks",
    "hooks" : [
        "sandvich.hooks.JustPretendThisExists",
        "mycustommodule.Example",
    ],
    "hookobjects" : [
        sandvich.hooks.JustPretendThisExists(),
        mycustommodule.Example()
    ],
    # ...
}
```

Note that `hooks` and `hooksdir` are ignored by `core.build`. `core.build` only
cares about `hookobjects`, which is generated by `__main__.inithooks()`.

[yaml]:     http://yaml.org/ 
[yamlwp]:   https://en.wikipedia.org/wiki/Yaml
[PKGBUILD]: https://raw.github.com/ausbin/sandvich/master/PKGBUILD
[Python 2]: http://python.org/
[PyYaml]:   http://pyyaml.org/wiki/PyYAML
[Jinja]:    http://jinja.pocoo.org/
[Django]:   https://djangoproject.com/
