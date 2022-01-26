from psychopy import prefs

import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui, sound

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
        self.fig_center = [-1,20]
        self.fig_select_center = [0,21]
        self.bars_low = []
        self.bars_mid = []#red bars indicating points: [0] will be left, [1] will be right
        self.bars_high = []
        self.move_distance = 76 #number of pixels between locations (distance to move for selection)
        self.select_length = 4 #amount of time subject has to make a decision
        self.image_length = 6 #duration the image stimulus is displayed for each trial
        self.total_reward = 0 #total number of points the subject has earned
        self.result_length = 2 #duration of result screen (you got ___ pts, total pts)
        self.small_reward = None #sounds to play for small and large rewards
        self.big_reward = None
        self.instructions = ['''Now you are going to have a chance to practice the task.''']
        self.trial = 0 #the trial number we are currently on, used for recording events
        self.trial_type = None #the trial type string to be printed out
        self.title = 'Approach Avoidance Conflict'



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
    decision_onset = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['DECISION_ONSET'], decision_onset, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['down']]) #clear response keys that may have been pressed already
    while g.clock.getTime() < g.ideal_trial_start + g.select_length + iti:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException
        key = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['down']]) #get any response keys pressed (just left, right, select)
        if key and not selected:
            if len(key) > 1:
                print 'MULTIPLE KEYS.  SHOULD NOT HAPPEN'
                print key
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
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_LOCATION'], now, now - decision_onset, 1, current_location, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                g.fig_select.pos = [g.fig_select_center[0] + g.move_distance * current_location, g.fig_select_center[1]]
                selected = True
                g.fig_select.draw()
            else: #should only happen when the figure is at one end or the other
                g.fig.draw()
            
            g.win.flip()
    if not selected:
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_LOCATION'], g.clock.getTime(), 'NA', 'NA', current_location, False, g.session_params['parallel_port_address'])    
    return current_location
    
def select_result_display_image(final_location, left_sound, right_sound, left_image, right_image, trial_type):
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
    
def show_reward(left_reward, right_reward, result):
    if result == 0:
        reward_amount = left_reward
        if left_reward > right_reward: #pick the sound to play
            to_play = g.big_reward
        else:
            to_play = g.small_reward #also small when left_reward == right_reward
    else:
        reward_amount = right_reward
        if left_reward < right_reward:
            to_play = g.big_reward
        else:
            to_play = g.small_reward
    g.reward_text_1.setText('You made ' + str(int(reward_amount)) + ' points')
    g.total_reward = g.total_reward + reward_amount
    g.reward_text_2.setText('Total: ' + str(int(g.total_reward)))
    g.reward_text_1.draw()
    g.reward_text_2.draw()
    g.win.flip()
    to_play.play()
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
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + iti)
    #show runway
    final_location = selection_period(trial_type, left_reward, right_reward, start_location, iti)
    #show image
    result = select_result_display_image(final_location, left_sound, right_sound, left_image, right_image, trial_type)
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + iti + g.select_length + g.image_length)
    #show reward points/play sound
    show_reward(left_reward, right_reward, result)
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + iti + g.select_length + g.image_length + g.result_length)
    g.ideal_trial_start = g.ideal_trial_start + iti + g.select_length + g.image_length + g.result_length #update current time for next trial
    #print outcome
    g.this_trial_output = g.this_trial_output + '\n'
 

def load_sounds(sound_files):
    directory = os.path.dirname(__file__)
    left_sounds = []
    right_sounds = []
    for i in range(len(sound_files[0])):
        left_sounds.append(sound.Sound(value=os.path.join(directory,sound_files[0][i]), volume=g.volume))
        right_sounds.append(sound.Sound(value=os.path.join(directory,sound_files[1][i]), volume=g.volume))
    return left_sounds, right_sounds
    
