from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap, QImage, QKeySequence
from PyQt6.QtCore import Qt, QPoint, QRect
import sys

class CanvasView(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1200, 800)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.GlobalColor.white)

        self.pen_color = QColor('black')
        self.pen_size = 5
        self.drawing = False
        self.last_point = QPoint()

        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # Zoom variables
        self.scale = 1.0
        self.offset = QPoint(0, 0)

        # Selection variables
        self.selection_start = None
        self.selection_rect = None
        self.selection_pixmap = None
        self.selection_active = False
        self.selection_offset = QPoint(0, 0)
        self.selection_dragging = False

        # Clipboard image paste support
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self.offset)
        painter.scale(self.scale, self.scale)
        painter.drawPixmap(0, 0, self.pixmap)

        # Draw selection rectangle if active
        if self.selection_rect and not self.selection_rect.isNull():
            painter.setPen(QPen(QColor(0, 120, 215), 2, Qt.PenStyle.DashLine))
            painter.drawRect(self.selection_rect)

        # Draw the selected pixmap being dragged
        if self.selection_active and self.selection_pixmap and self.selection_dragging:
            painter.drawPixmap(self.selection_rect.topLeft(), self.selection_pixmap)

    def mousePressEvent(self, event):
        pos = (event.position() - self.offset) / self.scale
        pos = pos.toPoint()
        if event.button() == Qt.MouseButton.LeftButton:
            if self.selection_active and self.selection_rect and self.selection_rect.contains(pos):
                # Start dragging selection
                self.selection_dragging = True
                self.selection_offset = pos - self.selection_rect.topLeft()
            else:
                self.drawing = True
                self.last_point = pos
                self.push_undo()

                # Clear selection if any
                self.clear_selection()

    def mouseMoveEvent(self, event):
        pos = (event.position() - self.offset) / self.scale
        pos = pos.toPoint()
        if self.drawing:
            painter = QPainter(self.pixmap)
            pen = QPen(self.pen_color, self.pen_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(self.last_point, pos)
            self.last_point = pos
            self.update()
        elif self.selection_dragging:
            # Move selection
            new_top_left = pos - self.selection_offset
            self.move_selection(new_top_left)
            self.update()
        elif event.buttons() & Qt.MouseButton.LeftButton:
            # Create selection rect
            if not self.selection_active:
                if self.selection_start is None:
                    self.selection_start = pos
                self.selection_rect = QRect(self.selection_start, pos).normalized()
                self.update()

    def mouseReleaseEvent(self, event):
        pos = (event.position() - self.offset) / self.scale
        pos = pos.toPoint()
        if event.button() == Qt.MouseButton.LeftButton:
            if self.drawing:
                self.drawing = False
            if self.selection_dragging:
                self.selection_dragging = False
                self.finalize_selection_move()
            elif self.selection_rect and not self.selection_active:
                self.create_selection()
            self.selection_start = None

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        angle = event.angleDelta().y()
        # Zoom in/out on cursor
        if modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            # Ctrl+Shift + Scroll => horizontal pan
            delta_x = angle / 120 * 20
            self.offset += QPoint(delta_x, 0)
            self.update()
        elif modifiers == Qt.KeyboardModifier.ControlModifier:
            # Ctrl + Scroll => zoom
            old_scale = self.scale
            if angle > 0:
                self.scale *= 1.1
            else:
                self.scale /= 1.1
            self.scale = max(0.1, min(self.scale, 10))

            # Adjust offset so zoom centers on cursor
            cursor_pos = event.position().toPoint()
            delta = cursor_pos - self.offset
            scale_change = self.scale / old_scale
            self.offset -= delta * (scale_change - 1)
            self.update()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        if event == QKeySequence.StandardKey.Undo or (event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Z):
            self.undo()
        elif event == QKeySequence.StandardKey.Redo or (event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Y):
            self.redo()
        elif event == QKeySequence.StandardKey.Paste or (event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V):
            self.paste_image()
        else:
            super().keyPressEvent(event)

    def push_undo(self):
        self.undo_stack.append(self.pixmap.copy())
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.pixmap.copy())
            self.pixmap = self.undo_stack.pop()
            self.update()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.pixmap.copy())
            self.pixmap = self.redo_stack.pop()
            self.update()

    def set_pen_color(self, color):
        self.pen_color = color

    def paste_image(self):
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()
        if mime.hasImage():
            img = clipboard.image()
            painter = QPainter(self.pixmap)
            painter.drawImage(0, 0, img)
            self.update()

    def clear_selection(self):
        self.selection_rect = None
        self.selection_pixmap = None
        self.selection_active = False
        self.selection_dragging = False

    def create_selection(self):
        if self.selection_rect and not self.selection_rect.isNull():
            self.selection_active = True
            self.selection_pixmap = self.pixmap.copy(self.selection_rect)
            # Clear selected area in main pixmap (fill white)
            painter = QPainter(self.pixmap)
            painter.fillRect(self.selection_rect, Qt.GlobalColor.white)
            self.update()

    def move_selection(self, top_left):
        if not self.selection_pixmap:
            return
        # Limit movement inside canvas
        rect = QRect(top_left, self.selection_pixmap.size())
        if rect.left() < 0:
            rect.moveLeft(0)
        if rect.top() < 0:
            rect.moveTop(0)
        if rect.right() > self.pixmap.width():
            rect.moveRight(self.pixmap.width())
        if rect.bottom() > self.pixmap.height():
            rect.moveBottom(self.pixmap.height())
        self.selection_rect = rect

    def finalize_selection_move(self):
        if not self.selection_pixmap or not self.selection_rect:
            return
        # Paste selection pixmap at new location
        painter = QPainter(self.pixmap)
        painter.drawPixmap(self.selection_rect.topLeft(), self.selection_pixmap)
        self.clear_selection()
        self.update()
