# -*- coding: utf-8 -*-

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4 import *
from PyQt4 import QtGui
from PyQt4.QtOpenGL import *
from PyQt4 import QtCore


class GLWidget(QGLWidget):
	def __init__(self, parent=None):
		QGLWidget.__init__(self, parent)

		self.parent = parent
		self.initParametres()


	def initParametres(self):
		self.xRot = 0
		self.yRot = 0
		self.zRot = 0
		self.zoom = -15

		self.lightAmbient = [.95, .95, .95, 1.0]
		self.lightDiffuse = [.5, .5, .5, 1.0]
		self.lightPossition = [29.0, 48.0, 37.0, 1.0]

		self.materialSpecular = [.15,.15,.15,.1]
		self.materialShiness = [0.25]

		self.lastPos = QtCore.QPoint()

	def updateScene(self, reset=False):
		if reset:
			self.initParametres()
		self.updateGL()

	def xRotation(self):
		return self.xRot

	def yRotation(self):
		return self.yRot

	def zRotation(self):
		return self.zRot

	def minimumSizeHint(self):
		return QtCore.QSize(50, 50)

	def sizeHint(self):
		return QtCore.QSize(400, 400)

	def setXRotation(self, angle):
		angle = self.normalizeAngle(angle)
		if angle != self.xRot:
			self.xRot = angle
			self.emit(QtCore.SIGNAL("xRotationChanged(int)"), angle)
			self.updateGL()

	def setYRotation(self, angle):
		angle = self.normalizeAngle(angle)
		if angle != self.yRot:
			self.yRot = angle
			self.emit(QtCore.SIGNAL("yRotationChanged(int)"), angle)
			self.updateGL()

	def setZRotation(self, angle):
		angle = self.normalizeAngle(angle)
		if angle != self.zRot:
			self.zRot = angle
			self.emit(QtCore.SIGNAL("zRotationChanged(int)"), angle)
			self.updateGL()

	def initializeGL(self):
		self.bed = self.makePrintingBed()
		self.axis = self.makeAxis()

		glClearDepth(1.0)
		glShadeModel(GL_FLAT)
		glEnable(GL_DEPTH_TEST)
		glDepthFunc(GL_LEQUAL)

		#material
		glMaterialfv(GL_FRONT, GL_SPECULAR, self.materialSpecular)
   		glMaterialfv(GL_FRONT, GL_SHININESS, self.materialShiness)

		#light
		glLightfv(GL_LIGHT0, GL_AMBIENT, self.lightAmbient)
		glLightfv(GL_LIGHT0, GL_DIFFUSE, self.lightDiffuse)
		glLightfv(GL_LIGHT0, GL_POSITION, self.lightPossition)
		glEnable(GL_LIGHT0)

		glColorMaterial ( GL_FRONT_AND_BACK, GL_EMISSION )
		glColorMaterial ( GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
		glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )

		glEnable(GL_COLOR_MATERIAL)
		glEnable(GL_LINE_SMOOTH)
		glEnable( GL_BLEND )

		glEnable(GL_CULL_FACE)


	def paintGL(self):
		glClearColor(0.0, 0.47, 0.62, 1.0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()
		glTranslated(0,-5,0)
		glTranslated(0.0, 0.0, self.zoom)
		glRotated(-90.0, 1.0, 0.0, 0.0)
		glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
		glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
		glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
		glLightfv(GL_LIGHT0, GL_POSITION, self.lightPossition)

		glCallList(self.bed)
		glDisable(GL_DEPTH_TEST)
		glCallList(self.axis)

		glPointSize(5)
		glColor3f(1,1,0)
		glBegin(GL_POINTS)
		glVertex3f(self.lightPossition[0], self.lightPossition[1], self.lightPossition[2])
		glEnd()

		glEnable(GL_DEPTH_TEST)


		'''
		draw scene with all objects
		'''
		glEnable ( GL_LIGHTING )
		if self.parent.controller.model.models:
			for model in self.parent.controller.model.models:
				glCallList(model)
		glDisable( GL_LIGHTING )



	def resizeGL(self, width, height):
		glViewport(0, 0, width, height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(60*((width*1.0)/(height*1.0)), (width*1.0)/(height*1.0), 0.0001, 1000.0)
		glMatrixMode(GL_MODELVIEW)

	def mousePressEvent(self, event):
		self.lastPos = QtCore.QPoint(event.pos())

	def mouseMoveEvent(self, event):
		dx = event.x() - self.lastPos.x()
		dy = event.y() - self.lastPos.y()

#		if event.buttons() & QtCore.Qt.LeftButton:
#			self.setXRotation(self.xRot + 8 * dy)
#			self.setYRotation(self.yRot + 8 * dx)
		if event.buttons() & QtCore.Qt.LeftButton:
			self.setXRotation(self.xRot + 8 * dy)
			self.setZRotation(self.zRot + 8 * dx)

		self.lastPos = QtCore.QPoint(event.pos())

	def wheelEvent(self, event):
		self.zoom = self.zoom + event.delta()/120
		self.parent.parent.statusBar().showMessage("Zoom = %s" % self.zoom)
		self.updateGL()

	def makePrintingBed(self):
		genList = glGenLists(1)
		glNewList(genList, GL_COMPILE)

		glLineWidth(2)


		glBegin(GL_LINES)
		glColor3f(1,1,1)
		for i in xrange(-10, 11, 1):
			glVertex3d(i, 10, 0)
			glVertex3d(i, -10, 0)

			glVertex3d(10, i, 0)
			glVertex3d(-10, i, 0)


		glVertex3d(-10, 10, 0)
		glVertex3d(-10, 10, 20)

		glVertex3d(10, 10, 0)
		glVertex3d(10, 10, 20)

		glVertex3d(10, -10, 0)
		glVertex3d(10, -10, 20)

		glVertex3d(-10, -10, 0)
		glVertex3d(-10, -10, 20)

		glEnd()

		glBegin(GL_LINE_LOOP)

		glVertex3d(-10, 10, 20)
		glVertex3d(10, 10, 20)
		glVertex3d(10, -10, 20)
		glVertex3d(-10, -10, 20)

		glEnd()
		glEndList()

		return genList

	def makeAxis(self):
		genList = glGenLists(1)
		glNewList(genList, GL_COMPILE)

		glLineWidth(5)

		glBegin(GL_LINES)

		glColor3f(1, 0, 0)
		glVertex3d(-10, -10, 0)
		glVertex3d(-9, -10, 0)

		glColor3f(0, 1, 0)
		glVertex3d(-10, -10, 0)
		glVertex3d(-10, -9, 0)

		glColor3f(0, 0, 1)
		glVertex3d(-10, -10, 0)
		glVertex3d(-10, -10, 1)

		glEnd()
		glEndList()

		return genList

	def normalizeAngle(self, angle):
		while angle < 0:
			angle += 360 * 16
		while angle > 360 * 16:
			angle -= 360 * 16
		return angle

