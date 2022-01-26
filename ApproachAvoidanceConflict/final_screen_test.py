
import os, random
from psychopy import visual, core, event, data, gui, sound




win = visual.Window(fullscr=True, screen=1,color=(1,1,1), waitBlanking=True, colorSpace='rgb',winType='pyglet')


def get_one_rating(question, responses, win):
    msg = visual.TextStim(win,text="",units='pix',pos=[0,130],color=[-1,-1,-1],height=50,wrapWidth=int(1600))
    msg.setText(question)
    scale_1 = visual.RatingScale(win, lineColor='Black', precision=1, low=1, high=7, singleClick=True, respKeys=range(1,len(responses) + 1), marker=visual.TextStim(win, text='l', units='norm', color='black'),
        textColor='Black', scale=None, labels=responses,  pos=(0,0), showAccept=False, acceptKeys='z', stretch=2, tickMarks=[1,2,3,4,5,6,7])

    while scale_1.noResponse:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        msg.draw()
        scale_1.draw()
        win.flip()
    return scale_1.getRating()
   
  
 
get_one_rating("When a NEGATIVE picture and sound were displayed, I tried to think about something unrelateed to the picture to distract myself:", ('      1\nNot at all', '2\n', '    3\nA little', '4\n', '       5\nQuite a bit', '6\n', '        7\nVery much'), win)