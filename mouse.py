from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor
from PIL import ImageDraw
import helpers

def mousePressEvent(self, event):
    if not self.image: return
    pos = self.view.mapToScene(event.pos())
    x, y = pos.x() / self.scale_factor, pos.y() / self.scale_factor
    self.drawing = True
    self.points = [(x, y)]
    self.last_brush_pos = None
    self.brush_update_counter = 0
    try:
        self.status_message.setText("")
        self.status_label.setStyleSheet(f"background: {helpers.COLORS['status_idle']}; border-radius: 10px;")
    except Exception:
        pass
    if self.tool_combo.currentData() == 1:
        helpers.update_brush_mask(self, x, y, update_display=True)
        
def mouseMoveEvent(self, event):
    pos = self.view.mapToScene(event.pos())
    if not self.drawing or not self.image:
        return
    x, y = pos.x() / self.scale_factor, pos.y() / self.scale_factor
    if self.tool_combo.currentData() == 0: #Lasso
        if len(self.points) > 1:
            prev = self.points[-1]
            line = self.scene.addLine(
                prev[0]*self.scale_factor, prev[1]*self.scale_factor,
                x*self.scale_factor, y*self.scale_factor,
                QPen(QColor("red"), 2)
            )
            self.lasso_lines.append(line)
        self.points.append((x, y))
    else: #Pędzel
        self.brush_update_counter += 1
        helpers.update_brush_mask(self, x, y, update_display=(self.brush_update_counter % 3 == 0))

def mouseReleaseEvent(self, event):
    if not self.image: return
    self.drawing = False
    if self.tool_combo.currentData() == 0 and len(self.points) > 2:
        draw = ImageDraw.Draw(self.mask)
        draw.polygon(self.points, fill=255)
    elif self.tool_combo.currentData() == 1:
        pos = self.view.mapToScene(event.pos())
        x, y = pos.x() / self.scale_factor, pos.y() / self.scale_factor
        helpers.update_brush_mask(self, x, y, update_display=False)
        self.last_brush_pos = None
    helpers.draw_image(self)
    
#===LOGIGA DLA WEJŚCIA NA OBRAZEK MYSZKĄ===#
    #===POJAWI SIĘ KURSON Z KUŁECZKIEM===#
def enterEvent_logic(self, event):
    if self.tool_combo.currentData() == 1 and self.image:
        self.view.viewport().setCursor(helpers.create_brush_cursor(self))
        
def leaveEvent_logic(self, event):
    self.view.viewport().setCursor(Qt.ArrowCursor)
