
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
        self.x = None #+ fixation stimulus
        self.output = None #The output file
        self.msg = None
        self.ideal_trial_start = None #ideal time the current trial started
        self.this_trial_output = '' #will contain the text output to print for the current trial
        self.left_av_runway = None #runway images with aversive stimuli on the left or right
        self.right_av_runway = None
        #self.resk = None
        self.fig = None #figure images
        self.fig_select = None
        self.fig_center = [0,0.06]
        self.fig_select_center = [0,0.06]
        self.bars_low = []
        self.bars_mid = []#red bars indicating points: [0] will be left, [1] will be right
        self.bars_high = []
        self.move_distance = 0.132 #number of normalized units between locations (distance to move for selection)
        self.select_length = 4 #amount of time subject has to make a decision
        self.image_length = 4 #duration the image stimulus is displayed for each trial 6
        self.total_reward = 0 #total number of points the subject has earned and will be paid
        self.total_reward_shown=0 #total that waill be displayed to subject
        self.result_length = 2 #duration of result screen (you got ___ pts, total pts) 2
        self.small_reward = None #sounds to play for small and large rewards
        self.big_reward = None
        self.instructions = ['''Now you are going to have a chance to practice the task.''']
        self.trial = 0 #the trial number we are currently on, used for recording events
        self.trial_type = None #the trial type string to be printed out
        self.title = 'Approach Avoidance Conflict'
        self.total_trials = 30
        self.joystick = None
  



event_types = {'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'FIXATION_ONSET':3, 
    'DECISION_ONSET':4, 
    'SELECTOR_MOVEMENT':5, 
    'FINAL_LOCATION':6, 
    'OUTCOME_SIDE':7, 
    'NEGATIVE_OUTCOME_SHOWN':8, 
    'POSITIVE_OUTCOME_SHOWN':9, 
    'POINTS_AWARDED':10,
    'TOTAL_POINTS':11,
    'VAS_RATING':12, 
    'POST_RATING':13,
    'TASK_END':StimToolLib.TASK_END}


def draw_bars(bars_to_draw):
    for b in bars_to_draw:
        b.draw()
        
        
def joystick_select(trial_type, left_reward, right_reward, start_location, iti, current_location, response_recorded, selected, this_runway, bars_to_draw, decision_onset,init_button_value):
  
    if not selected:
        sensitivity = 0.15 #the higher this value the more sensitive the joystick will be to hand movement
        response_recorded = True
        this_runway.draw()
        draw_bars(bars_to_draw)
        now=g.clock.getTime()
        joystick_pos = g.joystick.getX()
        j_mark=joystick_pos
        
        #non-pivot method
        if abs(joystick_pos) < 0.220: #tolerance to remove joystick spring offset in 0 position (without this figure will appear to move on its own)
            joystick_pos = 0
        current_location=current_location + (joystick_pos * sensitivity)
    
        #pivot method
        #current_location=(joystick_pos * 4)
        
        if current_location >= 4: # constrain max rightward position at 4
            current_location = 4
        elif current_location <= -4: # constrain max leftward position at -4
            current_location = -4
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SELECTOR_MOVEMENT'], now, now - decision_onset, str(joystick_pos) + ' (' + str(j_mark) + ')' , str(current_location) , None, None)
        g.fig.pos = [g.fig_center[0] + g.move_distance * current_location, g.fig_center[1]]
        g.fig.draw() 
        
        button_value=g.joystick.getButton(g.session_params['joy_forward'])
        if button_value:
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_LOCATION'], now, now - decision_onset, 'locked', current_location, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            g.fig_select.pos = [g.fig_select_center[0] + g.move_distance * current_location, g.fig_select_center[1]]
            selected = True
            g.fig_select.draw()
        
        event.clearEvents() #clear event buffer so that it doesn't get clogged
        g.win.flip()
        
        #now=g.clock.getTime()
        #StimToolLib.just_wait(g.clock,now+0.02)       
    return current_location, selected


