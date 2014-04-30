link_extractor
==============

Print a markdown-formatted bullet point with a link to the URL in your clipboard.

The script will also do some smart things to simplify "fancy" urls.  More info
in the [Usage](#Usage) Section.

Why?
----
I have markdown files with links.  Things like stories I should read, ones I'd
like read later, ones I might recommend to a friend, etc...

Typing them out by hand is boring.


Requires
--------
  * BeautifulSoup
  * Firefox
      - Not an actual requirement, but it will run faster if you use FF.

Usage
-----

My usual pattern is, while reading a story I want to save, copy the url from
Firefox, then use vim to open the file I want to add the link to, hit `,k`, and
the link appears in the line above the cursor.

### Example

For example, if I have the following URL in my copy-buffer,

```
http://stackoverflow.com/questions/3488603/how-do-i-use-tilde-in-the-context-of-paths
```

then the following line will be added to the file:

```
  * [How do I use '~' (tilde) in the context of paths? [stackoverflow.com]](http://stackoverflow.com/questions/3488603/how-do-i-use-tilde-in-the-context-of-paths)
```

### Fanciness

The title was too fancy for my liking, so link_extractor changed it from

```
How do I use '~' (tilde) in the context of paths? - Stack Overflow
```

to

```
How do I use '~' (tilde) in the context of paths? [stackoverflow.com]
```

No more of those pesky dashes!

### Vim

Here is the relevant `.vimrc` line:

```
nmap ,k O<esc>:.!link_extractor<CR>
```
