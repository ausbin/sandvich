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

