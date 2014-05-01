#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
Print a markdown-formatted bullet point with a link to the URL in your
clipboard.
"""
from HTMLParser import HTMLParser
from glob import glob
from itertools import chain
from os import path
from subprocess import Popen, PIPE
from urllib2 import urlopen, URLError
from urlparse import urlparse
import json

from BeautifulSoup import BeautifulSoup


def main():
    """Returns the .md formatted bullet point for the URL in the clipboard."""
    url = get_url_from_clipboard()
    site = urlparse(url).netloc.replace('www.', '')
    title = get_title(url)
    title = transform_title(title, site)
    return u'  * [{title} [{site}]]({url})'.format(
        title=title, site=site, url=url)


def get_url_from_clipboard():
    """Returns the contents of your clipboard, hopefully a url."""
    process = Popen(['xclip', '-out'], stdout=PIPE)
    clipboard_contents = process.communicate()[0]
    url = clipboard_contents.strip()
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
    substitutions = {u'\u2013': '-', u'\u2014': '-', u'\xb7': '-'}
    for letter, replacement in substitutions.iteritems():
        title = title.replace(letter, replacement)
    title = ''.join([x if ord(x) < 128 else '?' for x in title])
    title = parse_fancy_titles(title, site)
    return title


def get_title_from_firefox_session(url):
    """Get the title for the `url` from Firefox, if it's recently opened."""
    def get_url_and_tab_info_for_tab(tab):
        """Return a dict where the title and url for the tab are stored.

        Firefox stores closed tabs in a slightly different way from open ones,
        hence the branching.

        """
        if 'entries' in tab:
            place_where_url_stored = tab['entries'][0]
        else:
            place_where_url_stored = tab['state']['entries'][0]
        return place_where_url_stored

    def tab_matches_url(tab):
        """Does the `tab` match the `url` we are looking for?"""
        place_where_url_stored = get_url_and_tab_info_for_tab(tab)
        tab_title = place_where_url_stored.get('title', '')
        return tab_title and place_where_url_stored.get('url') == url

    try:
        session = get_session_file()
        with open(session, 'r') as json_session_file:
            firefox_data = json.loads(json_session_file.read())
    except IOError:
        return ''

    tabs = firefox_data['windows'][0]['tabs']
    closed_tabs = firefox_data['windows'][0]['_closedTabs']
    all_tabs = chain(tabs, closed_tabs)

    matching_tabs = filter(tab_matches_url, all_tabs)
    if matching_tabs:
        place_where_url_stored = get_url_and_tab_info_for_tab(matching_tabs[0])
        title = place_where_url_stored.get('title', '')
        return title
    return ''


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
        print u'Bad URL: ' + repr(url)
        title = ''
    except URLError:
        title = ''

    return title


def make_title_site_similarity_function(url):
    """Curry the title_site_similarity function to only require a title."""
    def title_site_similarity(title):
        """What portion of the words in the title are in the url?"""
        result = 0.0
        words = title.split(' ')
        for word in words:
            if word.lower() in url:
                result += 1.0 / len(words)

        return result

    return title_site_similarity


def parse_fancy_titles(title, url):
    """Pull out the title of the page when the title has the site in it.

    >>> parse_fancy_titles(
    ... 'Flubber - Wikipedia, the free encyclopedia', 'en.wikipedia.org')
    'Flubber'

    """
    title_parts = []
    for separator in [' -- ', ' - ', ' | ', ' >> ']:
        if separator in title:
            title_parts = title.split(separator)
            break

    if not title_parts:
        return title

    similarity_function = make_title_site_similarity_function(url)
    scores = zip(map(similarity_function, title_parts), title_parts)

    return min(scores)[1]


if __name__ == '__main__':
    print main()
