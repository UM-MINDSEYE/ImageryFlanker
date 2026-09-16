'''
IMAGERY FLANKER TASK - PsychoPy 2024.2.4 compatible 
'''

import numpy as np
import datetime
import os
from psychopy import visual, event, core, gui, monitors, sound, prefs

################ weird audio fix ################
# PTB backend crashes on some mac psychopy installs
prefs.hardware['audioLib'] = ['sounddevice']
prefs.hardware['audioLatencyMode'] = 0

################ adjustable variables ################
useFullScreen = True
nTrials = 50
sf = 6.7
size = .525 #0.35 # Gabor FWHM # Keri andSagi papers use sigma of .15; to convert to fwhm: .15 * 2.355 = 0.35325
stimDuration = 0.09
ISI = 1.0               # are these settings the same as other papers
feedbackDuration = 0.1  


################ run info ################
runInfo = {
    'Subject': 'test',
    'nRuns': 3,
    'task': ['vis', 'img', 'non'],
    'alignment': ['colinear', 'orthogonal', 'parallel'],
    'distance': ['mid', 'near', 'far'],
    'instructions': False
}

infoDlg = gui.DlgFromDict(
    dictionary=runInfo,
    title='Scan Parameters'
)

if not infoDlg.OK:
    core.quit()

################ monitor stuff ################
subMonitor = monitors.Monitor('testMonitor') # might should look into this to make sure all this is right
subMonitor.setWidth(53.0)
subMonitor.setDistance(57.0)
subMonitor.setSizePix((1800, 1169))
screenSize = [1400, 900]

################ directories ################
if not os.path.exists('subjectResponseFiles'):
    os.makedirs('subjectResponseFiles')

################ keys ################
responseKeys = ['left', 'right']
quitKeys = ['q', 'escape']


################ flanker positioning & orientation ################
# Polat and these groups do flanker measure the distance of flankers from target 
# using lambda, which is the wavelength of the gabors themselves. 

if runInfo['distance'] == 'near':
    lamb_mult = 1
elif runInfo['distance'] == 'mid':
    lamb_mult = 3
else:
    lamb_mult = 6

flanker_dist = (1 / sf) * lamb_mult  # how many lambdas from target are the flankers

if runInfo['alignment'] == 'colinear':
    flanker_pos = (
        (0., flanker_dist),
        (0., -flanker_dist)
    )
    flanker_ori = 0.
    align_name = 'clnr'

elif runInfo['alignment'] == 'orthogonal':
    flanker_pos = (
        (0., flanker_dist),
        (0., -flanker_dist)
    )
    flanker_ori = 90.
    align_name = 'orth'

else:
    flanker_pos = (
        (flanker_dist, 0.),
        (-flanker_dist, 0.)
    )
    flanker_ori = 0.
    align_name = 'para'

################ window ################
win = visual.Window(
    size=screenSize,
    monitor=subMonitor,
    screen=0,
    fullscr=useFullScreen,
    units='deg',
    color=[0, 0, 0],
    allowGUI=True
)

win.mouseVisible = False

################ stimuli ################
target = visual.GratingStim(
    win,
    tex='sin',
    mask='gauss',
    units='deg',
    size=size,
    sf=sf,
    phase=0.,
    ori=0.,
    pos=(0., 0.)
)

flanker_1 = visual.GratingStim(
    win,
    tex='sin',
    mask='gauss',
    units='deg',
    size=size,
    sf=sf,
    phase=0.,
    ori=flanker_ori,
    pos=flanker_pos[0],
    contrast=0.4
)

flanker_2 = visual.GratingStim(
    win,
    tex='sin',
    mask='gauss',
    units='deg',
    size=size,
    sf=sf,
    phase=0.,
    ori=flanker_ori,
    pos=flanker_pos[1],
    contrast=0.4
)

################ fixation ################

fixSquare = visual.Rect(
    win,
    width=0.2,
    height=0.2,
    fillColor='white',
    lineColor='white',
    units='deg'
)

################ crosshairs ################
# i did this to sort of help direct the eyes to be at the center since we can't have
# a fixation cross at center coz that's where the target is (anything at center will 
# cause afterimage) 

dist_crosshair = (1 / sf) * 15
len_crosshair = 2

line_N = visual.Line(
    win,
    start=(0, dist_crosshair),
    end=(0, dist_crosshair + len_crosshair),
    lineColor='black',
    units='deg'
)

line_S = visual.Line(
    win,
    start=(0, -dist_crosshair),
    end=(0, -dist_crosshair - len_crosshair),
    lineColor='black',
    units='deg'
)

line_E = visual.Line(
    win,
    start=(dist_crosshair, 0),
    end=(dist_crosshair + len_crosshair, 0),
    lineColor='black',
    units='deg'
)

line_W = visual.Line(
    win,
    start=(-dist_crosshair, 0),
    end=(-dist_crosshair - len_crosshair, 0),
    lineColor='black',
    units='deg'
)

def drawCrosshairs():
    line_N.draw()
    line_S.draw()
    line_E.draw()
    line_W.draw()

################ audio ################
stimSound = sound.Sound(
    value=800,
    secs=0.1,
    stereo=True
)