def key_select(trial_type, left_reward, right_reward, start_location, iti, current_location, response_recorded, selected, this_runway, bars_to_draw, decision_onset):
    key = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['down']]) #get any response keys pressed (just left, right, select)
    if key and not selected:
        if len(key) > 1:
            print('MULTIPLE KEYS.  SHOULD NOT HAPPEN')
            print(key)
        if not response_recorded: #record time of first button press
            pass
        response_recorded = True
        this_runway.draw()
        draw_bars(bars_to_draw)
        now = g.clock.getTime()
        if key[0] == g.session_params['left'] and current_location > -4:#move selction left unless at end
            current_location = current_location - 1
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SELECTOR_MOVEMENT'], now, now - decision_onset, -1, current_location, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            g.fig.pos = [g.fig_center[0] + g.move_distance * current_location, g.fig_center[1]]
            g.fig.draw()
        elif key[0] == g.session_params['right'] and current_location < 4: #move selection right unless at end 
            current_location = current_location + 1
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SELECTOR_MOVEMENT'], now, now - decision_onset, 1, current_location, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            g.fig.pos = [g.fig_center[0] + g.move_distance * current_location, g.fig_center[1]]
            g.fig.draw()
        elif key[0] == g.session_params['down']: #lock in response_recorded
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_LOCATION'], now, now - decision_onset, 'not locked', current_location, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            g.fig_select.pos = [g.fig_select_center[0] + g.move_distance * current_location, g.fig_select_center[1]]
            selected = True
            g.fig_select.draw()
        else: #should only happen when the figure is at one end or the other
            g.fig.draw()
        g.win.flip()
    return current_location, selected

def selection_period(trial_type, left_reward, right_reward, start_location, iti):
    #handle period where the subject can make a selection
    this_runway = None
    if trial_type == '0 1': #right aversive
        this_runway = g.runway_0_1
    if trial_type == '1 0': #left aversive
        this_runway = g.runway_1_0
    if trial_type == '0 0': #no aversive
        this_runway = g.runway_0_0 
    if trial_type == '1 1': #both aversive
        this_runway = g.runway_1_1
    
    
    bars_to_draw = [] #the point bar(s) to draw
    if left_reward == 2:
        bars_to_draw.append(g.bars_low[0])
    if left_reward == 4:
        bars_to_draw.append(g.bars_mid[0])
    if left_reward == 6:
        bars_to_draw.append(g.bars_high[0])
    if right_reward == 2:
        bars_to_draw.append(g.bars_low[1])
    if right_reward == 4:
        bars_to_draw.append(g.bars_mid[1])
    if right_reward == 6:
        bars_to_draw.append(g.bars_high[1])
        
    
    response_recorded = False
    selected = False #set to true when the subject locks in a response
    current_location = start_location #can be any integer from -4 to 4
    g.fig.pos = [g.fig_center[0] + g.move_distance * current_location, g.fig_center[1]]
    this_runway.draw()
    draw_bars(bars_to_draw)
    g.fig.draw()
    g.win.flip()
    init_button_value=g.joystick.getButton(g.session_params['joy_forward'])
    decision_onset = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['DECISION_ONSET'], decision_onset, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['down']]) #clear response keys that may have been pressed already
    while g.clock.getTime() < g.ideal_trial_start + g.select_length + iti:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException
        
        if g.session_params['joystick']:
            current_location, selected = joystick_select(trial_type, left_reward, right_reward, start_location, iti, current_location, response_recorded, selected, this_runway, bars_to_draw, decision_onset, init_button_value)
        else:
            current_location, selected=key_select(trial_type, left_reward, right_reward, start_location, iti, current_location, response_recorded, selected, this_runway, bars_to_draw, decision_onset)
    if not selected:
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_LOCATION'], g.clock.getTime(), 'NA', 'NA', current_location, False, g.session_params['parallel_port_address'])    
    return current_location
    
