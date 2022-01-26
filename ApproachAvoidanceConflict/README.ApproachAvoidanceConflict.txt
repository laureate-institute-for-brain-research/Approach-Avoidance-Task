README for the Approach Avoidance Conflict Task

*****************************************************************SUMMARY**************************************************************************

This task presents the subject with a series of choices between two different outcomes.
Each outcome has a valence and a point reward associated with it.
The valence can be positive or negative and indicates whether a positive or negative image/sound pair will be played.
Subjects are instructed to select their relative preference between the two possible outcomes for each trial, and their selection determines the probability of each happening.
They can control the probability of each outcome from 10% to 90%, but cannot determine one outcome with certainty.

Four instruction trials occur at the beginning of the practice run.
A script for the instruction slides can be found in XXXXX.

*****************************************************************TRIAL STRUCTURE******************************************************************

[instructions (four different trials are shown) ] ->
^                                               ^  
INSTRUCT_ONSET                              TASK_ONSET
                      
                      
       SELECTOR_MOVEMENT FINAL_LOCATION      POINTS_AWARDED
                  vvvv   v                   v
   [fixation] -> [decision] -> [stimulus] -> [point result] ->
   ^             ^              ^
FIXATION_ONSET   DECISION_ONSET OUTCOME_SIDE
                            NEGATIVE_OUTCOME_SHOWN
                            POSITIVE_OUTCOME_SHOWN                            

*****************************************************************INPUT DETAILS********************************************************************

EACH LINE CODES: one trial
COLUMN 1: valence of the two images using two space separated integers (0->positive, 1->negative, so e.g. '0 1' means positive on left and negative on right)
COLUMN 2: space separated images for the left and right outcomes in that order
COLUMN 3: duration of iti/fixation, left reward, right reward, starting location of avatar
COLUMN 4: two space separated sounds used for the left and right outcomes

TRIAL ORDER IS: fixed


*****************************************************************OUTPUT DETAILS*******************************************************************

trial_type codes:
LvRvLrRrS
left valence
right valence
left reward
right reward
start location

INSTRUCT_ONSET (1)
response_time: not used
response: not used
result: not used

TASK_ONSET (2)
response_time: time between INSTRUCT_ONSET and TASK_ONSET
response: not used
result: not used

FIXATION_ONSET (3)
response_time: not used
response: not used
result: not used

DECISION_ONSET (4)
response_time: not used
response: not used
result: not used

SELECTOR_MOVEMENT (5)
response_time: time from DECISION_ONSET
response: -1 for left, 1 for right
result: selector location

FINAL_LOCATION (6)
response_time: time since DECISION_ONSET, or NA if subject did not lock in
response: NA for timeout, 1 for locked in
result: final location

OUTCOME_SIDE (7)
response_time: not used
response: not used
result: -1 for left, 1 for right

NEGATIVE_OUTCOME_SHOWN (8)
response_time: not used
response: not used
result: image shown and sound played

POSITIVE_OUTCOME_SHOWN (9)
response_time: not used
response: not used
result: image shown and sound played

POINTS_AWARDED (10)
response_time: not used
response: not used
result: points gained and total points


TOTAL_POINTS (11)
response_time: not used
response: not used
result: total points earned in the task


VAS_RATING (12)
Three visual analogue scale ratings are collected using the mouse before the practice run and after the task run.
Subjects are asked to rate how pleasant, unpleasant, and intense they feel.
Trial numbers code which question is being asked (-1 for pleasant, -2 for unpleasant, -3 for intense).
response can range from 0 to 100, with 0 being not at all and 100 being very much.
response_time: time taken to make VAS ratings
response: numerical rating from 0 to 100
result: not used

POST_RATING (13)
After the task run, subjects are asked to rate a series of questions.
These ratings are from 1 to 7, and the questions can be found in T1000_AAC_PostQuestions.csv.
The trial number recorded corresponds to the -1 times the question number in the file.
response_time: time taken to make rating
response: numerical rating from 1 to 7
result: not used






