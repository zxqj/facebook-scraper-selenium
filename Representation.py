
class Representation(object):

    def __init__(self, node):
        self.node = node
    
    """
    Interrogates DOM node to populate object with properties.

    obj -- the object that is to be populated

    return value: None
    """
    def createObject(self, obj):
        pass    
    
    """
    Find this representation in an arbitrary DOM node, if one exists.
    If this representation occurs multiple times, return the first one.
    
    rootNode -- node to be searched
    
    return value: Representation -- will be None if none are found
    """
    @staticmethod
    def get(rootNode, RepresentationClass):
        nodes = RepresentationClass.getAll(rootNode)
        return None if len(nodes) is 0 else nodes[0]

    """
    Find all instances of this representation in an arbitrary DOM node, if any exist.

    rootNode -- node to be searched

    return value: List<Representation> -- will be an empty List if none are found
    """
    @staticmethod
    def getAll(rootNode):
        pass

    @staticmethod
    def create(creator, getter):
        class DerivingRepresentation(Representation):
            def __init__(self, node):
                super().__init__(node)

            def createObject(self, object):
                creator(self.node, object)

            @staticmethod
            def get(rootNode):
                return DerivingRepresentation(getter(rootNode))
        
        return DerivingRepresentation