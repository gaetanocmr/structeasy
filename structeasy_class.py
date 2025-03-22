class Node():
    """ This class will contain the node informations"""
    def __init__(self, nnumber, x, y, z, tag, eltype = 0):
        self.nnumber = nnumber # Node number (integer)
        self.x = x             # x-coordinate (float)
        self.y = y             # y-coordinate (float)   
        self.z = z             # z-coordinate (float) or None if 2D
        self.tag = tag         # Node tag (integer)
        self.coord = [x, y, z] # Node coordinates (list)
        self.eltype = eltype   # Element type (string)
        self.container = []    # Container for general porpouses (list)
        self.data_analysis = []# Container for analysis data (list) 

class Element(Node):
    """ This class will contain the node informations"""
    def __init__(self, enumber, nodes, tag, etype = 1):
        self.enumber = enumber  # Element number (integer)
        self.nodes = nodes      # Node list (list of nodes objects)
        self.nodei = nodes[0].nnumber # Node i number (integer)
        self.nodej = nodes[1].nnumber # Node j number (integer)
        self.tag = tag          # Element tag (integer)
        self.etype = etype      # Element type (string)
        self.container = []     # Container for general porpouses (list)
        self.data_analysis = [] # Container for analysis data (list)      

    def length(self): # Works only with two nodes elements
        """ Calculate the element length """
        if len(self.nodes) == 2:
            x1, y1, z1 = self.nodes[0].coord
            x2, y2, z2 = self.nodes[1].coord
            return ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)**0.5
        else:
            return None
    
    def vecxz(self, vecxy = [0, 0, 1]):
        # vecxy = What you want (vecxy is global vertical)
        from numpy import subtract, sqrt, cross, round, array
        # Method created FROM: https://portwooddigital.com/2020/08/08/a-vector-in-the-x-z-plane/ (M.Scott)
        xaxis = subtract(self.nodes[1].coord, self.nodes[0].coord) # Vector from node j to node i
        vecxz = cross(xaxis, vecxy).tolist() # vecz direction
        return vecxz
    