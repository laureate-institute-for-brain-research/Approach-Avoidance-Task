
import os, random
from psychopy import visual, core, event, data, gui, sound




original = open('AAC_scan_T1000_reorganized_T4.csv', 'r')
original.readline()
original.readline()
original.readline()
output = open('T1000_AAC_T4.csv', 'w')
output.write('TrialTypes,Stimuli,Durations,ExtraArgs\n')
for line in original:
    all_values = line.split(',')
    left_reward = all_values[1]
    right_reward = all_values[2]
    left_image = 'media/' + all_values[3]
    left_sound = all_values[4]
    left_sound = 'media/' + left_sound.split('.')[0] + '.aiff'
    right_image = 'media/' + all_values[5]
    right_sound = all_values[6]
    right_sound = 'media/' + right_sound.split('.')[0] + '.aiff'
    iti = all_values[7]
    start_location = all_values[20]
    left_is_aversive = all_values[21]
    if left_is_aversive == '0':
        trial_type = '0 1'
        t_i = left_image #flip image location (made it easier to make new schedules by hand)
        t_s = left_sound
        left_image = right_image
        left_sound = right_sound
        right_image = t_i
        right_sound = t_s
    if left_is_aversive ==  '1':
        trial_type = '1 0'
    if left_is_aversive == '3':
        trial_type = '0 0'
    output.write(trial_type + ',' + left_image + ' ' + right_image + ',' + iti + ' ' + left_reward + ' ' + right_reward + ' ' + start_location + ',' + left_sound + ' ' + right_sound + '\n')
    