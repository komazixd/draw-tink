from PyQt6.QtGui import QPainterPath
from PyQt6.QtCore import QRectF

def heart_path(rect: QRectF) -> QPainterPath:
    path = QPainterPath()
    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
    path.moveTo(x + w / 2, y + h / 5)
    path.cubicTo(x + w / 2, y, x, y, x, y + h / 3)
    path.cubicTo(x, y + h * 2 / 3, x + w / 2, y + h * 4 / 5, x + w / 2, y + h)
    path.cubicTo(x + w / 2, y + h * 4 / 5, x + w, y + h * 2 / 3, x + w, y + h / 3)
    path.cubicTo(x + w, y, x + w / 2, y, x + w / 2, y + h / 5)
    path.closeSubpath()
    return path
