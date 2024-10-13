import math
import numpy as np
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Line, Rectangle, Color, Ellipse

class Rect(Widget):
    def __init__(self):
        super().__init__()
        self.d = 14
        self.square = []
        self.points = [(200, 200), (200, 400), (400, 400), (400, 200)]
        self.circles = []
        self.line = []
        self.line_white = []
        self.cord_line = []
        self.dragging = None
        with self.canvas:
            
            for i in range(5):
                x, y = list(np.random.randint(10, 600, 2)), list(np.random.randint(10, 600, 2))
                self.cord_line.append((x,y))
                Color(1, 0, 0, 1)
                self.line.append(Line(points= (x, y), width=2))
                Color(1, 1, 1, 1)
                self.line_white.append(Line(points= (x, y), width=2))
            for i, point in enumerate(self.points):
                Color(0, 1, 0, 1)
                self.square.append(Line(points= (point, self.points[i-3])))
                Color(1, 0, 0, 1)
                self.circles.append(Ellipse(pos= (point[0]-self.d/2, point[1]-self.d/2), size= (self.d,self.d)))
    
    def redraw_line(self, i, new_cord):
        if new_cord is not None:
            self.line_white[i].points = (new_cord)
        elif new_cord is None:
            self.line_white[i].points = [[0, 0], [0, 0]]
        
    def on_touch_down(self, touch):
        for i, circle in enumerate(self.circles):
            circle_x = circle.pos[0] + circle.size[0] / 2
            circle_y = circle.pos[1] + circle.size[1] / 2
            distance = math.sqrt((touch.x - circle_x)**2 + (touch.y - circle_y)**2)
            if distance <= circle.size[0] / 2:
                self.dragging = circle
                self.dragging.pos = (touch.x-self.d/2, touch.y-self.d/2)
                for i, circle in enumerate(self.circles):
                    if circle == self.dragging:
                        self.points[i] = (round(touch.x), round(touch.y))
                        self.square[i].points = (self.points[i], self.points[i-3])
                        self.square[i-1].points = (self.points[i-1], self.points[i])
            
    def on_touch_move(self, touch):
        if self.dragging:
            self.dragging.pos = (touch.x-self.d/2, touch.y-self.d/2)
            for i, circle in enumerate(self.circles):
                if circle == self.dragging:
                    self.points[i] = (round(touch.x), round(touch.y))
                    self.square[i].points = (self.points[i], self.points[i-3])
                    self.square[i-1].points = (self.points[i-1], self.points[i])
        
    def on_touch_up(self, touch):
        self.dragging = None  

class CutLine(Widget):
    def __init__(self, info):
        super().__init__()
        self.info = info
        Clock.schedule_interval(self.update, .01)
    
    def cut(self, p1, p2, p3, p4):
        den = (p4[1] - p3[1]) * (p2[0] - p1[0]) - (p4[0] - p3[0]) * (p2[1] - p1[1])
        if den == 0:
            return None
        ua = ((p4[0] - p3[0]) * (p1[1] - p3[1]) - (p4[1] - p3[1]) * (p1[0] - p3[0])) / den
        ub = ((p2[0] - p1[0]) * (p1[1] - p3[1]) - (p2[1] - p1[1]) * (p1[0] - p3[0])) / den
          
        if 0 <= ua <= 1 and 0 <= ub <= 1:
            intersection_x = p1[0] + ua * (p2[0] - p1[0])
            intersection_y = p1[1] + ua * (p2[1] - p1[1])
            return (intersection_x, intersection_y)

        return None
    
    def point_inside(self, point):
        x, y = point
        count = 0
        n = len(self.info.points)
        
        for i in range(n):
            p1 = self.info.points[i]
            p2 = self.info.points[(i+1)%len(self.info.points)]
            if ((p1[1] > y) != (p2[1] > y)) and (x < (p2[0] - p1[0]) * (y - p1[1]) / (p2[1] - p1[1]) + p1[0]):
                count+= 1
                
        return count %2 == 1
    
    def cut_line(self, i):
        point_start = self.info.cord_line[i][0]
        point_end = self.info.cord_line[i][1]
        clipped_start = None
        clipped_end = None
        for j in range(len(self.info.points)):
            p1 = self.info.points[j]
            p2 = self.info.points[(j+1)%len(self.info.points)]
            intersection = self.cut(point_start, point_end, p1, p2)    
            if intersection is not None:
                if clipped_start is None:
                    clipped_start = intersection
                else:
                    clipped_end = intersection
                    
        if clipped_start is not None and clipped_end is not None:
            return [clipped_start, clipped_end]
        
        if self.point_inside(point_start):
            for j in range(len(self.info.points)):
                p1 = self.info.points[j]
                p2 = self.info.points[(j+1)%len(self.info.points)]
                a = self.cut(point_start, point_end, p1, p2)
                if clipped_end is None:
                    clipped_end = a
            clipped_start = point_start
            
        if self.point_inside(point_end):
            clipped_end = point_end
        
        if clipped_start and clipped_end:
            return [clipped_start, clipped_end]
            
        
    def update(self, dt):
        for i in range(len(self.info.line_white)):
            self.info.redraw_line(i, self.cut_line(i))

class MainApp(App):
    def build(self):
        parent = Widget()
        rect = Rect()
        cutLine = CutLine(rect)
        parent.add_widget(cutLine)
        parent.add_widget(rect)
        return parent
    
if __name__ == '__main__':
    MainApp().run()