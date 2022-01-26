from psychopy import prefs
import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui, sound
from psychopy.hardware import joystick

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.clock = None #global clock used for timing
        self.output = None #The output file
        self.msg = None

event_types = {'INSTRUCT_ONSET':1, 
    'TASK_ONSET':2, 
    'SELECTION_MADE':3,
    'RIGHT_MAX':4,
    'LEFT_MAX':5,
    'TASK_END':StimToolLib.TASK_END}
       
def draw_display():
    g.vol_knob.draw()
    g.vol_msg0.draw()
    g.vol_msg1.draw()
    g.vol_msg2.draw()
    g.vol_msg3.draw()

def volume_workup(sound_file, start_volume):
    
    s = sound.Sound(sound_file)
    possible_options = ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1']
    c = possible_options[int(start_volume * 10):] #don't let the user pick a volume less than the starting volume
    index=0
    last_volume = str(start_volume)
    
    g.win.setColor([-1,-1,-1])
    g.msg.setColor([1,1,1])
    
    g.vol_knob=visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'Images', last_volume +'.png'), units='pix', pos=(23,-180))
    g.vol_msg0 = visual.TextStim(g.win, text="SOUND CHECK", units='pix', color='Yellow', bold=True, pos=(0,190), height=46)
    g.vol_msg1 = visual.TextStim(g.win, text="To increase the volume, push the joystick upward", units='pix', pos=(-435,131), color=([1,1,1]), height=26, alignHoriz='left', wrapWidth=1000)
    g.vol_msg2 = visual.TextStim(g.win, text="To decrease the volume, pull the joystick downward", units='pix', pos=(-435,86), color=([1,1,1]), height =26, alignHoriz='left', wrapWidth=1000)
    g.vol_msg3 = visual.TextStim(g.win, text="To select the volume, press the trigger button.", units='pix', pos=(-435,41), color=([1,1,1]),height=26,alignHoriz='left', wrapWidth=1000)
    
    
    while True:
        
        g.vol_knob.setImage(os.path.join(os.path.dirname(__file__), 'Images', last_volume +'.png'))
        draw_display()
        g.win.flip()
        s.setVolume(float(last_volume) * 0.5)
        s.play()
        now=g.clock.getTime()
        StimToolLib.just_wait(g.clock, now+2)
        
        draw_display()
        g.win.flip()

        while g.joystick.getY()<0.8 and g.joystick.getY()>-0.8 and not g.joystick.getButton(g.session_params['joy_forward']):
            k=event.getKeys('escape')
            if k!=[] and k != None:
                if k[0]=='escape':
                    raise StimToolLib.QuitException()
            event.clearEvents()
            draw_display()
            g.win.flip()
            
        s.stop()
        now=g.clock.getTime()
        if g.joystick.getButton(g.session_params['joy_forward']):
            return float(last_volume) * 0.5
        elif  g.joystick.getY()<-0.8:
            try:
                last_volume=c[index+1]
                index=index+1
            except IndexError:
                g.msg.setText('Maximum volume reached. You can not pick a volume higher than this.')
                g.msg.draw()
                g.win.flip()
                StimToolLib.just_wait(g.clock, now+2.5)
        elif  g.joystick.getY()>0.8:
            if index-1>=0:
                last_volume=c[index-1]
                index=index-1
            else:
                g.msg.setText('Minimum volume reached. You can not pick a volume lower than this.')
                g.msg.draw()
                g.win.flip()
                StimToolLib.just_wait(g.clock, now+2.5)


def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/VW.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1

    g.joystick._device.close() # close device when finished
    StimToolLib.task_end(g)
    return g.status


def run_try():  
    joystick.backend='pyglet'
    prefs.general['audioLib'] = [u'pyo', u'pygame']
    #prefs.general[u'audioDriver'] = [u'ASIO4ALL', u'ASIO', u'Audigy']
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="VW")
        myDlg.addField('Run Number', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            # print 'QUIT!'
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
    fileName = os.path.join(g.prefix + '.csv')
    subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '_' + g.run_params['param_file'])
    g.output= open(fileName, 'w')
    #sorted_events = sorted(event_types.iteritems(), key=operator.itemgetter(1))
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    start_time = data.getDateStr()
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  schedule_file + ",Event Codes:," + str(sorted_events) + '\n')    
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    StimToolLib.general_setup(g)

    nJoysticks=joystick.getNumJoysticks()
    if nJoysticks>0:
        g.joystick = joystick.Joystick(0)
    else:
        StimToolLib.error_popup("You don't have a joystick connected?")
    
    
    StimToolLib.task_start(StimToolLib.VOLUME_WORKUP_CODE, g) #send message that this task is starting
    instruct_onset = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_onset, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    
    if g.run_params['practice']:
        StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'Instructions', 'VW_instruct_schedule_P.csv'), g)
    else:
        StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'Instructions', 'VW_instruct_schedule_1.csv'), g)
    
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    instruct_end=g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end, instruct_end - instruct_onset, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.win.flip()
    g.win.setColor([-1,-1,-1])
    g.msg.setColor([1,1,1])
    
    selected_volume=volume_workup(os.path.join(os.path.dirname(__file__),'110_BabyLaugh.aiff'), 0.1)
    sel_time=g.clock.getTime()
    StimToolLib.write_var_to_file(subj_param_file, 'volume', selected_volume)
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['SELECTION_MADE'], sel_time, sel_time-instruct_end, selected_volume, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    
    g.win.setColor([0,0,0])
    g.msg.setColor([-1,-1,-1])
    g.win.flip()
    
    
    g.msg.setText('Turn off scanner then press Enter')
    g.msg.draw()
    g.win.flip()
    event.waitKeys(keyList=['return'])
    circ = visual.Circle(g.win,units='pix',pos=(0,-100),radius=30,fillColor='red')
    circ.draw()
    g.win.flip()
        
    pressed=False
    #g.joystick = joystick.Joystick(0) 
    g.msg.setText('Move the the joystick all the way right and press the trigger button.')
    g.msg.setColor('red')
    while not pressed:
        g.msg.draw()
        x=g.joystick.getX()
        x_pix=x*g.session_params['screen_x']/2
        circ.pos=(x_pix,-100)
        circ.draw()
        g.win.flip()
        if g.joystick.getButton(g.session_params['joy_forward']):
            pressed=True
            StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['RIGHT_MAX'], sel_time, sel_time-instruct_end, x, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            while g.joystick.getButton(g.session_params['joy_forward']):
                wait_for_release=True
                g.win.flip()
                event.clearEvents()
        event.clearEvents()
    
    g.msg.setColor('Black')
    g.msg.setText('Press enter to continue.')
    g.msg.draw()
    g.win.flip()
    event.waitKeys(keyList=['return'])
    event.clearEvents()
    pressed=False

    g.msg.setText('Move the the joystick all the way left and press the trigger button.')
    g.msg.setColor('blue')
    circ.fillColor='blue'
    while not pressed:
        g.msg.draw()
        x=g.joystick.getX()
        x_pix=x*g.session_params['screen_x']/2
        circ.pos=(x_pix,-100)
        circ.draw()
        g.win.flip()
        if g.joystick.getButton(g.session_params['joy_forward']):
            pressed=True
            StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['LEFT_MAX'], sel_time, sel_time-instruct_end, x, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        event.clearEvents()   
    g.win.setColor([1,1,1])
    g.msg.setColor([-1,-1,-1])
    g.win.flip()
