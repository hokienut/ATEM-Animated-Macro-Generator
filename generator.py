'''
    Generator for ATEM Macros
'''
# ATEM INFO
Profile = {
    'majorVersion': '2',
    'minorVersion': '0',
    'product': 'ATEM 4 M/E Constellation HD'}

SS = '0'
FPS = 30
TRANSITION_SEC = 1.5
TRANSITION_METHOD = 'eo'
TRANSITION_A = 3.0
MACRO_START_NUM = 88

show_animations = False
save_animations = False
save_xml = True
xml_fp = 'export_eo_all.xml'

frames = int(round(FPS * TRANSITION_SEC))

MacroID = {
    'size': 'SuperSourceV2BoxSize',
    'xPosition': 'SuperSourceV2BoxXPosition',
    'yPosition': 'SuperSourceV2BoxYPosition',    
    'left': 'SuperSourceV2BoxMaskLeft',
    'top': 'SuperSourceV2BoxMaskTop',
    'right': 'SuperSourceV2BoxMaskRight',
    'bottom': 'SuperSourceV2BoxMaskBottom',
    'enable': 'SuperSourceV2BoxEnable',
    'source': 'SuperSourceV2BoxInput',
    'fillSource': 'SuperSourceV2ArtFillInput'
    }

# tab = '\t'
tab = ' '*4
def output_frames(boxes, i, reverse=False, method='linear', **kwargs):
    output = ''
    b = dict()
    for box_i, box in boxes.items():
        if reverse and 'end' in box:
            b = {'start':box['end'], 'end':box['start']}
        else:
            b = box

        for key in b['start']:
            if i == 0:
                newPos = b['start'][key]
            elif box.get('end'):
                newPos = interp(b['start'][key], b['end'][key], frames, i, method=method, **kwargs)
            else:
                continue
            output += f'{tab*3}<Op id="{MacroID[key]}" superSource="{SS}" boxIndex="{box_i}" {key}="{newPos:0.6f}"/>\n'
    return output
        
def interp(start, end, frames, i, method='linear', **kwargs):
    move_eqs = {
        'linear':lambda x, *args, **kwargs: x,
        'eieo': lambda x, a=2: (x**a/(x**a + (1-x)**a)),
        'ei': lambda x, a=2: x**a,
        'eo': lambda x, a=2: 1-(1-x)**a
    }
    fun = move_eqs.get(method, lambda x,a: x)
    return start + fun(i/frames, **kwargs) * (end - start)

defaults = {
    'start_name': 'ME2',
    'end_name': '2Box',
    'fillSource': 'ProdMed 2',
    'start_source':'ME2',
    'end_source':'SuperSource',
    'boxes': {
        0:{
            'size':0.85,
            'xPosition':8.5,
            'yPosition':0,
            'left':9,
            'right':9,
            'top':0,
            'bottom':0,
            },
        1:{
            'size':0.56,
            'xPosition':-6.5,
            'yPosition':1.1,
            'left':2,
            'top':0,
            'right':2,
            'bottom':0,
        }
    }
}
fullScreen = {
    'size':1,
    'xPosition':0,
    'yPosition':0,
    'left':0,
    'right':0,
    'top':0,
    'bottom':0,
    }

animations = []
animations.append({
    'start_name': 'ME2',
    'end_name': '2Box',
    'fillSource': 'Camera12',
    'start_source':'Camera14',
    'end_source':'SuperSource',
    'boxes':{
        0:{
            'source':'Camera14',
            'start':fullScreen,
            'end':defaults['boxes'][0],    
        },
        1:{
            'source':'Camera12',
            'start':
            {
                'size':0.3,
                'xPosition':-6.5,
                'yPosition':1.1,
                'left':2,
                'top':0,
                'right':2,
                'bottom':0,
            },  
            'end':defaults['boxes'][1],
        }
    }
})

