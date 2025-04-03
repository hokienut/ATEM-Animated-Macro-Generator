import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation

MacroID = {
    'size': 'SuperSourceV2BoxSize',
    'xPosition': 'SuperSourceV2BoxXPosition',
    'yPosition': 'SuperSourceV2BoxYPosition',    
    'left': 'SuperSourceV2BoxMaskLeft',
    'top': 'SuperSourceV2BoxMaskTop',
    'right': 'SuperSourceV2BoxMaskRight',
    'bottom': 'SuperSourceV2BoxMaskBottom'
    }
MacroVal = {v:k for k,v in MacroID.items()}

class frame():
    def __init__(self):
        self.boxes = {}

class box():
    def __init__(self, xPosition=0, yPosition=0, size=1, left=0, right=0, top=0, bottom=0):
        self.id = None
        self.source = None
        self.enabled = False
        self.set(xPosition, yPosition, size, left, right, top, bottom)

        # I think these should come from some global variable or Parent or Super class
        # Basically stating that the screen size should come from a parent class
        self.scn_size_x = 16*2
        self.scn_size_y = 9*2

    def __str__(self):
        return f'xPosition: {self.xPosition}, yPosition: {self.yPosition}, size: {self.size}, left: {self.left}, right: {self.right}, top: {self.top}, bottom: {self.bottom}'
    
    def __repr__(self):
        return f'xPosition: {self.xPosition}, yPosition: {self.yPosition}, size: {self.size}, left: {self.left}, right: {self.right}, top: {self.top}, bottom: {self.bottom}' 
    
    def set(self, xPosition=0, yPosition=0, size=1, left=0, right=0, top=0, bottom=0):
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.size = size
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def reset(self):
        self.xPosition = 0
        self.yPosition = 0
        self.size = 1
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0

    def update(self, box):
        self.xPosition = box.xPosition
        self.yPosition = box.yPosition
        self.size = box.size
        self.left = box.left
        self.right = box.right
        self.top = box.top
        self.bottom = box.bottom

    def crop(self, edge, amount=1):
        if edge == 'left':
            self.left += amount
        elif edge == 'right':
            self.right += amount
        elif edge == 'top':
            self.top += amount
        elif edge == 'bottom': 
            self.bottom += amount
    
    def nudge_size(self, amount=0.05):
        self.size += amount

    def nudge_position(self, x=1, y=1):
        self.xPosition += x
        self.yPosition += y

    def set_position(self, x=1, y=1):
        self.xPosition = x
        self.yPosition = y

    def set_size(self, size=1):
        self.size = size

    def set_mask(self, left=0, right=0, top=0, bottom=0):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def get_rectangles(self):
        'Calculate rectangle coordinates for the original box, and the masked box'
        rect_x = self.xPosition - (self.scn_size_x*self.size / 2)
        rect_y = self.yPosition - (self.scn_size_y*self.size / 2)
        rect_width = self.size*self.scn_size_x
        rect_height = self.size*self.scn_size_y

        'Calculate mask coordinates'
        mask_x = rect_x + self.left*self.size
        mask_y = rect_y + self.bottom*self.size
        mask_width = rect_width - (self.right + self.left)*self.size
        mask_height = rect_height - (self.bottom + self.top)*self.size

        return {
            'rect': (rect_x, rect_y, rect_width, rect_height),
            'mask': (mask_x, mask_y, mask_width, mask_height)},

    
def parse_atem_macro_xml(xml_string):
    """
    Parses an ATEM macro XML string and extracts SuperSource box positions, sizes, and masks.

    Args:
        xml_string (str): The XML string representing the ATEM macro.

    Returns: [macros {index, name, description, frames:[]]
        list: A list of dictionaries, where each dictionary contains a macro info and frames which is
              a list of dictionaries, where each dictionary represents a frame of the animation.
              Each frame dictionary contains box information (xPosition, yPosition, size, masks)
              for each box (0-3).
    """

    root = ET.fromstring(xml_string)
    macros = []
    for macro in root.findall('.//Macro'):
        frames = []
        current_frame = {}
        for op_element in macro.iter('Op'):
            op_id = op_element.get("id")
            # super_source = int(op_element.get("superSource")) if op_element.get("superSource") else None
            box_index = int(op_element.get("boxIndex")) if op_element.get("boxIndex") else None
            if op_id in MacroVal:
                key = MacroVal.get(op_id)
                if box_index is not None:
                    if box_index not in current_frame:
                        current_frame[box_index] = {}
                    current_frame[box_index][key] = float(op_element.get(key))
                    
            elif op_id == "MacroSleep":
                frames.append(current_frame.copy())
                current_frame = {} # Reset current frame
        macros.append({**macro.attrib, 'frames':frames})

    return macros