def select_result_display_image(final_location, left_sound, right_sound, left_image, right_image, trial_type):
    ## After Changing Output Resolution
    left_image.units = 'pix'
    right_image.units = 'pix'

    left_image.size = [g.session_params['screen_x'], g.session_params['screen_y']]
    right_image.size = [g.session_params['screen_x'], g.session_params['screen_y']]
    #based on the final location, pick which image to display
    #return 0 for left, 1 for right
    probability_right = (final_location + 5) / float(10)
    if random.random() < probability_right: #show the image on the right
        #g.this_trial_output = g.this_trial_output + ',R' 
        right_image.draw()
        g.win.flip()
        right_sound.play()
        retval = 1
        now = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['OUTCOME_SIDE'], now, -1, 'NA', 1, False, g.session_params['parallel_port_address'])
        stim_shown = right_image._imName + ' ' + right_sound.fileName
        if trial_type[2] == '0': #positive on right
            g.this_trial_output = g.this_trial_output + ',0'
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['POSITIVE_OUTCOME_SHOWN'], now, 'NA', 'NA', stim_shown, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        else: 
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['NEGATIVE_OUTCOME_SHOWN'], now, 'NA', 'NA', stim_shown, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            #g.this_trial_output = g.this_trial_output + ',1'
    else: #show the image on the left
        #g.this_trial_output = g.this_trial_output + ',L'
        left_image.draw()
        g.win.flip()
        left_sound.play()
        retval = 0
        now=g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['OUTCOME_SIDE'], now, 'NA', 'NA', -1, False, g.session_params['parallel_port_address'])
        stim_shown = left_image._imName + ' ' + left_sound.fileName
        if trial_type[0] == '0': #positive on left
            g.this_trial_output = g.this_trial_output + ',0'
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['POSITIVE_OUTCOME_SHOWN'], now, 'NA', 'NA', stim_shown, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        else: 
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['NEGATIVE_OUTCOME_SHOWN'], now, 'NA', 'NA', stim_shown, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    return retval
    
def show_reward(left_reward, right_reward, result, left_image, right_image):
    if result == 0:
        reward_amount = left_reward
        left_image.draw()
    else:
        reward_amount = right_reward
        right_image.draw()
    g.reward_text_1.setText('YOU MADE ' + str(int(reward_amount)) + ' CENTS')
    
    g.total_reward = g.total_reward + reward_amount
    g.total_reward_shown = g.total_reward_shown + reward_amount
    StimToolLib.write_var_to_file(g.subj_param_file, 'total_reward', g.total_reward)
    StimToolLib.write_var_to_file(g.subj_param_file, 'total_reward_shown', g.total_reward_shown)
    g.reward_text_2.setText('TOTAL: ' + str(int(g.total_reward_shown)))
    
    g.reward_rect.draw()
    
    g.reward_text_1.draw()
    g.reward_text_2.draw()
    g.win.flip()
    #to_play.play()
    #time_stamp()
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['POINTS_AWARDED'], now, 'NA', 'NA', reward_amount, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TOTAL_POINTS'], now, 'NA', 'NA', g.total_reward, False, g.session_params['parallel_port_address'])
    #g.this_trial_output = g.this_trial_output + ',' + str(int(reward_amount)) + ',' + str(int(g.total_reward))

    
def do_one_trial(trial_type, iti, left_reward, right_reward, start_location, left_sound, right_sound, left_image, right_image):
    #wait for iti
    g.x.draw()
    g.win.flip()
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION_ONSET'], now, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.x.draw()
   
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + iti)
    g.offset=g.joystick.getX()*-1
    #show runway
    final_location = selection_period(trial_type, left_reward, right_reward, start_location, iti)
    #show image
    result = select_result_display_image(final_location, left_sound, right_sound, left_image, right_image, trial_type)
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + iti + g.select_length + g.image_length)
    #show reward points/play sound
    show_reward(left_reward, right_reward, result, left_image, right_image)
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + iti + g.select_length + g.image_length + g.result_length)
    left_sound.stop()
    right_sound.stop()
    g.ideal_trial_start = g.ideal_trial_start + iti + g.select_length + g.image_length + g.result_length #update current time for next trial
    # print outcome
    g.this_trial_output = g.this_trial_output + '\n'
 

