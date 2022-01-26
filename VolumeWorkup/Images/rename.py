#!/usr/bin/env python

import glob

#images = glob.glob('C:\Approach-Avoidance-Task\ApproachAvoidanceConflict\media\images\*\*gif')

images = glob.glob('c:\Approach-Avoidance-Task\ApproachAvoidanceConflict\media\images\\*\\*.gif')


print images
for image in images:
    print(image)