from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import Qt


class LineTogglerCircle(QGraphicsEllipseItem):
	__RADIUS = 10

	def __init__(self, center_x, center_y, callback, data):
		super(LineTogglerCircle, self).__init__(
			center_x - self.__RADIUS / 2,
			center_y - self.__RADIUS / 2,
			self.__RADIUS,
			self.__RADIUS
		)
		self.__callback = callback
		self.__data = data
		self.setBrush(QBrush(QColor(200, 200, 200)))
		self.setCursor(Qt.PointingHandCursor)

	def mousePressEvent(self, event):
		super(LineTogglerCircle, self).mousePressEvent(event)
		self.__callback(self.__data)


class QubitCircle(QGraphicsEllipseItem):
	__RADIUS = 19

	def __init__(self, q_id):
		super(QubitCircle, self).__init__(0, 0, self.__RADIUS, self.__RADIUS)
		self.setBrush(QBrush(QColor(100, 200, 100, 199)))
		text = QGraphicsTextItem(str(q_id), self)
		text.setPos(0, -5)

	def setPos(self, x, y):
		super(QubitCircle, self).setPos(x - self.__RADIUS / 2, y - self.__RADIUS / 2)


class TextValueChanger(QGraphicsTextItem):
    def __init__(self, x, y):
        super(TextValueChanger, self).__init__()
        self.setPos(x, y)
        self.setCursor(Qt.PointingHandCursor)
        self.__callback = None
        self.__data = None

    def mousePressEvent(self, event):
        inc = lambda i: i + 0.5
        dec = lambda i: i - 0.5
        if event.button() == Qt.LeftButton:
            self.__callback(self.__data, inc)
        elif event.button() == Qt.RightButton:
            self.__callback(self.__data, dec)

    def set_callbacks(self, callback, data):
        self.__callback = callback
        self.__data = data


class CrossbarGrid(QGraphicsView):
    __OUTER_MARGIN = 30
    __SQUARE_WIDTH = 40

    __Y_PADDING = -7
    __X_PADDING = -12

    __PEN_WIDTH = 3
    __GRAY_PEN = QPen(QBrush(QColor(100, 100, 100)), 2)
    __RED_PEN = QPen(QBrush(QColor(200, 100, 100)), __PEN_WIDTH)
    __BLUE_PEN = QPen(QBrush(QColor(100, 100, 200)), __PEN_WIDTH)
    __RED_PEN_DASHED = QPen(QBrush(QColor(200, 100, 100)), __PEN_WIDTH, Qt.DotLine)
    __BLUE_PEN_DASHED = QPen(QBrush(QColor(100, 100, 200)), __PEN_WIDTH, Qt.DotLine)

    def __init__(self, parent, model):
        super(CrossbarGrid, self).__init__(parent)
        self.__model = model
        m, n, d = model.get_line_dimensions()
        self.__height = 2 * self.__OUTER_MARGIN + m * self.__SQUARE_WIDTH
        self.__width = 2 * self.__OUTER_MARGIN + n * self.__SQUARE_WIDTH
        self.setFixedSize(self.__width, self.__height)
        self.__scene = QGraphicsScene(self)
        self.__h_line_items = self.__draw_h_lines(m)
        self.__v_line_items = self.__draw_v_lines(n)
        self.__d_values = self.__draw_d_lines(d)
        self.setScene(self.__scene)
        self.__qubits = {}
        for q_id, _ in self.__model.iter_qubits_positions():
            self.__qubits[q_id] = QubitCircle(q_id)
            self.__scene.addItem(self.__qubits[q_id])
        self.__model.subscribe(self)

    def __draw_h_lines(self, count):
        line_items = []
        for i in range(count):
            x1 = self.__OUTER_MARGIN
            y1 = self.__OUTER_MARGIN + i * self.__SQUARE_WIDTH + self.__SQUARE_WIDTH / 2
            x2 = self.__width - self.__OUTER_MARGIN
            y2 = y1

            line = QGraphicsLineItem(x1, y1, x2, y2)
            circle = LineTogglerCircle(x2, y2, self.__model.toggle_h_line, i)

            line_items.append(line)
            self.__scene.addItem(line)
            self.__scene.addItem(circle)
        return line_items

    def __draw_v_lines(self, count):
        line_items = []
        for i in range(count):
            x1 = self.__OUTER_MARGIN + i * self.__SQUARE_WIDTH + self.__SQUARE_WIDTH / 2
            y1 = self.__OUTER_MARGIN
            x2 = x1
            y2 = self.__width - self.__OUTER_MARGIN

            line = QGraphicsLineItem(x1, y1, x2, y2)
            circle = LineTogglerCircle(x1, y1, self.__model.toggle_v_line, i)

            line_items.append(line)
            self.__scene.addItem(line)
            self.__scene.addItem(circle)
        return line_items

    def __draw_d_lines(self, count):
        value_items = []
        for i in range(count):
            if i <= count / 2:
                x1 = self.__OUTER_MARGIN
                y1 = self.__OUTER_MARGIN + (i + 2) * self.__SQUARE_WIDTH
                x2 = self.__OUTER_MARGIN + (i + 2) * self.__SQUARE_WIDTH
                y2 = self.__OUTER_MARGIN
                value_changer = TextValueChanger(x1 - 15, y1 + self.__Y_PADDING)
            else:
                x1 = self.__width - self.__OUTER_MARGIN
                y1 = self.__OUTER_MARGIN + (i + (1 - count) / 2) * self.__SQUARE_WIDTH
                x2 = self.__OUTER_MARGIN + (i + (1 - count) / 2) * self.__SQUARE_WIDTH
                y2 = self.__height - self.__OUTER_MARGIN
                value_changer = TextValueChanger(x2 + self.__X_PADDING, y2 - self.__OUTER_MARGIN / 2 + 9)
            value_changer.set_callbacks(self.__model.change_d_line, i)
            line = QGraphicsLineItem(x1, y1, x2, y2)
            line.setPen(self.__GRAY_PEN)

            value_items.append(value_changer)
            self.__scene.addItem(line)
            self.__scene.addItem(value_changer)
        return value_items

    def notified(self):
        for i in range(len(self.__h_line_items)):
            pen = self.__BLUE_PEN_DASHED if self.__model.h_barrier_down(i) else self.__BLUE_PEN
            self.__h_line_items[i].setPen(pen)
        for i in range(len(self.__v_line_items)):
            pen = self.__RED_PEN_DASHED if self.__model.v_barrier_down(i) else self.__RED_PEN
            self.__v_line_items[i].setPen(pen)
        for i in range(len(self.__d_values)):
            self.__d_values[i].setPlainText(str(self.__model.d_line_value(i)))
        for q_id, position in self.__model.iter_qubits_positions():
            y = self.__OUTER_MARGIN + (position[0] + 1) * self.__SQUARE_WIDTH
            x = self.__OUTER_MARGIN + (position[1] + 1) * self.__SQUARE_WIDTH
            self.__qubits[q_id].setPos(x, y)
        self.update()
