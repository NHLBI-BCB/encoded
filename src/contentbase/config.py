import venusian
from pyramid.interfaces import (
    PHASE2_CONFIG,
)
from .interfaces import (
    COLLECTIONS,
    PHASE1_5_CONFIG,
    ROOT,
    TYPES,
)


def includeme(config):
    registry = config.registry
    registry[COLLECTIONS] = CollectionsTool()
    config.set_root_factory(root_factory)


def root_factory(request):
    return request.registry[ROOT]


def root(factory):
    """ Set the root
    """

    def set_root(config, factory):
        root = factory(config.registry)
        config.registry[ROOT] = root

    def callback(scanner, factory_name, factory):
        scanner.config.action(('root',), set_root,
                              args=(scanner.config, factory),
                              order=PHASE1_5_CONFIG)
    venusian.attach(factory, callback, category='pyramid')

    return factory


def collection(name, **kw):
    """ Attach a collection at the location ``name``.

    Use as a decorator on Collection subclasses.
    """

    def set_collection(config, Collection, name, Item, **kw):
        registry = config.registry
        registry[TYPES].register(Item.item_type, Item)
        collection = Collection(registry, name, Item.item_type, **kw)
        registry[COLLECTIONS].register(name, collection)

    def decorate(Item):

        def callback(scanner, factory_name, factory):
            scanner.config.action(('collection', name), set_collection,
                                  args=(scanner.config, Item.Collection, name, Item),
                                  kw=kw,
                                  order=PHASE2_CONFIG)
        venusian.attach(Item, callback, category='pyramid')
        return Item

    return decorate


class CollectionsTool(dict):
    def __init__(self):
        self.by_item_type = {}

    def register(self, name, value):
        self[name] = value
        self[value.item_type] = value
        self.by_item_type[value.item_type] = value