def final_screen():
    #show final screen
    g.final_bar.draw()
    g.final_fill.draw()
    g.win.flip()
    g.final_sound.play()
    if g.total_reward < 50: #pick which ribbon to show
        ribbon = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/honorable_mention.png'), pos=[150,-30], units='pix')
    elif g.total_reward < 100:
        ribbon = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/third.png'), pos=[150,-30], units='pix')
    elif g.total_reward < 150:
        ribbon = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/second.png'), pos=[150,-30], units='pix')
    else:
        ribbon = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/first.png'), pos=[150,-30], units='pix')
    full_idx = 717
    max_pts = 200
    fill_to = g.total_reward * full_idx / max_pts

    for i in range(int(fill_to)): #fill the bar, up to the amount of points the subject earned
        g.final_fill.setSize([g.final_fill.size[0], g.final_fill.size[1] + 1])
        if i % 2 == 0:
            g.final_fill.setPos([g.final_fill.pos[0], g.final_fill.pos[1] + 1])
        if i % 6 == 0:
            continue
        g.final_bar.draw()
        g.final_fill.draw()
        g.congrats.draw()
        g.black_bars[0].draw()
        g.black_bars[1].draw()
        g.black_bars[2].draw()
        g.win.flip()
        
    #draw the ribbon, then wait for 30s or until the user hits escape
    g.final_bar.draw()
    g.final_fill.draw()
    g.black_bars[0].draw()
    g.black_bars[1].draw()
    g.black_bars[2].draw()
    ribbon.draw()
    g.congrats.draw()
    g.msg.setPos([0,-500])
    g.msg.setText("Press enter to continue")
    g.msg.draw()
    g.win.flip()
    event.getKeys(["return"])
    while True:
        if event.getKeys(["return"]):
            break
    g.msg.setPos([0,0])
    g.final_sound.stop() #stop the sound if it's still playing
    #StimToolLib.just_wait(g.clock, g.ideal_trial_start + 30)

def one_instruct_slide(start_loc, this_runway, bar, img, sound, pts, to_play, total_pts):
    #show one instruction slide--don't quit until user hits enter
    g.x.draw()
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.clock.getTime()  + 2)
    selected = False
    current_location = start_loc
    this_runway.draw()
    draw_bars(bar)
    g.fig.pos = [g.fig_center[0] + g.move_distance * current_location, g.fig_center[1]]
    g.fig.draw()
    g.win.flip()
    event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['down'], 'return']) #clear response keys that may have been pressed already
    while True:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException
        key = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['down']]) #get any response keys pressed (just left, right, select)
        if event.getKeys(['return']):
            break
        if key and not selected:
            if len(key) > 1:
                print 'MULTIPLE KEYS.  SHOULD NOT HAPPEN'
                print key
            response_recorded = True
            this_runway.draw()
            draw_bars(bar)
            if key[0] == g.session_params['left'] and current_location > -4:#move selction left unless at end
                current_location = current_location - 1
                g.fig.pos = [g.fig_center[0] + g.move_distance * current_location, g.fig_center[1]]
                g.fig.draw()
            elif key[0] == g.session_params['right'] and current_location < 4: #move selection right unless at end 
                current_location = current_location + 1
                g.fig.pos = [g.fig_center[0] + g.move_distance * current_location, g.fig_center[1]]
                g.fig.draw()
            elif key[0] == g.session_params['down']: #lock in response_recorded
                g.fig_select.pos = [g.fig_select_center[0] + g.move_distance * current_location, g.fig_select_center[1]]
                selected = True
                g.fig_select.draw()
            else: #should only happen when the figure is at one end or the other
                g.fig.draw()
            g.win.flip()
    img.draw()
    g.win.flip()
    sound.play()
    StimToolLib.just_wait(g.clock, g.clock.getTime() + 6)
    
    g.reward_text_1.setText('You made ' + str(int(pts)) + ' points')
    g.reward_text_2.setText('Total: ' + str(int(total_pts)))
    g.reward_text_1.draw()
    g.reward_text_2.draw()
    g.win.flip()
    to_play.play()
    StimToolLib.just_wait(g.clock, g.clock.getTime() + 2)