def visualize_atem_macro2(frames):
    fig = plt.figure('animation', figsize=(16/2, 9/2))
    fig.clf()
    ax = fig.add_subplot(111)
    
    ax.grid(False)
    ax.tick_params(labelbottom=False, labeltop=False, labelleft=False, labelright=False,
                bottom=False, top=False, left=False, right=False)
    ax.set_facecolor((0.2,0.2,0.22))
    fig.tight_layout()
    
    alpha = {'rect':0.1, 'mask':1.0}
    boxes = [{key: patches.Rectangle((0,0),0,0,linewidth=1,color=f'C{i}',alpha=alpha[key],zorder=4-i) for key in ['rect','mask']} for i in range(4)]
    
    for box in boxes:
        for art in box.values():
            ax.add_patch(art)
    
    size_x = 16*2
    size_y = 9*2
    
    ax.set_xlim(-size_x/2,size_x/2)  # Adjust based on your xPosition values
    ax.set_ylim(-size_y/2,size_y/2)  # Adjust based on your yPosition values
    
    box = {}
    
    def update(i):
        frame_data = frames[i]
        for box_index, box_info in frame_data.items():
            x = box_info.get("xPosition", 0.0)
            y = box_info.get("yPosition", 0.0)
            size = box_info.get("size", 1.0)
            mask_left = box_info.get("left", 0.0)
            mask_right = box_info.get("right", 0.0)
            mask_top = box_info.get("top", 0.0)
            mask_bottom = box_info.get("bottom", 0.0)
            
            # Calculate rectangle coordinates
            rect_x = x - (size_x*size / 2)
            rect_y = y - (size_y*size / 2)
            rect_width = size*size_x
            rect_height = size*size_y
    
            # Apply masking
            mask_x = rect_x + mask_left*size
            mask_y = rect_y + mask_bottom*size
            mask_width = rect_width - (mask_right + mask_left)*size
            mask_height = rect_height - (mask_bottom + mask_top)*size
    
            # Draw the rectangles
            boxes[box_index]['rect'].set_bounds(rect_x, rect_y, rect_width, rect_height)
            boxes[box_index]['mask'].set_bounds(mask_x, mask_y, mask_width, mask_height)
            # box[box_index]['rect'] = patches.Rectangle((rect_x, rect_y), rect_width, rect_height, linewidth=1, edgecolor=c, facecolor=c, alpha=.3)
            # box[box_index]['mask'] = patches.Rectangle((mask_x, mask_y), mask_width, mask_height, linewidth=1, edgecolor=c2, facecolor=c2, alpha=.8)
            
            # for art in box[box_index].values():
            #     ax.add_patch(art)
                
    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=1000/30, repeat_delay=2000)
    # plt.show()
    return ani
        
def addMacroPool(fp):
    with open(fp, 'r') as f:
        allLines = f.read()
    tag = 'MacroPool'
    allLines = f'{" "*4}<{tag}>\n{allLines}\n{" "*4}</{tag}>'
    return allLines

if __name__ == '__main__':
    # fp = r'C:\Local Repo\ATEM-Animated-Macro-Generator\export_eo.xml'
    fp = 'export_eo.xml'
    xml_str = addMacroPool(fp)
    macros = parse_atem_macro_xml(xml_str)
    # frames = macros[1].get('frames')
    hold_frames = [macros[1].get('frames')[0]]*30
    frames = macros[0].get('frames') + hold_frames + macros[1].get('frames')
    ani = visualize_atem_macro2(frames)
    plt.show()
    # ani.save('GIF_output.gif', fps=30)