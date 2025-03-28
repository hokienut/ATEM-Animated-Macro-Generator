fps = 30
transition_seconds = 0.4

frames = fps * transition_seconds
template = {
    'start_name':'',
    'end_name':'',
    'fillSource':'Color1',
    'start_source':'Camera3',
    'end_source':'SuperSource',
    'boxes':{
        0:{
            'source':'Camera2',
            'start':{
                'size':0.68,
                'xPosition':-27,
                'yPosition':0,
                'left':0,
                'top':0,
                'right':0,
                'bottom':0,
            },
            'end':{
                'size':0.68,
                'xPosition':-27,
                'yPosition':0,
                'left':0,
                'top':0,
                'right':0,
                'bottom':0,
            },
        },
        1:{
            'source':'Camera3',
            'start':{
                'size':1.0,
                'xPosition':0,
                'yPosition':0,
                'left':0,
                'top':0,
                'right':0,
                'bottom':0,
            },
            'end':{
                'size':0.68,
                'xPosition':11,
                'yPosition':0,
                'left':8,
                'top':0,
                'right':8,
                'bottom':0,
                },
        }
    },
}

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
tab = '    '
def output_frames(boxes, i, method='linear'):
    output = ''
    for box_i, box in boxes.items():
        for key in box['start']:
            if i == 0:
                newPos = box['start'][key]
            elif 'end' in box:
                newPos = interp(box['start'][key], box['end'][key], frames, i, method=method)
            else:
                continue
            output += f'{tab*3}<Op id="{MacroID[key]}" superSource="0" boxIndex="{box_i}" {key}="{newPos:0.4f}"/>\n'
    return output

def get_frame_range(frames,reverse):
    if reverse:
        return reversed(range(0,int(frames)+1))
    return range(0,int(frames)+1)
        
move_eqs = {
    'linear':lambda x, a=2: x,
    'eieo': lambda x, a=2: (x**a/(x**a + (1-x)**a)),
    'ei': lambda x, a=2: x**a,
    'eo': lambda x, a=2: 1-(1-x)**a
}
def interp(start, end, frames, i, method='linear'):
    fun = move_eqs.get(method, lambda x: x)

    return start + fun(i/frames) * (end - start)

defaults = {
    'start_name': 'ME2',
    'end_name': '2Box',
    'fillSource': 'ProdMed 2',
    'start_source':'ME2',
    'end_source':'SuperSource',
    'boxes': {
        0:{
            'size':0.81,
            'xPosition':7.44,
            'yPosition':0,
            'left':7,
            'right':7,
            'top':0,
            'bottom':0,
            },    
        },
        1:{
            'size':0.56,
            'xPosition':-6.13,
            'yPosition':0,
            'left':2,
            'top':0,
            'right':2,
            'bottom':0,
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
    'fillSource': 'ProdMed 2',
    'start_source':'ME2',
    'end_source':'SuperSource',
    'boxes':{
        0:{
            'source':'ME2',
            'start':fullScreen,
            'end':defaults['boxes'][0],    
        },
        1:{
            'source':'ProdMed 1',
            'start':defaults['boxes'][1],
            'end':defaults['boxes'][1],  
        }
    }
})


output = ''

reverse = False
macroNumber = 88
for index, a in enumerate(animations):
    for reverse in range(2):
        name = ' --> '.join([x[key] for key in ['start_name', 'end_name']][::-2*reverse+1])
        output += f'{tab*2}<Macro index="{macroNumber + index*2 + reverse}" name="{name}" description="">\n'

        for x in range(0,4):
            enable_flag = x in a['boxes']
            f'{tab*3}<Op id="SuperSourceV2BoxEnable" superSource="0" boxIndex="{x}" enable="{enable_flag}"/>\n'
            
        for box_i, box in a['boxes'].items():
            output += f'{tab*3}<Op id="SuperSourceV2BoxInput" superSource="0" boxIndex="{box_i}" input="{box["source"]}"/>\n'

        output += f'{tab*3}<Op id="SuperSourceV2ArtFillInput" superSource="0" input="{a["fillSource"]}"/>\n'

        for i in  get_frame_range(frames,reverse):
            output += output_frames(a['boxes'],i)
            output += f'{tab*3}<Op id="MacroSleep" frames="1"/>\n'

            ## Change Sources
            if i == 0: #After ensuring that the initial frame has been set to avoid jumping around on frame 1. 
                if not reverse:
                    output += f'{tab*3}<Op id="ProgramInput" mixEffectBlockIndex="0" input="SuperSource"/>\n'
                else:
                    output += f'{tab*3}<Op id="ProgramInput" mixEffectBlockIndex="0" input="{a["start_source"]}"/>\n'
                    # Reset the SuperSource to the final position for preview if it's no longer in Program
                    if a["start_source"] != 'SuperSource':
                        output += output_frames(a['boxes'],frames)
                output += f'{tab*3}<Op id="MacroSleep" frames="1"/>\n'
            
            if i == frames:
                if not reverse:
                    output += f'{tab*3}<Op id="PreviewInput" mixEffectBlockIndex="0" input="{a["start_source"]}"/>\n'
                if reverse:
                    output += f'{tab*3}<Op id="PreviewInput" mixEffectBlockIndex="0" input="SuperSource"/>\n'

                output += f'{tab*3}<Op id="MacroSleep" frames="1"/>\n'
            
        output += f'{tab*2}</Macro>\n'

with open('export2.xml','w') as f:
    f.write(output)