def generate_macro_pair(a, macroNumber, transition=TRANSITION_METHOD, transition_a=TRANSITION_A, frames=frames):
    tab = ' '*4
    output = ''
    for reverse in range(2):
        name = ' --> '.join([a[key] for key in ['start_name', 'end_name']][::-2*reverse+1])
        output += f'{tab*2}<Macro index="{macroNumber + reverse}" name="{name}" description="">\n'

            # Enable/ Disable Active Boxes
        for x in range(4):
            enable_flag = x in a['boxes']
            output += f'{tab*3}<Op id="SuperSourceV2BoxEnable" superSource="0" boxIndex="{x}" enable="{enable_flag}"/>\n'

            # Set Sources for SuperSource Boxes
        for box_i, box in a['boxes'].items():
                # In case setting source by macro is not desired
            if box.get('source'):
                output += f'{tab*3}<Op id="SuperSourceV2BoxInput" superSource="0" boxIndex="{box_i}" input="{box["source"]}"/>\n'

            # Set Fill Source
        if a.get('fillSource'):
            output += f'{tab*3}<Op id="SuperSourceV2ArtFillInput" superSource="0" input="{a["fillSource"]}"/>\n'

        for i in range(frames+1):
            output += output_frames(a['boxes'], i, reverse=reverse, method=transition, a=transition_a)

            ## Change Sources
            if i == 0: #After ensuring that the initial frame has been set to avoid jumping around on frame 1. 
                    # if reverse:
                    #     output += f'{tab*3}<Op id="ProgramInput" mixEffectBlockIndex="0" input="{a["start_source"]}"/>\n'
                    #     # Reset the SuperSource to the final position for preview if it's no longer in Program
                    #     if a["start_source"] != 'SuperSource':
                    #         output += output_frames(a['boxes'], frames)
                    # else:
                    #     output += f'{tab*3}<Op id="ProgramInput" mixEffectBlockIndex="0" input="SuperSource"/>\n'
                    # I can't think of a reason that you would not want the SuperSource
                    # to be in Program on the first frame of a transition if SuperSource is
                    # handling the animation of all the windows.

                output += f'{tab*3}<Op id="ProgramInput" mixEffectBlockIndex="0" input="SuperSource"/>\n'
                    # output += f'{tab*3}<Op id="MacroSleep" frames="1"/>\n'
                
                # this could probably move to outside of the loop since it only runs on the last frame...
            if i == frames:
                endPreviewInput = 'SuperSource' if reverse else a['start_source']
                output += f'{tab*3}<Op id="PreviewInput" mixEffectBlockIndex="0" input="{endPreviewInput}"/>\n'
                    # output += f'{tab*3}<Op id="MacroSleep" frames="1"/>\n'
                
            output += f'{tab*3}<Op id="MacroSleep" frames="1"/>\n'

        output += f'{tab*2}</Macro>\n'
    return output

if __name__ == '__main__':
    header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    profile_info = 'majorVersion="1" minorVersion="5" product="ATEM Constellation 8K (4K Mode)"'
    profile_info = ' '.join([f'{k}="{v}"'for k,v in Profile.items()])

    for index, a in enumerate(animations):
        macro_number = MACRO_START_NUM + index*2
        output = header + generate_macro_pair(a, macro_number)

    tag = 'MacroPool'
    indent = 1
    allLines = f'{tab*indent}<{tag}>\n{output}\n{tab*indent}</{tag}>'

    tag = 'Profile'
    indent = 0
    allLines = f'{tab*indent}<{tag} {profile_info}>\n{allLines}\n{tab*indent}</{tag}>'

    with open(xml_fp,'w') as f:
        f.write(allLines)

    if show_animations or save_animations:
        from Edit_ATEM_Macro import addMacroPool, visualize_atem_macro2, parse_atem_macro_xml
        xml_str = addMacroPool(xml_fp)
        macros = parse_atem_macro_xml(xml_str)

        # frames = macros[1].get('frames')
        hold_frames = [macros[1].get('frames')[0]]*FPS*1
        frames = macros[0].get('frames') + hold_frames + macros[1].get('frames')

        ani = visualize_atem_macro2(frames)

        if show_animations:
            from matplotlib import pyplot as plt
            plt.show()

        if save_animations:
            ani.save('GIF_output.gif', fps=30)