def load_sounds(sound_files):
    directory = os.path.dirname(__file__)
    left_sounds = []
    right_sounds = []
    for i in range(len(sound_files[0])):
        left_sounds.append(sound.Sound(value=os.path.join(directory,sound_files[0][i]),volume=g.volume))
        right_sounds.append(sound.Sound(value=os.path.join(directory,sound_files[1][i]),volume=g.volume))
    return left_sounds, right_sounds
    
def final_screen():
    #g.final_sound.play()
    if g.total_reward==g.total_reward_shown:
        g.msg.setText('Congratulations, you\'ve won $' + "{0:.2f}".format(g.total_reward/100) + '!')
    else:
        g.msg.setText('Congratulations, you\'ve won $' + "{0:.2f}".format(g.total_reward/100) +'!\n(This includes your winnings from the trials you repeated.')
    g.msg.draw()
    g.msg.setText('\n\n\n\n\n\nPress the trigger button to continue.')
    g.msg.draw()
    g.win.flip()
    while not g.joystick.getButton(g.session_params['joy_forward']):
        if g.total_reward==g.total_reward_shown:
            g.msg.setText('Congratulations, you\'ve won $' + "{0:.2f}".format(g.total_reward/100) + '!')
        else:
            g.msg.setText('Congratulations, you\'ve won $' + "{0:.2f}".format(g.total_reward/100) +'!\n(This includes your winnings from the trials you repeated.')
        g.msg.draw()
        g.msg.setText('\n\n\n\n\n\nPress the trigger button to continue.')
        g.msg.draw()
        event.clearEvents('joystick')
        g.win.flip()
    g.msg.setPos([0,0])
    #g.final_sound.stop() #stop the sound if it's still playing
    #StimToolLib.just_wait(g.clock, g.ideal_trial_start + 30)

def get_vas_ratings():
    g.mouse.setVisible(1)
    top_text = visual.TextStim(g.win, text="Please rate how you feel", units='norm', height=0.1, color='black', pos=[0,0.7], wrapWidth=int(1.5))
    
    text_1 = visual.TextStim(g.win, text="PLEASANT", units='norm', height=0.05, color='black', pos=[0,0.33], wrapWidth=int(1600))
    scale_1 = visual.RatingScale(g.win, lineColor='Black', marker=visual.TextStim(g.win, text='l', units='norm', color='black'), precision=1, low=0, 
        high=100, textColor='Black', markerStart=50, scale=None, labels=['not at all', 'extremely'], tickMarks=[0,100], showValue=False, pos=(0,0.4), showAccept=False, acceptKeys='z')
    
    text_2 = visual.TextStim(g.win, text="UNPLEASANT", units='norm', height=0.05, color='black', pos=[0,-0.07], wrapWidth=int(1600))
    scale_2 = visual.RatingScale(g.win, lineColor='Black', marker=visual.TextStim(g.win, text='l', units='norm', color='black'), precision=1, low=0, 
        high=100, textColor='Black', markerStart=50, scale=None, labels=['not at all', 'extremely'], tickMarks=[0,100], showValue=False, pos=(0,0), showAccept=False, acceptKeys='z')
    
    text_3 = visual.TextStim(g.win, text="INTENSE", units='norm', height=0.05, color='black', pos=[0,-0.47], wrapWidth=int(1600))
    scale_3 = visual.RatingScale(g.win, lineColor='Black', marker=visual.TextStim(g.win, text='l', units='norm', color='black'), precision=1, low=0, 
        high=100, textColor='Black', markerStart=50, scale=None, labels=['not at all', 'extremely'], tickMarks=[0,100], showValue=False, pos=(0,-0.4), showAccept=False, acceptKeys='z')
    bot_text = visual.TextStim(g.win, text="Press enter when done", units='pix', height=50, color='black', pos=[0,-450], wrapWidth=int(1600))
    vas_start_time = g.clock.getTime()
    while True:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        if event.getKeys(["return"]):
            break
        #item.draw()
        text_1.draw()
        text_2.draw()
        text_3.draw()
        scale_1.draw()
        scale_2.draw()
        scale_3.draw()
        top_text.draw()
        bot_text.draw()
        g.win.flip()
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, -1, 'NA', event_types['VAS_RATING'], now, now - vas_start_time, str(scale_1.getRating()), 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, -2, 'NA', event_types['VAS_RATING'], now, now - vas_start_time, str(scale_2.getRating()), 'NA', False, g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, -3, 'NA', event_types['VAS_RATING'], now, now - vas_start_time, str(scale_3.getRating()), 'NA', False, g.session_params['parallel_port_address'])
    g.mouse.setVisible(0)
    
    
