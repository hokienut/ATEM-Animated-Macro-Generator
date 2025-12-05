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

SCRN_SIZE_X = 16*2
SCRN_SIZE_Y = 9*2

def parse_atem_macro_xml(xml_string):
    """
    Parses an ATEM macro XML string and extracts SuperSource box positions, sizes, and masks.

    Args:
        xml_string (str): The XML string representing the ATEM macro.

    Returns: [macros {index, name, description, frames:[{...}]]
        list: A list of dictionaries, where each dictionary contains macro info and frames which is
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
    boxes = [{key: patches.Rectangle((0,0),0,0,
                                     linewidth=1,
                                     color=f'C{i}',
                                     alpha=alpha[key],
                                     zorder=4-i) 
                                     for key in ['rect','mask']} for i in range(4)]
    
    for box in boxes:
        for art in box.values():
            ax.add_patch(art)
    
    size_x = SCRN_SIZE_X
    size_y = SCRN_SIZE_Y
    
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
                
    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=1000/30, repeat_delay=2000)
    # plt.show()
    return ani
        
def addMacroPool(fp):
    allLines = readMacro(fp)
    tag = 'MacroPool'
    allLines = f'{" "*4}<{tag}>\n{allLines}\n{" "*4}</{tag}>'
    return allLines

def readMacro(fp):
    with open(fp, 'r') as f:
         allLines = f.read()
    return allLines

if __name__ == '__main__':
    # fp = r'C:\Local Repo\ATEM-Animated-Macro-Generator\export_eo.xml'
    # fp = 'export_eo.xml'
    fp = 'macro_export.xml'
    # xml_str = addMacroPool(fp)
    xml_str = readMacro(fp)

    macros = parse_atem_macro_xml(xml_str)
    # frames = macros[1].get('frames')
    hold_frames = [macros[1].get('frames')[0]]*30
    frames = macros[0].get('frames') + hold_frames + macros[1].get('frames')
    ani = visualize_atem_macro2(frames)
    plt.show()
    # ani.save('GIF_output.gif', fps=30)