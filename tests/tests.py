from mock import patch
from unittest import TestCase

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
    """Should strip out 'unit testing -' and '- Stack Overflow'."""

    url = 'https://stackoverflow.com/questions/11155210/how-to-patch-python-class-using-mock-library'
    title = 'unit testing - How to patch Python class using Mock library - Stack Overflow'
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