def get_post_ratings():
    
    msg=['''
The following are questions about the task you just completed related to gaining money and/or seeing negative
    or neutral pictures.  For each question, use the mouse to select the response that best describes your
                                                          opinion regarding the task.''']
    text = visual.TextStim(g.win, text=msg, units='norm', height=0.1, color='black', pos=[0,0], wrapWidth=int(1.5))
    g.mouse.setVisible(1)
    response_labels = ('      1\nNot at all', '2\n', '    3\nA little', '4\n', '       5\nQuite a bit', '6\n', '        7\nVery much')
    questions = open(os.path.join(os.path.dirname(__file__),'T1000_AAC_PostQuestions.csv'))
    i = -1 #index of current question
    for line in questions:
        resp,end_time,resp_time = StimToolLib.get_one_rating(line, response_labels, g.win, g.clock)
        StimToolLib.mark_event(g.output, i, 'NA', event_types['POST_RATING'], end_time, resp_time, resp, line.rstrip(), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        i = i - 1
    if int(resp) > 1:
        resp,end_time,resp_time = StimToolLib.get_text_response('Please describe (type) any other strategies used to manage emotions triggered by negative pictures.  Press enter when done.', g.win, g.clock)
        StimToolLib.mark_event(g.output, i, 'NA', event_types['POST_RATING'], end_time, resp_time, resp, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #r = StimToolLib.get_one_rating("When a NEGATIVE picture and sound were displayed, I tried to think about something unrelateed to the picture to distract myself:", response_labels, g.win)
    
def track_run():
    try:
        g.final_run=False
        f=open(g.session_params['task_list'])
        tl=f.read().splitlines()
        aac_runs=[s for s in tl if 'Approach Avoidance Conflict' in str(s)]
        track_version = 1
        count=1
        for i in aac_runs:
            run_version = i.split(':')[1]
            if g.run_params['practice']:
                track_version=0
                break
            elif run_version[4:len(run_version)]=='VolumeWorkup.schedule' or run_version[4:len(run_version)]=='Randomizer.schedule' :
                track_version=0
            elif StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), run_version[4:-9]+'.params'), 'practice'):
                track_version=0       
            elif run_version[4:len(run_version)] == g.run_params['run'] and run_version[4:len(run_version)]!='VolumeWorkup.schedule':
                break
            track_version=track_version+1
            count=count+1
        if count==len(aac_runs):
            g.final_run=True
    except KeyError: #this exception occurs if running task in free mode - set track_version to 1
        track_version = 1
        g.final_run=True
    return track_version
    
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/AAC.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    

    try:
        g.joystick._device.close()
    except:
        pass
   
    StimToolLib.task_end(g)
    return g.status

