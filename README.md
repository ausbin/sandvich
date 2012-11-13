sandvich
========

sandvich is a simple, extensible document generator based on a pool of data and a basic template processor.

config
------

As mentioned above, sandvich is based around a data pool. In the default interface this is initialized by a yaml file named `config.yml`. If you're not familiar with yaml, it might be helpful to familiarize yourself with it via [its website](http://yaml.org/) or the [wikipedia article](https://en.wikipedia.org/wiki/Yaml).

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

By the `final` hook, the data pool initialized by the above configuration would resemble this python dictionary:

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

sandvich's template processor is extremely simple. It inserts values. If you're looking for more complex logic, try using hooks.

The most basic value is `{ arandomvalue }`. Using the configuration example above this would end up as `8093`. 

If you'd like to seek a value in a dictionary, you can use the `:` operator: `{ fruitcolors : banana }` results in `yellow`. `:` calls __getitem__ with the string you specified, so the last example would result in a call that looks like `d.__getitem__("fruitcolors").__getitem__("banana")` (`d` is the internal variable name for the data pool).

Trying to access an item in a list with the `:` operator will result in a blank value. Why? Because the parameter to `__getitem__()` is a string! The solution is the `#` operator, which converts the value name to an integer before calling `__getitem__()`.    
For example, `{ pigfoods # 0 }` results in `bacon`. The cool part is that you can use other values such as `-1` because they're integers too. `{ pigfoods # -1 }` would end up as `pork rinds`.

Attributes can be accessed with the `.` operator. `{ hookobjects # 1 . exampleattribute }` would become the value of `example.Example().exampleattribute`.  

If the last value in a chain of values is `callable()`, it will be replaced with its return value. 

If the final value is deemed `False` by `bool()` or accessing it raises an error, then it will be inserted into the template as an empty string.

The `|` operator can be used for basic logic. If the preceding value chain results in a value that is determined to be False by `bool()`, the next chain of values will be evaluated. For example, `{ fruitcolors : donkey | arandomvalue }` would result in `8093`. `fruitcolors["donkey"]` doesn't exist, so that value chain ends up as `None`. Since that value chain ended up evaluating to `False`, the value of `arandomvalue` will be inserted instead. 

hooks
-----

Hooks are certain points in sandvich's build process in which the data pool can be is exposed and modified. 

Here's a list of the basic process of a build and when hooks are called:

* *start* hook
* *template* hook
* template's location is determined and its content is loaded
* *prepages* hook
* loop through pages
    * the current page is loaded into `d["page"]`.
    * the page's location is determined and its content is loaded
    * *page* hook
    * the page's content is parsed for template tags
    * *premerge* hook
    * the page's content is replaced with the template's processed content
    * *postmerge* hook
    * page's destination is determined and written
    * *postpage* hook
* *postpages* hook
* *final* hook

Hooks are implemented using hook classes. Each hook is represented by a method. The first parameter is the data pool, a dictionary. Any modified version returned replaces the data pool entirely. Hook classes should always subclass `sandvich.hooks.Hook` to provide method stubs for hooks that aren't used. 

Here's an example hook that replaces every occurance of "banana" in each page with "apple":

```python
from sandvich.hooks import Hook

class Example (Hook) :
    def page (self, d) :
        d["page"]["content"].replace("banana", "apple")

        return d
```

If you're using the command line interface, list the names of the hook classes in `config.yml` in the order in which you would like them to be executed. If their module are not located in `sys.path`, add their location to `hooksdir`.

```yaml
hooksdir: customhooks

hooks:
- sandvich.hooks.JustPretendThisExists
- mycustommodule.Escape
```

Those will be found and initialized by `__main__.inithooks()` and put into `d["hookobjects"]` like so:

```python
{
    # ...
    "hooksdir" : "customhooks",
    "hooks" : [
        "sandvich.hooks.JustPretendThisExists",
        "mycustommodule.Escape",
    ],
    "hookobjects" : [
        sandvich.hooks.JustPretendThisExists(),
        mycustommodule.Escape()
    ],
    # ...
}
```
Note that `hooks` and `hooksdir` are ignored by `core.build`. `core.build` only cares about `hookobjects`, which is generated by `__main__.inithooks()`.
