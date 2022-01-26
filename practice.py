
from psychopy import visual, event

win = visual.Window([400,400])
msg = visual.TextStim(win, text='press a key\n<esc> to quit')
msg.draw()
win.flip()

k = ('f', 0)
print k[0]
print k[1]
count = 0
while k[0] not in ['escape', 'esc']:
    k = event.getKeys(timeStamped=True)
    print k
    print k[0][1]
    #print k[0][0]
    #print k[0][1]
    
    
    count += 1
