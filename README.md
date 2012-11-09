sandvich
========

sandvich is a simple, extensible document generator based on a pool of data and a basic template processor.

config
======

As mentioned above, sandvich is based around a data pool. In the default interface this is initialized by a yaml file named `config.yml`.

Here's an example `config.yml`:

    src: pages
    ext: .html
    
    dest: dest
    newext: .html
    
    templatedir: templates
    templateext: .html
    template: # more or less required, default is templates/template.html
      # evaluates to: `location: templates/mytemplate.html`
      name: mytemplate
    
    # last 7 lines are equivalent to:
    # template:
    #   location: templates/mytemplate.html
    
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

That configuration at the `page` hook would look like the following python snippet:

    {
        "src" : "src",
        "ext" : ".html",
        "dest" : "dest",
        "newext" : ".html",
    
        "templatedir" : "templates",
        "templateext" : ".html",
        "template" : {
            "name" : "mytemplate",
            "location" : "templates/mytemplate.html",
        },
    
        "hooksdir" : "hooks",
        "hooks" : [
            "sandvich.hooks.Markdown",
            "example.Example"
        ],
        "hookobjects" : [
            sandvich.hooks.Markdown(),
            example.Example()
        ],
    
        "page" : [
            {
                "name" : "bob",
                "title" : "a tomato",
                "has-banana" : True
                "location" : "src/bob.html",
                "content" : "this is the contents of the file src/bob.html"
            },
            {
                "number-of-chickens" : 47,
                "name" : "larry",
                "title" : "a cucumber",
                "location" : "src/larry.html",
                "content" : "i am not a pickle!"
            },
            {
                "location" : "src/jerry.html",
                "content" : "this is a page about jerry"
            }
        ]
    
    
    
    }

