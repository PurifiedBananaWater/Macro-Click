from cgitb import small
from tkinter import filedialog
import os
import cv2
import numpy as np
from PIL import ImageGrab

class ImageSnipper:
    def __init__(self, master):
        self.master = master
        self.screen_image = None
        self.copy = None
        
        # Cropping parameters
        self.refPt = []
        self.cropping = False
        self.done_cropping = False

    def take_screenshot(self):
        return cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2BGR)

    def snip_image(self):
        # Take screenshot of full screen
        self.screen_image = self.take_screenshot()
        self.copy = self.screen_image.copy()
        # Create the 'image' window
        cv2.namedWindow('image')
        
        # Set mouse callback
        cv2.setMouseCallback('image', self.crop_image)
        
        self.done_cropping = False 

        while not self.done_cropping:
            cv2.imshow("image", self.copy)
            key = cv2.waitKey(1)


        x1, y1 = self.refPt[0]
        x2, y2 = self.refPt[1]

        if x1 > x2:
            x1, x2 = x2, x1

        if y1 > y2:   
            y1, y2 = y2, y1
        
        cropped = self.screen_image[y1:y2, x1:x2]

        f = filedialog.asksaveasfilename(defaultextension=".jpg", 
                                    filetypes=[("JPG File", ".jpg")])
        if f is None: # asksaveasfilename return None if dialog closed with "cancel".
            return

        # Extract folder path and filename
        folder_path, file_name = os.path.split(f)  
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Save image
        cv2.imwrite(f, cropped)
        
        cv2.destroyAllWindows()
   
   
    def crop_image(self, event, x, y, flags, param):
        
        # Handle mouse events to crop the image
        if event == cv2.EVENT_LBUTTONDOWN:
            self.refPt = [(x, y)]
            self.cropping = True

        elif event == cv2.EVENT_LBUTTONUP:
            self.refPt.append((x, y))
            self.cropping = False

            # Draw final rectangle
            cv2.rectangle(self.copy, self.refPt[0], self.refPt[1], (0, 255, 0), 2)

        elif event == cv2.EVENT_RBUTTONDOWN:
            self.done_cropping = True  

        elif event == cv2.EVENT_MOUSEMOVE:
            if flags == cv2.EVENT_FLAG_LBUTTON:    
                self.copy = self.screen_image.copy()    
                cv2.rectangle(self.copy, self.refPt[0], (x, y), (0, 255, 0), 2) 


    def find_template(self, image_dir, template_name, match_percentage=0.8):

        if image_dir == "":
            template_path = f"{template_name}.jpg"
        else:
            template_path = f"{image_dir}//{template_name}.jpg"

        if os.path.exists(template_path):
            self.screen_image = cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2BGR)
            self.copy = self.screen_image.copy()

            template = cv2.imread(template_path)
            
            result = cv2.matchTemplate(self.screen_image, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            
            if max_val >= match_percentage:
                c, w, h = template.shape[::-1]
        
                meth = 'cv2.TM_CCOEFF_NORMED'
                method = eval(meth)
        
                # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
                if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                    top_left = min_loc
                else:
                    top_left = max_loc

                bottom_right = (top_left[0] + w, top_left[1] + h)
                
        
                x = top_left[0] + w/2
                y = top_left[1] + h/2

                center = (int(x), int(y))

                return True, center
            else:
                return False, None
        else:
            return False, None
        

    def find_templates_in_folder(self, folder, match_percentage=0.8):
        if folder:
            templates_positions = []
            for file_name in os.listdir(folder):
                if file_name.lower().endswith(".jpg"):
                    found, center = self.find_template(folder, file_name[:-4], match_percentage)
                    if found:
                        templates_positions.append(center)
            
            return templates_positions
                

            
    def detect_color(self, image_dir, color_template_image, smallest_size=(0,0)):
        if image_dir == "":
            image_path = f"{color_template_image}.jpg"
        else:
            image_path = f"{image_dir}//{color_template_image}.jpg"

        screen_grab = self.take_screenshot()

        # Load color template image
        template = cv2.imread(image_path)

        # Convert to HSV
        hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        
        # Extract average HSV values from template
        h, s, v = cv2.split(hsv)
        avg_hsv = (np.average(h), np.average(s), np.average(v))

        # Convert screen grab to HSV
        screen_hsv = cv2.cvtColor(screen_grab, cv2.COLOR_BGR2HSV)
        
        # Define threshold range based on average HSV 
        lower = (int(max(0, avg_hsv[0]-10)), int(max(0, avg_hsv[1]-40)), int(max(0, avg_hsv[2]-40))) 
        upper = (int(min(255, avg_hsv[0]+10)), int(min(255, avg_hsv[1]+40)), int(min(255, avg_hsv[2]+40)))
        
        # Create mask and find contours
        mask = cv2.inRange(screen_hsv, lower, upper)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check if contours were found
        if len(contours) > 0:
            found = True

            # Filter small contours
            centers = []
            for c in contours:
                x,y,w,h = cv2.boundingRect(c)
                if w >= smallest_size[0] and h >= smallest_size[1]:
                    centers.append((x+w//2, y+h//2))


            #If you want to see where it is detecting uncomment the code below:
            ### Get bounding rects and centers
            ##rects = [cv2.boundingRect(c) for c in contours]

            ### Draw rectangles and save image
            ##output = screen_grab.copy()
            ##for x, y, w, h in rects:
                ##cv2.rectangle(output, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            ##cv2.imwrite("output_image.jpg", output)


        else:
            found = False
            centers = []

            
        return found, centers
