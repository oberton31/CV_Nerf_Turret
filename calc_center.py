import cv2

# Object holds the position of the center of the face/body in frame
class Calc_Center:
    def __init__ (self):
        self.classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        
    def update (self, frame, frame_center):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        people = self.classifier.detectMultiScale(gray, 1.3, 5, (cv2.CASCADE_DO_CANNY_PRUNING + cv2.CASCADE_FIND_BIGGEST_OBJECT + cv2.CASCADE_DO_ROUGH_SEARCH))
        
        
        if len(people) > 0:
            maxArea = 0
            x = 0
            y = 0
            w = 0
            h = 0
            for (_x,_y,_w,_h) in people:
                #Pick only largest person
                if  _w*_h > maxArea:
                    x = int(_x)
                    y = int(_y)
                    w = int(_w)
                    h = int(_h)
                    maxArea = w*h
            center_x = int(x + (w / 2.0))
            center_y = int(y + (h / 2.0))
            return ((center_x, center_y), people[0])
    
        # If no people  found return center of screen
        return (frame_center, None)