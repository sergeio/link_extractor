from unittest import TestCase
from unittest.mock import patch

from link_extractor import link_extractor


class _BaseTest(TestCase):

    def setUp(self):
        self.returned = self.execute()

    @patch('link_extractor.link_extractor.get_url_from_clipboard')
    @patch('link_extractor.link_extractor.get_title')
    def execute(self, get_title, get_url):
        get_title.return_value = self.title
        get_url.return_value = self.url
        return link_extractor.main()

    def test_main_function(self):
        self.assertEqual(self.returned, self.expected)


class TestSimpleTitle(_BaseTest):
    """Should make basic bullet point."""

    url = 'http://learnpythonthehardway.org/book/'
    title = 'Learn Python'
    expected = '  * [Learn Python [learnpythonthehardway.org]]({url})'.format(url=url)


class TestFancyTitleHyphen(_BaseTest):
    """Should strip out '- Stack Overflow'."""

    url = 'https://stackoverflow.com/questions/11155210/how-to-patch-python-class-using-mock-library'
    title = 'How to patch Python class using Mock library - Stack Overflow'
    expected = '  * [How to patch Python class using Mock library [stackoverflow.com]]({url})'.format(url=url)


class TestFancyTitleWithDots(_BaseTest):
    """Should strip out the '- NYTimes.com'."""

    url = 'http://www.nytimes.com/2014/05/06/science/a-desert-spider-with-astonishing-moves.html?hp&_r=1'
    title = 'A Desert Spider With Astonishing Moves - NYTimes.com'
    expected = '  * [A Desert Spider With Astonishing Moves [nytimes.com]]({url})'.format(url=url)


class TestFakeFancyTitle(_BaseTest):
    """A title that has some hierarchy, but none of the parts appear in the
    site, so no simplification should take place."""

    url = 'http://www.infinityplus.co.uk/stories/under.htm'
    title = 'Understand - a novelette by Ted Chiang'
    expected = '  * [Understand - a novelette by Ted Chiang [infinityplus.co.uk]]({url})'.format(url=url)


class TestUnicodeQuotesInTitle(_BaseTest):
    """Should output unicode quotes without changing them."""

    url = 'https://docs.python.org/2.7/library/multiprocessing.html'
    title = '16.6. multiprocessing - Process-based \u201cthreading\u201d interface - Python v2.7.6 documentation'
    expected = '  * [16.6. multiprocessing - Process-based \u201cthreading\u201d interface [docs.python.org]]({url})'.format(url=url)


class TestUnicodeInUrl(_BaseTest):
    """Should process the unicode fine."""
    url = 'https://en.wikipedia.org/wiki/Kurt_Gödel'
    title = 'Kurt Gödel - Wikipedia, the free encyclopedia'
    expected = '  * [Kurt Gödel [en.wikipedia.org]]({url})'.format(url=url)


class TestUnicodeSeparatorInTitle(_BaseTest):
    """Title is fancy, with a unicode hyphen; Should split and defancify."""

    url = 'http://aeon.co/magazine/world-views/logic-of-buddhist-philosophy/'
    title = 'The logic of Buddhist philosophy – Aeon'
    expected = '  * [The logic of Buddhist philosophy [aeon.co]]({url})'.format(url=url)


class TestMultipleTitlePartsHaveSimilarityZero(_BaseTest):
    """The first two parts of the title (separated by hyphens) have a
    similarity score of 0, since they don't appear in the site, while the
    'Aeon' part does.  So we should keep the first two title parts, and throw
    away the 'Aeon'."""

    url = 'http://aeon.co/magazine/world-views/logic-of-buddhist-philosophy/'
    title = 'The logic of Buddhist philosophy - Graham Priest - Aeon'
    expected = '  * [The logic of Buddhist philosophy - Graham Priest [aeon.co]]({url})'.format(url=url)


class TestTitleAndSiteNameHaveArticles(_BaseTest):
    """Should not count things like "the" towards the score of a title-part
    when defancifying titles."""

    url = 'http://www.theguardian.com/world/2013/jul/31/nsa-top-secret-program-online-data'
    title = 'XKeyscore: NSA tool collects \'nearly everything a user does on the internet\' | World news | theguardian.com'
    expected = '  * [XKeyscore: NSA tool collects \'nearly everything a user does on the internet\' | World news [theguardian.com]]({url})'.format(url=url)


class TestUnicodeWord(_BaseTest):
    """When one "word" is 100% unicode, make sure it isn't automatically count
    towards the score of a title-part when defancifying titles."""

    url = 'https://www.youtube.com/watch?v=iCqwwTfXr1Q'
    title = "▶ Day[9]\'s Musings - Being Relentlessly Positive - Youtube"
    expected = '  * [▶ Day[9]\'s Musings - Being Relentlessly Positive [youtube.com]]({url})'.format(url=url)


class TestTitleWithNewLines(_BaseTest):
    """Should strip out the carriage returns when defancifying."""

    url = 'http://lesswrong.com/lw/jd/human_evil_and_muddled_thinking/'
    title = '\nHuman Evil and Muddled Thinking - Less Wrong\n'
    expected = '  * [Human Evil and Muddled Thinking [lesswrong.com]]({url})'.format(url=url)
