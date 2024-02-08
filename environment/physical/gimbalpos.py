from email.mime import base
import numpy as np
from physical.vector import Vector


class GimbalPos:
    def __init__(self, config={}):
        self.translation = Vector()
        self.initHeight = Vector(0, 0, config['INITIAL_HEIGHT'])  # initial height
        self.rotation = Vector()

        baseAngles = []
        baseAngles.append( config['BASE_ANGLE_X'] )
        baseAngles.append( config['BASE_ANGLE_Y'] )
        baseAngles.append( config['BASE_ANGLE_Z'] )

        platformAngles = []
        platformAngles.append( config['PLATFORM_ANGLE_X'] )
        platformAngles.append( config['PLATFORM_ANGLE_Y'] )
        platformAngles.append( config['PLATFORM_ANGLE_Z'] )

        betaAngles = []
        betaAngles.append( config['BETA_ANGLES_X'] )
        betaAngles.append( config['BETA_ANGLES_Y'] )
        betaAngles.append( config['BETA_ANGLES_Z'] )

        self.baseRadius = float(config['BASE_RADIUS'])  # base radius
        self.platformRadius = float(config['PLATFORM_RADIUS'])  # platform radius
        self.hornLength = float(config['SERVO_HORN_LENGTH'])  # servo horn length
        self.legLength = float(config['SERVO_LEG_LENGTH'])  # server leg length
        self.baseAngles = baseAngles  # base angle
        self.platformAngles = platformAngles  # platform angles
        self.beta = betaAngles  # beta angles
        self.alpha = {}

        self.baseJoints = {}
        self.platformJoints = {}
        self.q = {}
        self.l = {}
        self.A = {}

        for i in range(0, 3):
            mx = self.baseRadius * np.cos(np.radians(self.baseAngles[i]))
            my = self.baseRadius * np.sin(np.radians(self.baseAngles[i]))
            self.baseJoints[i] = Vector(mx, my)

        for i in range(0, 3):
            mx = self.platformRadius * np.cos(np.radians(self.platformAngles[i]))
            my = self.platformRadius * np.sin(np.radians(self.platformAngles[i]))
            self.platformJoints[i] = Vector(mx, my)

            self.q[i] = Vector()
            self.l[i] = Vector()
            self.A[i] = Vector()

    def applyTranslation(self, transform, rotation):
        self.rotation.set(rotation.x, rotation.y, rotation.z)
        self.translation.set(transform.x, transform.y, transform.z)
        self.calcQ()
        self.calcAlpha()

    def calcQ(self):
        for i in range(0, 3):
            self.q[i].x = np.cos(self.rotation.z) * np.cos(self.rotation.y) * self.platformJoints[i].x + \
                          (-np.sin(self.rotation.z) * np.cos(self.rotation.x) + np.cos(self.rotation.z) * np.sin(
                              self.rotation.y) * np.sin(self.rotation.x)) * self.platformJoints[i].y + \
                          (np.sin(self.rotation.z) * np.sin(self.rotation.x) + np.cos(self.rotation.z) * np.sin(
                              self.rotation.y) * np.cos(self.rotation.x)) * self.platformJoints[i].z

            self.q[i].y = np.sin(self.rotation.z) * np.cos(self.rotation.y) * self.platformJoints[i].x + \
                          (np.cos(self.rotation.z) * np.cos(self.rotation.x) + np.sin(self.rotation.z) * np.sin(
                              self.rotation.y) * np.sin(self.rotation.x)) * self.platformJoints[i].y + \
                          (-np.cos(self.rotation.z) * np.sin(self.rotation.x) + np.sin(self.rotation.z) * np.sin(
                              self.rotation.y) * np.cos(self.rotation.x)) * self.platformJoints[i].z

            self.q[i].z = -np.sin(self.rotation.y) * self.platformJoints[i].x + \
                          np.cos(self.rotation.y) * np.sin(self.rotation.x) * self.platformJoints[i].y + \
                          np.cos(self.rotation.y) * np.cos(self.rotation.x) * self.platformJoints[i].z
            self.q[i].update()

            # translations
            self.q[i].add(Vector.addVect(self.rotation.get(), self.initHeight.get()))
            tempVector = Vector.subVect(self.q[i].get(), self.baseJoints[i].get())
            self.l[i] = Vector(tempVector[0], tempVector[1], tempVector[2])

    def calcAlpha(self):
        for i in range(0, 3):
            L = self.l[i].magSq() - (self.legLength * self.legLength) + (self.hornLength * self.hornLength)
            M = 2 * self.hornLength * (self.q[i].z - self.baseJoints[i].z)
            N = 2 * self.hornLength * (np.cos(self.beta[i]) * (self.q[i].x - self.baseJoints[i].x) + np.sin(
                self.beta[i] * (self.q[i].y - self.baseJoints[i].y)))

            self.alpha[i] = np.arcsin(L / np.sqrt(M * M + N * N)) - np.arctan2(N, M)

            xtemp = self.hornLength * np.cos(self.alpha[i]) * np.cos(self.beta[i]) + self.baseJoints[i].x
            ytemp = self.hornLength * np.cos(self.alpha[i]) * np.sin(self.beta[i]) + self.baseJoints[i].y
            ztemp = self.hornLength * np.sin(self.alpha[i]) + self.baseJoints[i].z
            self.A[i].set(xtemp, ytemp, ztemp)

            xqxb = (self.q[i].x - self.baseJoints[i].x)
            yqyb = (self.q[i].y - self.baseJoints[i].y)
            h0 = np.sqrt((self.legLength * self.legLength) + (self.hornLength * self.hornLength) - (xqxb * xqxb) - (
                    yqyb * yqyb)) - self.q[i].z

            L0 = 2 * self.hornLength * self.hornLength
            M0 = 2 * self.hornLength * (h0 + self.q[i].z)
            a0 = np.arcsin(L0 / np.sqrt(M0 * M0 + N * N)) - np.arctan2(N, M0)

    def getAlpha(self):
        return self.alpha

    def getDegrees(self):
        degrees = {}
        degrees['x'] = np.degrees(self.alpha[0])
        degrees['y'] = np.degrees(self.alpha[1])
        degrees['z'] = np.degrees(self.alpha[2])
        return degrees

    def preview(self):
        for i in range(0, 3):
            print(self.alpha[i])