rightSound = sound.Sound(
    value=1200,
    secs=0.1,
    stereo=True
)

wrongSound = sound.Sound(
    value=400,
    secs=0.1,
    stereo=True
)

################ 3up 1down staircase ################
log_spacing = np.linspace(-3, -.4, 27) # we want step size of .1 in logspace, to know how many steps to take in linspace to get .1 logspace steps: num = ((stop - start)/step size) + 1
# jlb, could maybe write that equation out later so that it's a parameter that we can adjust
deltaCs = 10 ** log_spacing
#print('log_spacing: ', log_spacing)
#print('deltaCs: ', deltaCs)

################ runs!! ################
for iRun in range(runInfo['nRuns']):

    stairTracker = {
        'contrastLevel': 20,
        'nRight': 0
    }

    subjectResponses = []

    nowTime = datetime.datetime.now()

    timeStamp = '%04d%02d%02d_%02d%02d_%02d' % (
        nowTime.year,
        nowTime.month,
        nowTime.day,
        nowTime.hour,
        nowTime.minute,
        nowTime.second
    )

    outputFile = os.path.join(
        'subjectResponseFiles',
        '%s_%s_%s_%sxL_%s.txt' % (
            runInfo['Subject'],
            runInfo['task'],
            align_name,
            lamb_mult,
            timeStamp
        )
    )

    ################ instructions ################
    # note that currently you also have to press a key again to start-start

    instructionText = '''
Press LEFT if target appeared during FIRST beep.

Press RIGHT if target appeared during SECOND beep.

Press any key to begin.
'''

    instructionMsg = visual.TextStim(
        win,
        text=instructionText,
        units='norm',
        height=0.07,
        wrapWidth=1.5
    )

    instructionMsg.draw()
    win.flip()

    keys = event.waitKeys()

    if keys[0] in quitKeys:
        core.quit()

    ################ INITIAL FIXATION ################

    fixSquare.draw() # jlb: might need to change this so that it doesn't leave afterimage on first trial
    drawCrosshairs()

    win.flip()

    keys = event.waitKeys()

    if keys[0] in quitKeys:
        core.quit()

    ################ TRIAL TIMER ################

    trialTimer = core.Clock()

    ################ TRIAL LOOP ################

    for iTrial in range(nTrials):

        event.clearEvents()

        core.wait(0.5)

        whichInterval = int(np.random.random() > 0.5)

        trialTimer.reset()

        for iInterval in range(2):

            thisContrast = deltaCs[
                stairTracker['contrastLevel']
            ]
#            print('thisContrast:  ', thisContrast)
            while trialTimer.getTime() < (
                ISI * iInterval
            ):
                core.wait(0.001)

            stimSound.play()

            if iInterval == whichInterval:

                target.contrast = thisContrast

                target.draw()

            if runInfo['task'] == 'vis':

                flanker_1.draw()
                flanker_2.draw()

            drawCrosshairs()

            win.flip()

            while trialTimer.getTime() < (
                ISI * iInterval + stimDuration
            ):
                core.wait(0.001)

            drawCrosshairs()

            win.flip()

        ################ RESPONSE ################

        keys = event.waitKeys(
            keyList=quitKeys + responseKeys
        )

        key = keys[0]

        if key in quitKeys:

            win.close()
            core.quit()

        correct = (
            key == responseKeys[whichInterval]
        )

        response = {
            'trial': iTrial,
            'key': key,
            'time': trialTimer.getTime(),
            'deltaC': thisContrast,
            'correct': correct
        }

        subjectResponses.append(response)

        ################ STAIRCASE ################

        if correct:

            stairTracker['nRight'] += 1

            fixColor = 'green' # jlb removed this for now 

            fbSound = rightSound

        else:

            stairTracker['nRight'] = 0

            stairTracker['contrastLevel'] = min(
                len(deltaCs) - 1,
                stairTracker['contrastLevel'] + 1
            )

            fixColor = 'red' # jlb removed this for now 

            fbSound = wrongSound

        ################ FEEDBACK ################

        fixSquare.fillColor = fixColor

        #fixSquare.draw() # jlb taking out fixation for now

        drawCrosshairs()

        win.flip()

        fbSound.play()

        core.wait(feedbackDuration)

        fixSquare.fillColor = 'white'

        ################ STAIRCASE STEP DOWN ################

        if stairTracker['nRight'] == 3:

            stairTracker['nRight'] = 0

            stairTracker['contrastLevel'] = max(
                0,
                stairTracker['contrastLevel'] - 1
            )

    ################ SAVE DATA ################

    with open(outputFile, 'w') as f:

        f.write(
            'Trial\tResponse\tReactionTime\tdC\tcorrect\n'
        )

        for trial in subjectResponses:

            f.write(
                '%d\t%s\t%2.3f\t%2.3f\t%d\n' % (
                    trial['trial'],
                    trial['key'],
                    trial['time'],
                    trial['deltaC'],
                    trial['correct']
                )
            )

    thanks = visual.TextStim(
        win,
        text='Thank you!'
    )

    thanks.draw()

    win.flip()

    core.wait(1)

################ CLEANUP ################

win.close()
core.quit()