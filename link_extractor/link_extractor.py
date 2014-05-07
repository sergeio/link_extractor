#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Print a markdown-formatted bullet point with a link to the URL in your
clipboard.
"""
from glob import glob
from html.parser import HTMLParser
from os import path
from subprocess import Popen, PIPE
from urllib.error import URLError
from urllib.parse import unquote, urlparse
from urllib.request import urlopen
import json
import re

from bs4 import BeautifulSoup


def main():
    """Returns the .md formatted bullet point for the URL in the clipboard."""
    url = get_url_from_clipboard()
    site = urlparse(url).netloc.replace('www.', '')
    title = get_title(url)
    title = transform_title(title, site)
    return '  * [{title} [{site}]]({url})'.format(
        title=title, site=site, url=url)


def get_url_from_clipboard():
    """Returns the contents of your clipboard, hopefully a url."""
    process = Popen(['xclip', '-out'], stdout=PIPE)
    clipboard_contents = process.communicate()[0]
    url = clipboard_contents.strip()
    url = str(url, encoding='utf-8')
    url = unquote(url)
    return url


def get_title(url):
    """Get the title of the page matching the `url`."""
    title = get_title_from_firefox_session(url)
    if not title:
        title = get_title_from_internet(url)
    return title


def transform_title(title, site):
    """Miscellaneous title transformations.

    Handle some unicode, unescape HTML, simplify hierarchical titles, ...

    """
    title = HTMLParser().unescape(title)
    title = parse_fancy_titles(title, site)
    return title


def get_title_from_firefox_session(url):
    """Get the title for the `url` from Firefox, if it's recently opened."""
    def get_firefox_data():
        """Get a dictionary with the Firefox state from disk."""
        try:
            session = get_session_file()
            with open(session, 'r') as json_session_file:
                firefox_data = json.loads(json_session_file.read())
        except IOError:
            return ''
        return firefox_data

    def walk(structure, criteria=lambda x: True):
        """Yield each substructure in the nested `structure`.

        Only yields things that match the `criteria` passed in.

        """
        if criteria(structure):
            yield structure
        if isinstance(structure, dict):
            for value in structure.values():
                for structure in walk(value, criteria=criteria):
                    yield structure
        elif isinstance(structure, list) or isinstance(structure, tuple):
            for item in structure:
                for structure in walk(item, criteria=criteria):
                    yield structure

    def search(structure, criteria):
        """Search the `structure` for a substruct that matches `criteria`."""
        for match in walk(structure, criteria):
            return match
        return {}

    def has_matching_url(element):
        """`element` has the url we are looking for."""
        isdict = isinstance(element, dict)
        return isdict and unquote(element.get('url', '')) == url

    firefox_data = get_firefox_data()
    matching_tab = search(firefox_data, has_matching_url)
    return matching_tab.get('title')


def get_session_file():
    """Get the path of the place where firefox stores its session info."""
    home = path.expanduser('~')
    glob_path = path.join(home, '.mozilla/firefox/*.default/sessionstore.js')
    session_file = glob(glob_path)
    return session_file[0]


def get_title_from_internet(url):
    """Get the title of the `url` from the internet."""
    try:
        html = urlopen(url).read()
        soup = BeautifulSoup(html)
        title = soup.find('title').text
    except ValueError:
        # Usually happens when the clipboard doesn't contain a URL.
        title = ''
    except AttributeError:
        # Usually happens when soup = None; e.g. when URL is an image or PDF.
        title = ''
    except URLError:
        title = ''

    return title


def make_title_site_similarity_function(site):
    """Curry the title_site_similarity function to only require a title."""
    def remove_non_alphanumerics(word):
        """Returns the `word` with nonalphanumerics (and underscores)."""
        return re.sub(r'[^\w]', '', word)

    def title_site_similarity(title):
        """What portion of the words in the title are in the site?"""
        result = 0.0
        words = re.split(r'[. ]', title)
        for word in words:
            word = word.lower()
            word = remove_non_alphanumerics(word)
            if word in site:
                result += 1.0 / len(words)

        return result

    return title_site_similarity


def parse_fancy_titles(title, site):
    """Pull out the title of the page when the title has the site in it.

    >>> parse_fancy_titles(
    ... 'Flubber - Wikipedia, the free encyclopedia', 'en.wikipedia.org')
    'Flubber'

    """
    title_parts = []
    for separator in [' -- ', ' - ', ' | ', ' >> ', ' : ']:
        if separator in title:
            title_parts = title.split(separator)
            break

    if not title_parts:
        return title

    similarity_function = make_title_site_similarity_function(site)
    scores = list(zip(map(similarity_function, title_parts), title_parts))

    if not any(score for score, title_part in scores):
        return title
    return min(scores)[1]


if __name__ == '__main__':
    print(main())
