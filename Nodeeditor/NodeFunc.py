from Nodeeditor.GraphicalNode import DrawGraphicalNode
from Nodeeditor.ContentWidgetFunc import AllContentWidgetFunctions
from Nodeeditor.SerializationFunc import Serializable
from Nodeeditor.SocketFunc import *

class AllNodeFunctions(Serializable):
    def __init__(self, scene, title="Undefined Node", inputs=[], outputs=[]):
        super().__init__()
        self._title = title
        self.scene = scene

        self.content = AllContentWidgetFunctions(self)
        self.grNode = DrawGraphicalNode(self)
        self.title = title

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        self.socket_spacing = 22

        # create socket for inputs and outputs
        self.inputs = []
        self.outputs = []
        counter = 0
        for item in inputs:
            socket = AllSocketFunctions(node=self, index=counter, position=LEFT_BOTTOM, socket_type=item, multi_edges=False)
            counter += 1
            self.inputs.append(socket)

        counter = 0
        for item in outputs:
            socket = AllSocketFunctions(node=self, index=counter, position=RIGHT_TOP, socket_type=item, multi_edges=True)
            counter += 1
            self.outputs.append(socket)

    # def __str__(self):
    #     return "<Node %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])
    def setPos(self, x, y):
        self.grNode.setPos(x, y)

    @property
    def pos(self):
        return self.grNode.pos()        # QPointF

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title

    def getSocketPosition(self, index, position):
        x = 0 if (position in (LEFT_TOP, LEFT_BOTTOM)) else self.grNode.width

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # start from bottom
            y = self.grNode.height - self.grNode.edge_size - self.grNode.padding - index * self.socket_spacing
        else :
            # start from top
            y = self.grNode.title_height + self.grNode.padding + self.grNode.edge_size + index * self.socket_spacing

        return [x, y]


    def updateConnectedEdges(self):
        for socket in self.inputs + self.outputs:
            # if socket.hasEdge():
            for edge in socket.edges:
                edge.updatePositions()


    def remove(self):
        for socket in (self.inputs+self.outputs):
            for edge in socket.edges:
                edge.remove()
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        self.scene.removeNode(self)


    def serialize(self):
        inputs, outputs = [], []
        for socket in self.inputs: inputs.append(socket.serialize())
        for socket in self.outputs: outputs.append(socket.serialize())
        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.grNode.scenePos().x()),
            ('pos_y', self.grNode.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs),
            ('content', self.content.serialize()),
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data['id']
        hashmap[data['id']] = self

        self.setPos(data['pos_x'], data['pos_y'])
        self.title = data['title']

        data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000 )
        data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000 )

        self.inputs = []
        for socket_data in data['inputs']:
            new_socket = AllSocketFunctions(node=self, index=socket_data['index'], position=socket_data['position'],
                                            socket_type=socket_data['socket_type'])
            new_socket.deserialize(socket_data, hashmap, restore_id)
            self.inputs.append(new_socket)

        self.outputs = []
        for socket_data in data['outputs']:
            new_socket = AllSocketFunctions(node=self, index=socket_data['index'], position=socket_data['position'],
                                            socket_type=socket_data['socket_type'])
            new_socket.deserialize(socket_data, hashmap, restore_id)
            self.outputs.append(new_socket)


        return True