def run_try():  
    joystick.backend = 'pyglet'
    prefs.general['audioLib'] = ['pyo', 'pygame']
    #prefs.general[u'audioDriver'] = [u'ASIO4ALL', u'ASIO', u'Audigy']
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="AAC")
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
    
    
    #Randomize order of AAC runs in task list (optional, ie if randomizer.schedule is not included in task list AAC runs will run normally in the order they are listed)
    #Randomizer.schedule must be run seperately (ie in a practice or setup task list) before the actual task list for changes to take effect
    if 'Randomizer' in g.run_params['run']:
        f=open(os.path.dirname(os.path.dirname(__file__))+'\\'+g.session_params['study_sf']+g.run_params['scan_tl'])
        #f=open(g.run_params['scan_tl'])
        versions = g.run_params['versions'].split(',')
        random.shuffle(versions)
        lines=f.read().splitlines()
        vidx=0
        lidx=0
        for i in lines:
            if g.run_params['run_id'] in str(i):
                lines[lidx]=i[:-10]+versions[vidx]+'.schedule'
                vidx+=1
            lidx+=1
        f.close()
        f=open(os.path.dirname(os.path.dirname(__file__))+'\\'+g.session_params['study_sf']+g.run_params['scan_tl'],'w') #reopen task list file and overwrite with modified task list
        # print (os.path.dirname(os.path.dirname(__file__))+'\\'+g.session_params['study_sf']+g.run_params['scan_tl']+'8888888888888888888888888888888888')
        #f=open(g.run_params['scan_tl'],'w') #reopen task list file and overwrite with modified task list
        for i in lines:
            f.write(i+'\n')
        f.close()
        return
    
    g.prefix = StimToolLib.generate_prefix(g)
    g.subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '_' + g.run_params['param_file'])
    
    #Volume workup
    #VolumeWorkup.schedule must be run first in order to set g.volume
    g.volume = StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'volume') #should have been set by volume workup run first
    if g.volume == None:
        StimToolLib.error_popup('Could not read volume parameter from ' + g.subj_param_file + '. Did you run the volume workup first?')
   
    StimToolLib.general_setup(g)
    
    #Initialize joystick
    if g.session_params['joystick']:
        nJoysticks=joystick.getNumJoysticks()
        if nJoysticks>0:
            g.joystick = joystick.Joystick(0) 
        else:
            StimToolLib.error_popup("You don't have a joystick connected?")
        
    #PReload stimuli
    trial_types,images,durations,sound_files = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    
    print('TRIALTYPES')
    print(trial_types)
    print('IMAGES')
    print(images)
    print('DURATIONS')
    print(durations)
    print('SOUND FILES')
    print(sound_files)
    g.x = visual.TextStim(g.win, text="X", units='pix', height=50, color=[-1,-1,-1], pos=[0,0], bold=True)
    g.left_images = images[0]
    g.right_images = images[1]
    itis = durations[0]
    left_rewards = durations[1]
    right_rewards = durations[2]
    start_locations = durations[3]
    g.left_sounds, g.right_sounds = load_sounds(sound_files)
    g.runway_0_0 = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Runway_0_0.bmp'), interpolate=True, units='norm', size=(1.85,0.38))
    g.runway_0_1 = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Runway_0_1.bmp'), interpolate=True, units='norm', size=(1.85,0.38))
    g.runway_1_0 = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Runway_1_0.bmp'), interpolate=True, units='norm', size=(1.85,0.38))
    g.runway_1_1 = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Runway_1_1.bmp'), interpolate=True, units='norm', size=(1.85,0.38))
    g.fig = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/figure.png'), pos=[0,0.05], units='norm', size=(0.13,0.35))
    g.fig_select = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/figure_select.png'), pos=[0,0.05], units='norm', size=(0.13,0.37) )
    g.reward_text_1 = visual.TextStim(g.win, text="", units='pix', height=46, color='white', pos=[0,-238], bold=True, wrapWidth=1000)
    g.reward_text_2 = visual.TextStim(g.win, text="", units='pix', height=46, color='white', pos=[0,-291], bold=True, wrapWidth=1000)
    g.reward_rect=visual.Rect(g.win, units='pix', fillColor='black', opacity=0.5, height=138, width=512, pos=[0,-269])
    left_bar_loc = [-0.855,0.02]
    right_bar_loc = [0.855, 0.02]
    g.bars_low.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_low.png'), pos=left_bar_loc, units='norm', size=(0.13,0.32)))
    g.bars_low.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_low.png'), pos=right_bar_loc, units='norm', size=(0.13,0.32)))
    g.bars_mid.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_mid.png'), pos=left_bar_loc, units='norm', size=(0.13,0.32)))
    g.bars_mid.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_mid.png'), pos=right_bar_loc, units='norm', size=(0.13,0.32)))
    g.bars_high.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_full.png'), pos=left_bar_loc, units='norm', size=(0.13,0.32)))
    g.bars_high.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_full.png'), pos=right_bar_loc, units='norm', size=(0.13,0.32)))
    g.congrats = visual.TextStim(g.win,text="Congratulations!",units='pix',pos=[0,405],color=[-1,-1,-1],height=100,wrapWidth=int(1600), bold=True)
    
    track_version = track_run() #track version is an integer value that corresponds to the run's place in this task's run order (in free mode track_version=1)
    
    #Maintain a running total of the reward across runs that will be paid
    reset_total=StimToolLib.get_var_from_file('run_flags.txt', 'AAC_reset_total')
    if reset_total:
        g.total_reward=0
        StimToolLib.write_var_to_file('run_flags.txt', 'AAC_reset_total', False)
        StimToolLib.write_var_to_file(g.subj_param_file, 'total_reward', g.total_reward)
    else:
        g.total_reward=StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'total_reward')

    #Maintain a running total of the reward across runs that is displayed
    recorded_trial_num=StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'trial_num')
    if track_version==1 or track_version==0:
        StimToolLib.write_var_to_file(g.subj_param_file, 'initial_reward', 0)
        initial_reward=0
    elif recorded_trial_num>int(g.total_trials/2-1): #If task is stopped during run after half the trials are complete the reward visible to the subject will carry over, otherwise it's reset to the initial value
        initial_reward=StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'total_reward_shown')
        StimToolLib.write_var_to_file(g.subj_param_file, 'initial_reward', initial_reward)
    else:
        initial_reward=StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'initial_reward')
    g.total_reward_shown=initial_reward
    
    start_time = data.getDateStr()
    fileName = os.path.join(g.prefix + '_R' + str(track_version) +'.csv')
    g.output = open(fileName, 'w')
    StimToolLib.write_var_to_file(g.subj_param_file, 'output_run'+str(track_version), fileName)
    #sorted_events = sorted(event_types.iteritems(), key=operator.itemgetter(1))
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Schedule File:,' +  schedule_file + ',Post-question file:,T1000_AAC_PostQuestions.csv,Event Codes:,' + str(sorted_events) + ', For ratings the trial number is negative and used to identify the question being rated.  VAS ratings are in the order pleasant-unpleasant-intense and are from 0 (not at all) to 100 (very much) \n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')

    g.win.setColor([1,1,1]) #change background to white
    g.win.flip()
    g.win.flip() #flip twice to change to white
    g.msg.setColor([-1,-1,-1])

    StimToolLib.task_start(StimToolLib.AAC_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    
       #JorgeCode
    if g.session_params['study_sf'] == 'PA':
            if g.run_params['practice'] == True:
                StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'instructions_P','AAC_instruct_schedule_PPA.csv'), g)
            else:
                StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'instructions_T','AAC_instruct_schedule_' + str(track_version) + 'PA' + '.csv'), g)    
    
    else:
        if g.run_params['practice']:
            StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'instructions_P','AAC_instruct_schedule_P.csv'), g)
        else:
    #/JorgeCode
            StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'instructions_T','AAC_instruct_schedule_' + str(track_version) + '.csv'), g)


    #Scan code
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    g.win.flip()
       
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.ideal_trial_start = g.clock.getTime()  #since we aren't syncing with a scanner pulse, don't reset the clock at the beginning of the real task--times will be reletive to the task start as reported to BIOPAC
    g.x.draw()
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 8)
    g.ideal_trial_start = g.clock.getTime()
    for t,iti,left_r,right_r,start_l,left_s,right_s, left_i, right_i in zip(trial_types, itis, left_rewards, right_rewards, start_locations, g.left_sounds, g.right_sounds, g.left_images, g.right_images):
        g.trial_type = t[0] + t[2] + '_'+ str(int(left_r))  + str(int(right_r)) + '_'+str(int(start_l))
        StimToolLib.write_var_to_file(g.subj_param_file, 'trial_num', g.trial)
        do_one_trial(t,iti,left_r,right_r,start_l,left_s,right_s, left_i, right_i)
        g.trial = g.trial + 1
  

    if g.final_run:
        final_screen()
    








