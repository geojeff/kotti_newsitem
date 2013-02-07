from datetime import date
from random import randint

from kotti.resources import get_root

from kotti_newsitem.resources import NewsItem
from kotti_newsitem.views import NewsItemListViews
from kotti_newsitem.views import NewsItemView


def test_newsitem_view(db_session, dummy_request):

    root = get_root()
    content = NewsItem()
    root['content'] = content

    view = NewsItemView(root['content'], dummy_request)

    assert view.view() == {}


def test_news_item_list_views(db_session, dummy_request):

    root = get_root()
    d = date.today()

    # Add some news items
    for i in range(10):

        n = NewsItem(
            title=u"News Item %s Title" % (i + 1),
            description=u"News Item %s description" % (i + 1),
            )

        if i == 9:
            # Set date to future for the last news item
            # this will fail in leap years on february 29th, which is acceptable
            # as this is only a test.
            n.publish_date = date(d.year + 1, d.month, d.day)
        else:
            # Set date to random year in the past
            n.publish_date = date(d.year - randint(0, 100), d.month, d.day)

        root["news_item_%s" % (i + 1)] = n
        db_session.add(n)
        db_session.flush()

    dummy_request.registry.settings['kotti_newsitem.widget.num_news'] = 4
    view = NewsItemListViews(root, dummy_request)

    assert len(view.news_items()) == 9
    assert len(view.news_items(5)) == 5

    assert len(view.all_news()['items']) == 9
    assert len(view.recent_news()['items']) == 4

    # Test order
    d = date.today()
    for n in view.news_items():
        assert n.publish_date <= d
        d = n.publish_date
