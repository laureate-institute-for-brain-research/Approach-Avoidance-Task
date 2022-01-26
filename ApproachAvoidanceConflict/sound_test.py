from psychopy import prefs
import sys, os, ctypes
prefs.general['audioLib'] = [u'pyo', u'pygame']
#prefs.general['audioLib'] = [u'pygame']
from psychopy import sound, core, visual
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) #add directory up one level to search path
#import StimToolLib
lib_dll = ctypes.windll.LoadLibrary(os.path.join(os.path.dirname(__file__), '..', 'inpout32.dll'))

settings_file = os.path.join(os.path.dirname(__file__), '..', 'Default.params')
#parallel_address = StimToolLib.get_var_from_file(settings_file, 'parallel_port_address')


prefs.general[u'audioDriver'] = [u'ASIO4ALL', u'ASIO', u'Audigy']

s = sound.Sound(value='SS_50ms.wav', volume=0.1)
#s = sound.Sound(value='media/sounds/reward/lastScreen.wav')

win = visual.Window(fullscr=False, screen=1,color=(-1,-1,-1), waitBlanking=True, colorSpace='rgb',winType='pyglet', allowGUI=False)
x = visual.TextStim(win, text="X", units='pix', height=50, color=[1,1,1], pos=[0,0], bold=True)    


for i in range(20):
    if i % 2 == 0:
        x.draw()
    
    #core.wait(0.4)
    win.flip()
    s.play()
    #lib_dll.Out32(parallel_address, 1)
    #core.wait(0.05)
    #lib_dll.Out32(parallel_address, 0)
    core.wait(1)

win.close()
core.quit()