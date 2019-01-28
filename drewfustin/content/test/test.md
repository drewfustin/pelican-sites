Title: Test Page
Slug: test
Date: 1982-04-19
Status: draft
Banner: #111
Imports: [vega]
Summary: This is the summary for the test page.

---

The quick brown fox jumped over the lazy dog. The quick brown fox jumped over the lazy dog. The quick brown fox jumped over the lazy dog. The quick brown fox jumped over the lazy dog. The quick brown fox jumped over the lazy dog. [ref]a footnote is this. I want it to be a really long footnote so that it goes over a single line. I'm trying to make sure the line-height parameter is set correctly for this CSS element.[/ref]

The quick brown fox jumped over the lazy dog. The quick brown fox jumped over the lazy dog. The quick brown fox jumped over the lazy dog. The quick brown fox jumped over the lazy dog. The quick brown fox jumped over the lazy dog. The quick brown fox jumped over the lazy dog. The quick brown fox jumped over the lazy dog. The quick brown fox jumped over the lazy dog. The quick brown fox jumped over the lazy dog.

---

# h1 Heading 8-)
## h2 Heading
### h3 Heading
#### h4 Heading
##### h5 Heading
###### h6 Heading


## Horizontal Rules

---


## Emphasis

**This is bold text**

*This is italic text*

<s>This is strikethrough text</s>


## Blockquotes


> Blockquotes can also be nested...
>> ...by using additional greater-than signs right next to each other...
> > > ...or with spaces between arrows.


## Lists

Unordered

- Create a list by starting a line with `+`, `-`, or `*`
- Sub-lists are made by indenting 4 spaces:
    - Marker character change forces new list start:
        - Ac tristique libero volutpat at
        - Facilisis in pretium nisl aliquet
        - Nulla volutpat aliquam velit
- Very easy!

Ordered

1. Lorem ipsum dolor sit amet
2. Consectetur adipiscing elit
3. Integer molestie lorem at massa


## Code

Inline `code`

Syntax highlighting

    #!js
    var foo = function (bar) {
      return bar++;
    };

    console.log(foo(5));

This is Python code

    #!python start:15
    @LiquidTags.register('img')
    def img(preprocessor, tag, markup):
        src = None
        width = None
        height = None
        alt = None
        title = None
        caption = None
        credit = None

        match = FORMAT.search(markup)
        if match:
            argdict = match.groupdict()
            src = argdict['src']
            width = argdict['width']
            height = argdict['height']
            alt = argdict['alt'] or " "
            title = argdict['title']
            caption = argdict['caption']
            credit = argdict['credit']

        if not src:
            raise ValueError("Error processing input, "
                             "expected syntax: {0}".format(SYNTAX))

        tag = "<figure class='img'><img src='{src}' alt='{alt}'".format(src=src, alt=alt)
        if title:
            tag += " title='{title}'".format(title=title)
        if width:
            tag += " width='{width}px'".format(width=width)
        if height:
            tag += " height='{height}px'".format(height=height)
        tag += ">"
        if credit:
            tag += "<div class='credit'>{credit}</div>".format(credit=credit)
        if caption:
            tag += "<figcaption>{caption}</figcaption>".format(caption=caption)
        tag += "</figure>"

        return tag

{% code
    test/code/inquisition.py
    language:python
    lines:20-30
    :download:
%}

## Tables

| Option | Description |
| ------ | ----------- |
| data   | path to data files to supply the data that will be passed into templates. |
| engine | engine to be used for processing templates. Handlebars is the default. |
| ext    | extension to be used for dest files. |

Right aligned columns

| Option | Description |
| ------:| -----------:|
| data   | path to data files to supply the data that will be passed into templates. |
| engine | engine to be used for processing templates. Handlebars is the default. |
| ext    | extension to be used for dest files. |

Big table that scrolls

| First Name | Last Name | Points | Points | Points | Points | Points | Points | Points | Points | Points | Points | Points | Points | Points |
| ---------- | --------- | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| Jill       | Smith     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     |
| Eve        | Jackson   | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     |
| Adam       | Johnson   | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     | 50     |


## Links

[link text](http://dev.nodeca.com)

[link with title](http://nodeca.github.io/pica/demo/ "title text!")


## Images

{% img
    https://octodex.github.com/images/stormtroopocat.png
    width:400
    height:400
    alt:"Stormtroopocat"
    title:"Stormtroopocat"
    caption:"This is the caption"
    credit:"This is the credit"
%}

{% img {filename}img/preview.png width:200 %}


{% csv
    test/data/data.csv
    :download:
%}

{% csv
    test/data/scores.csv
    lines:1-2
    :download:
%}

## Math

Inline: $E=mc^2$

Newline: $$\frac{\partial \phi}{\partial t} + u \cdot \nabla \phi = 1$$


## Subscript/Superscript

- 19^th^
- H~2~O

## Plots

{% vega
    test/plot/horsepower_vs_mpg.json
    caption:"This is the caption"
    credit:"This is the credit"
    kwargs: {"data_file": "data/cars.json"}
%}

{% vega
    test/plot/horsepower_vs_mpg.py
    :altair:
    style:static/json/vega.json
    kwargs: {"data_file": "data/cars.json"}
%}

## Pandas in-line

{% pandas
    src: {"data/data.csv": "test/data/data.csv"}
    (pd.read_csv('data/data.csv')
       .assign(e2=lambda x: np.power(x['e'], 2))
       .set_index(['a', 'b']))
%}
