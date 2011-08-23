from tiddlyweb.config import config

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag

from tiddlywebplugins.utils import get_store

from tiddlywebplugins.mysql2 import index_query
from tiddlywebplugins.sqlalchemy2 import (sField, sRevision, sText,
        sBag, sRecipe, sUser, sPolicy, sRole, sTag, sTiddler)

def setup_module(module):
    module.store = get_store(config)
    module.environ = {'tiddlyweb.config': config,
            'tiddlyweb.store': module.store}
    session = module.store.storage.session
# delete everything
    for table in (sField, sRevision, sBag, sRecipe, sUser, sText,
            sPolicy, sRole, sTag, sTiddler):
        session.query(table).delete()

def test_simple_store():
    bag = Bag('bag1')
    store.put(bag)
    tiddler = Tiddler('tiddler1', 'bag1')
    tiddler.text = u'oh hello i chrisdent have nothing to say here you know'
    tiddler.tags = [u'apple', u'orange', u'pear']
    tiddler.fields[u'house'] = u'cottage'
    store.put(tiddler)

    retrieved = Tiddler('tiddler1', 'bag1')
    retrieved = store.get(retrieved)

    assert retrieved.text == tiddler.text

def test_simple_search():
    tiddlers = list(store.search('"chrisdent"'))
    assert len(tiddlers) == 1
    assert tiddlers[0].title == 'tiddler1'
    assert tiddlers[0].bag == 'bag1'

    tiddlers = list(store.search('hello'))
    assert len(tiddlers) == 1
    assert tiddlers[0].title == 'tiddler1'
    assert tiddlers[0].bag == 'bag1'

def test_index_query_id():
    kwords = {'id': u'bag1:tiddler1'}
    tiddlers = list(index_query(environ, **kwords))

    assert len(tiddlers) == 1
    assert tiddlers[0].title == 'tiddler1'
    assert tiddlers[0].bag == 'bag1'

def test_index_query_filter():
    kwords = {'tag': u'orange'}
    tiddlers = list(index_query(environ, **kwords))

    assert len(tiddlers) == 1
    assert tiddlers[0].title == 'tiddler1'
    assert tiddlers[0].bag == 'bag1'

def test_index_query_filter_fields():
    kwords = {'house': u'cottage'}
    tiddlers = list(index_query(environ, **kwords))

    assert len(tiddlers) == 1
    assert tiddlers[0].title == 'tiddler1'
    assert tiddlers[0].bag == 'bag1'
    assert tiddlers[0].fields['house'] == 'cottage'

    kwords = {u'house': u'mansion'}
    tiddlers = list(index_query(environ, **kwords))

    assert len(tiddlers) == 0

def test_index_query_filter_fields():
    kwords = {'bag': u'bag1', 'house': u'cottage'}
    tiddlers = list(index_query(environ, **kwords))

    assert len(tiddlers) == 1
    assert tiddlers[0].title == 'tiddler1'
    assert tiddlers[0].bag == 'bag1'
    assert tiddlers[0].fields['house'] == 'cottage'

def test_search_right_revision():
    tiddler = Tiddler('revised', 'bag1')
    tiddler.text = u'alpha'
    tiddler.fields[u'house'] = u'cottage'
    store.put(tiddler)
    tiddler = Tiddler('revised', 'bag1')
    tiddler.text = u'beta'
    tiddler.fields[u'house'] = u'mansion'
    store.put(tiddler)
    tiddler = Tiddler('revised', 'bag1')
    tiddler.text = u'gamma'
    tiddler.fields[u'house'] = u'barn'
    store.put(tiddler)
    tiddler = Tiddler('revised', 'bag1')
    tiddler.text = u'delta'
    tiddler.fields[u'house'] = u'bungalow'
    store.put(tiddler)
    tiddler = Tiddler('revised', 'bag1')
    tiddler.text = u'epsilon'
    tiddler.fields[u'house'] = u'treehouse'
    store.put(tiddler)

    tiddlers = list(store.search('beta'))
    assert len(tiddlers) == 0

    tiddlers = list(store.search('epsilon'))
    assert len(tiddlers) == 1
    tiddler = store.get(Tiddler(tiddlers[0].title, tiddlers[0].bag))
    assert tiddler.title == 'revised'
    assert tiddler.bag == 'bag1'
    assert tiddler.fields['house'] == 'treehouse'

    kwords = {'bag': u'bag1', 'house': u'barn'}
    tiddlers = list(index_query(environ, **kwords))

    assert len(tiddlers) == 0

    kwords = {'bag': u'bag1', 'house': u'treehouse'}
    tiddlers = list(index_query(environ, **kwords))

    assert tiddlers[0].title == 'revised'
    assert tiddlers[0].bag == 'bag1'
    assert tiddlers[0].fields['house'] == 'treehouse'

    kwords = {'bag': u'bag1', 'tag': u'orange'}
    tiddlers = list(index_query(environ, **kwords))

    assert len(tiddlers) == 1

    kwords = {'bag': u'bag1', 'tag': u'rang'}
    tiddlers = list(index_query(environ, **kwords))

    assert len(tiddlers) == 0