def show_extra_instructions():
    StimToolLib.show_instructions(g.win, ['''The staff member will now go over the instructions with you for this task.'''])
    #extra trials just for the first instructions--these selection periods will last until the user hits enter
    one_instruct_slide(1, g.runway_0_1, [g.bars_low[1]], g.left_images[0], g.left_sounds[0], 0, g.small_reward, 0)
    
    one_instruct_slide(-3, g.runway_1_0, [g.bars_low[0]], g.left_images[1], g.left_sounds[1], 2, g.big_reward, 2)
    
    one_instruct_slide(0, g.runway_0_0, [g.bars_mid[1]], g.right_images[2], g.right_sounds[2], 4, g.big_reward, 6)

    one_instruct_slide(2, g.runway_1_0, [], g.right_images[3], g.right_sounds[3], 0, g.small_reward, 6)
    
    g.total_reward = 6
    final_screen()
    g.total_reward = 0
def get_vas_ratings():
    g.mouse.setVisible(1)
    top_text = visual.TextStim(g.win, text="Please rate how you feel", units='pix', height=100, color='black', pos=[0,405], wrapWidth=int(1600))
    
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
    
    StimToolLib.show_instructions(g.win, ['''
The following are questions about the task you just completed related to gaining points and/or seeing negative
    or neutral pictures.  For each question, use the mouse to select the response that best describes your
                                                          opinion regarding the task.'''])
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
    StimToolLib.task_end(g)
    return g.status

