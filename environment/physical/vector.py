import numpy as np

class Vector:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        self.arr = np.array([x, y, z])

    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.update()

    def update(self):
        self.arr = np.array([self.x, self.y, self.z])

    def get(self):
        return self.arr

    def add(self, vec: np.array([0, 0, 0])):
        s = Vector.addVect(vec, self.arr)
        self.x = s[0]
        self.y = s[1]
        self.z = s[2]
        self.update()

    def sub(self, vec: np.array([0,0,0])):
        s = Vector.subVect(vec, self.arr)
        self.x = s[0]
        self.y = s[1]
        self.z = s[2]
        self.update()

    def mag(self):
        return Vector.magVect(self.arr)

    def magSq(self):
        return Vector.magSqVect(self.arr)

    @staticmethod
    def addVect(vec1: np.array([0, 0, 0]), vec2: np.array([0, 0, 0])):
        s = np.add(vec1, vec2)
        return s

    @staticmethod
    def subVect(vec1: np.array([0, 0, 0]), vec2: np.array([0, 0, 0])):
        s = np.subtract(vec1, vec2)
        return s

    @staticmethod
    def magVect(vec1: np.array([0, 0, 0])):
        return np.sqrt(vec1.dot(vec1))

    @staticmethod
    def magSqVect(vec1: np.array([0, 0, 0])):
        mag = Vector.magVect(vec1)
        return mag ** 2