def test_search_follow_syntax():
    QUERY = u'ftitle:GettingStarted (bag:cdent_public OR bag:fnd_public)'

    store.put(Bag('fnd_public'))
    store.put(Bag('cdent_public'))
    tiddler = Tiddler('GettingStarted', 'fnd_public')
    tiddler.text = u'fnd starts'
    tiddler.fields[u'house'] = u'treehouse'
    tiddler.fields[u'car'] = u'porsche'
    store.put(tiddler)
    tiddler = Tiddler('GettingStarted', 'cdent_public')
    tiddler.text = u'cdent starts'
    tiddler.fields[u'left-hand'] = u'well dirty'
    store.put(tiddler)
    tiddler = Tiddler('other', 'cdent_public')
    tiddler.text = u'cdent starts'
    store.put(tiddler)

    tiddlers = list(store.search(u'starts'))
    assert len(tiddlers) == 3

    tiddlers = list(store.search(QUERY))
    assert len(tiddlers) == 2

    tiddlers = list(store.search(u'"cdent starts"'))
    assert len(tiddlers) == 2

    tiddlers = list(store.search(u'"fnd starts"'))
    assert len(tiddlers) == 1

    tiddler = list(store.search(u'left-hand:"well dirty"'))
    assert len(tiddlers) == 1

def test_search_arbitrarily_complex():
    QUERY = u'ftitle:GettingStarted (bag:cdent_public OR bag:fnd_public) house:treehouse'

    tiddlers = list(store.search(QUERY))
    assert len(tiddlers) == 1

    QUERY = u'ftitle:GettingStarted ((bag:cdent_public OR bag:fnd_public) AND (house:treehouse AND car:porsche))'

    tiddlers = list(store.search(QUERY))
    assert len(tiddlers) == 1

def test_field_with_dot():
    tiddler = Tiddler('geoplace', 'cdent_public')
    tiddler.text = u'some place somewhere'
    tiddler.fields[u'geo.lat'] = u'1.25'
    tiddler.fields[u'geo.long'] = u'-45.243'
    store.put(tiddler)

    tiddlers = list(store.search(u'geo.lat:1.2*'))

    assert len(tiddlers) == 1

    tiddlers = list(store.search(u'geo.lat:"1.2*" AND geo.long:"-45.*"'))

    assert len(tiddlers) == 1
    
    tiddlers = list(store.search(u'geo.lat:"1.3*" AND geo.long:"-46.*"'))

    assert len(tiddlers) == 0

    tiddlers = list(store.search(u'geo.lat:"1.2*" OR geo.long:"-46.*"'))

    assert len(tiddlers) == 1

def test_limited_search():
    tiddlers = list(store.search(u'starts _limit:1'))
    assert len(tiddlers) == 1, tiddlers

    tiddlers = list(store.search(u'starts'))
    assert len(tiddlers) != 1, tiddlers

    tiddlers = list(store.search(u'starts _limit:so'))
    assert len(tiddlers) != 1, tiddlers

def test_modified():
    tiddler = Tiddler('GettingStarted', 'fnd_public')
    tiddler.modifier = u'fnd';
    store.put(tiddler)

    tiddlers = list(store.search(u'modifier:fnd'))

    assert len(tiddlers) == 1

    tiddler = Tiddler('GettingStarted', 'fnd_public')
    tiddler.modifier = u'cdent';
    store.put(tiddler)

    tiddlers = list(store.search(u'modifier:fnd'))

    assert len(tiddlers) == 0

    tiddler = Tiddler('GettingFancy', 'fnd_public')
    tiddler.modifier = u'fnd';
    store.put(tiddler)

    tiddlers = list(store.search(u'modifier:fnd OR modifier:cdent'))

    assert len(tiddlers) == 2

    tiddlers = list(store.search(u'modifier:fnd NOT modifier:cdent'))

    assert len(tiddlers) == 1

    tiddlers = list(store.search(u'modifier:fnd NOT (modifier:cdent OR title:GettingStarted)'))

    assert len(tiddlers) == 1

    tiddlers = list(store.search(u'modifier:fnd AND modified:20*'))

    assert len(tiddlers) == 1
