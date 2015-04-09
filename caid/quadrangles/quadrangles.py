# -*- coding: UTF-8 -*-
import numpy as np
import matplotlib.tri as tri
import matplotlib.pyplot as plt

class Quadrangles(object):
    def __init__(self, x, y, quads=None):
        """
        a quadrangular mesh is represented by a triangulation. However, we must
        pay attention to degenerated quadangles and those with an angle > pi
        """
        self._x = x
        self._y = y
        if quads is None:
            print ("quadrangles automatic construction from vertices not yet implemented")
            raise()
        self._quads = quads

        self._triangles = None
        self._triang    = None
        self._ancestors = None
        self._sons      = None

        self._create_triangulation()
        self._compute_neighbors()

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def quads(self):
        return self._quads

    @property
    def triangles(self):
        return self._triangles

    @property
    def triang(self):
        return self._triang

    @property
    def ancestors(self):
        return self._ancestors

    @property
    def neighbors(self):
        return self._neighbors

    @property
    def sons(self):
        return self._sons

    def _uniform_split_quad(self, quad):
        """
        splits a quadrangle into 2 triangles
        Args:
            quad: list of 4 vertices ids
        Returns:
            2 triangles
        """
        I00,I10,I11,I01 = quad
        T1 = [I00,I10,I11]
        T2 = [I00,I11,I01]
        return T1,T2

    def _create_triangulation(self):
        triangles = [] ; ancestors = [] ; sons = []
        for enum,quad in enumerate(self.quads):
            T1,T2 = self._uniform_split_quad(quad)

            triangles.append(T1) ; ancestors.append(enum)
            triangles.append(T2) ; ancestors.append(enum)
            sons.append([2*enum, 2*enum+1])
        self._triangles = np.asarray(triangles)
        self._ancestors = np.asarray(ancestors)
        self._sons = np.array(sons, dtype=np.int32)

        self._triang = tri.Triangulation(self.x,self.y,self.triangles)

    def _compute_neighbors(self):
        n_quad = len(self.quads)
        ancestors = self.ancestors
#        print ancestors
        _neighbors = []
        for i in range(0, n_quad):
            T1 = 2*i ; T2 = 2*i+1
            ancestor = i
            neighbors = list(self.triang.neighbors[T1][0:2]) \
                    + list(self.triang.neighbors[T2][1:])
            neighbors = np.array(neighbors, dtype=np.int32)
#            print neighbors
            quad_neighbors = -np.ones(4, dtype=np.int32)
            for enum,T in enumerate(neighbors):
                if T > -1:
                    quad_neighbors[enum] = ancestors[T]
            _neighbors.append(quad_neighbors)
        self._neighbors = np.array(_neighbors, dtype=np.int32)
#        print "========="
#        print self._neighbors

    def plot(self):
        plt.triplot(self.triang, '-', lw=0.75, color="red")


class CubicHermiteBezier(Quadrangles):
    def __init__(self, nodes_filename, elements_filename):
        # node,R,Z,u1,u2,v1,v2,w1,w2,boundary type,boundary index,color
        fmt_nodes = [int, float, float, float, float, float, float, float, float, int, int, int]
        nodes    = np.genfromtxt(nodes_filename, comments="#")
        print nodes.shape

        # element,vertex(1:4),color
        fmt_elements = [int, int, int, int, int, int]
        elements = np.genfromtxt(elements_filename, comments="#")
        elements = np.array(elements, dtype=np.int32)
        colors    = np.array(elements[:,-1], dtype=np.int32)
        print elements.shape

        # extract quadrangles and use 0 based indexing
        quads = elements[:,1:-1] - 1

        R        = nodes[:,1]
        Z        = nodes[:,2]
        u        = nodes[:,3:5]
        v        = nodes[:,5:7]
        w        = nodes[:,7:9]
        bnd_type = np.array(nodes[:,9], dtype=np.int32)
        bnd_ind  = np.array(nodes[:,10], dtype=np.int32)
        vertices_colors  = np.array(nodes[:,11], dtype=np.int32)

        Quadrangles.__init__(self, R, Z, quads=quads)

        # elements attributs
        self._colors    = colors

        # nodes attributs
        self._u         = u
        self._v         = v
        self._w         = w
        self._bnd_type  = bnd_type
        self._bnd_index = bnd_ind
        self._vertices_colors = vertices_colors

    @property
    def colors(self):
        """
        returns an array of colors for each quadrangle
        """
        return self._colors

    @property
    def vertices_colors(self):
        """
        returns an array of colors for each quadrangle
        """
        return self._vertices_colors

    @property
    def u(self):
        """
        returns a 2D array of u vector for each vertex
        """
        return self._u

    @property
    def v(self):
        """
        returns a 2D array of v vector for each vertex
        """
        return self._v

    @property
    def w(self):
        """
        returns a 2D array of w vector for each vertex
        """
        return self._w

    @property
    def boundary_type(self):
        """
        returns a 1D array of boundary type for each vertex
        """
        return self._bnd_type

    @property
    def boundary_index(self):
        """
        returns a 1D array of boundary index for each vertex
        """
        return self._bnd_index