def run_try():  
    prefs.general['audioLib'] = [u'pyo', u'pygame']
    prefs.general[u'audioDriver'] = [u'ASIO4ALL', u'ASIO', u'Audigy']
    #resk = {'up':'r', 'down':'y', 'left':'left', 'right':'right', 'select':'down'}
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="AAC")
        myDlg.addField('Run Number', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print 'QUIT!'
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
    subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '_' + g.run_params['param_file'])
    #subj_param_file = g.prefix + '.txt'
    if g.run_params['run'] == 'VolumeWorkup.schedule': #volume workup run--just get the volume and save it to a file
        selected_volume = StimToolLib.volume_workup(os.path.join(os.path.dirname(__file__),'media', 'sounds', 'IADSPA', '110_BabyLaugh.aiff'), 0.1)
        StimToolLib.write_var_to_file(subj_param_file, 'volume', selected_volume)
        return
    g.volume = StimToolLib.get_var_from_file(subj_param_file, 'volume') #should have been set by volume workup run first
    if g.volume == None:
        StimToolLib.error_popup('Could not read volume parameter from ' + subj_param_file + '. Did you run the volume workup first?')
    StimToolLib.general_setup(g)
    
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_AAC_Schedule' + str(g.run_params['run']) + '.csv')
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_AAC_T0.csv')
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_AAC_T4.csv')
    trial_types,images,durations,sound_files = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    
    g.x = visual.TextStim(g.win, text="X", units='pix', height=50, color=[-1,-1,-1], pos=[0,0], bold=True)
    #g.resk = resk
    g.left_images = images[0]
    g.right_images = images[1]
    itis = durations[0]
    left_rewards = durations[1]
    right_rewards = durations[2]
    start_locations = durations[3]
    g.left_sounds, g.right_sounds = load_sounds(sound_files)
    g.runway_0_0 = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Runway_0_0.bmp'), interpolate=True)
    g.runway_0_1 = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Runway_0_1.bmp'), interpolate=True)
    g.runway_1_0 = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Runway_1_0.bmp'), interpolate=True)
    g.runway_1_1 = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Runway_1_1.bmp'), interpolate=True)
    g.fig = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/figure.png'), pos=[-1,20], units='pix')
    g.fig_select = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/figure_select.png'), pos=[0,21], units='pix')
    g.reward_text_1 = visual.TextStim(g.win, text="", units='pix', height=50, color='blue', pos=[0,50], bold=True)
    g.reward_text_2 = visual.TextStim(g.win, text="", units='pix', height=50, color='red', pos=[0,-50], bold=True)
    left_bar_loc = [-490, 10]
    right_bar_loc = [491, 10]
    g.bars_low.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_low.png'), pos=left_bar_loc, units='pix'))
    g.bars_low.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_low.png'), pos=right_bar_loc, units='pix'))
    g.bars_mid.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_mid.png'), pos=left_bar_loc, units='pix'))
    g.bars_mid.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_mid.png'), pos=right_bar_loc, units='pix'))
    g.bars_high.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_full.png'), pos=left_bar_loc, units='pix'))
    g.bars_high.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_full.png'), pos=right_bar_loc, units='pix'))
    g.small_reward = sound.Sound(value=os.path.join(os.path.dirname(__file__),'media/sounds/reward/smallReward.aiff'), volume=g.volume)
    g.big_reward = sound.Sound(value=os.path.join(os.path.dirname(__file__),'media/sounds/reward/bigReward.aiff'), volume=g.volume)
    
    #load stimuli for final screen
    g.final_sound = sound.Sound(value=os.path.join(os.path.dirname(__file__),'media/sounds/reward/lastScreen.aiff'), volume=g.volume)
    g.final_bar = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/final_bar_200.png'), pos=[-400,-30], units='pix')
    g.final_fill = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/blue_dot.png'), pos=[-352,-387], units='pix', size=[241,1])
    g.black_bars = []
    g.black_bars.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/black_bar.png'), pos=[-352,-208], units='pix'))
    g.black_bars.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/black_bar.png'), pos=[-352,-28], units='pix'))
    g.black_bars.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/black_bar.png'), pos=[-352,152], units='pix'))
    g.congrats = visual.TextStim(g.win,text="Congratulations!",units='pix',pos=[0,405],color=[-1,-1,-1],height=100,wrapWidth=int(1600), bold=True)
    
    
    
    
    start_time = data.getDateStr()
    #g.prefix = 'AAC-' + g.session_params['SID'] + '-Admin_' + g.session_params['raID'] + '-run_' + str(g.run_params['run']) + '-' + start_time
    fileName = os.path.join(g.prefix + '.csv')
    g.output = open(fileName, 'w')
    sorted_events = sorted(event_types.iteritems(), key=operator.itemgetter(1))
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Schedule File:,' +  schedule_file + ',Post-question file:,T1000_AAC_PostQuestions.csv,Event Codes:,' + str(sorted_events) + ', For ratings the trial number is negative and used to identify the question being rated.  VAS ratings are in the order pleasant-unpleasant-intense and are from 0 (not at all) to 100 (very much) \n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    
    StimToolLib.task_start(StimToolLib.AAC_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #StimToolLib.show_title(g.win, g.title)
    g.win.setColor([1,1,1]) #change background to white
    g.win.flip()
    g.win.flip() #flip twice to change to white
    g.msg.setColor([-1,-1,-1])
        
    if g.run_params['practice']:
        get_vas_ratings()
        StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'AAC_instruct_scheduleP.csv'), g)
        #show_extra_instructions()
    else:
        StimToolLib.show_instructions(g.win, ['Press enter to begin'])
        #StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'AAC_instruct_scheduleS.csv'), g)
        #StimToolLib.show_instructions(g.win, g.instructions)
        
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.ideal_trial_start = g.clock.getTime()  #since we aren't syncing with a scanner pulse, don't reset the clock at the beginning of the real task--times will be reletive to the task start as reported to BIOPAC
    for t,iti,left_r,right_r,start_l,left_s,right_s, left_i, right_i in zip(trial_types, itis, left_rewards, right_rewards, start_locations, g.left_sounds, g.right_sounds, g.left_images, g.right_images):
        g.trial_type = t[0] + t[2] + str(int(left_r))  + str(int(right_r)) + str(int(start_l))
        do_one_trial(t,iti,left_r,right_r,start_l,left_s,right_s, left_i, right_i)
        g.trial = g.trial + 1
        
    final_screen()

    
    if not g.run_params['practice']:
        #try:
        get_vas_ratings()
        get_post_ratings()
        
    
    








