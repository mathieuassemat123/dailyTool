from rv import commands, rvtypes
from pymu import MuSymbol

_newSession = MuSymbol("shotgun_mode.sessionFromVersionIDs")


def playSingleMedia(path, id):
    commands.clearSession()
	
    #newLayout = commands.newNode("RVSequenceGroup", "sequence")
    #commands.setViewNode(newLayout)
	
    _newSession([id], clearFirst = False)
    commands.play() 
    
    #alternative method below, doesn't allow for shotgrid tools integration
    '''
    print path
    newLayout = commands.newNode("RVSequenceGroup", "sequence")
    allSourceGroups = []
    source = commands.addSourceVerbose([path])
    allSourceGroups.append(commands.nodeGroup(source))
    commands.setNodeInputs(newLayout, allSourceGroups)
    commands.setViewNode(newLayout)
    commands.play()   
    '''

def playAsLayout(paths):
    newLayout = commands.newNode("RVLayoutGroup", "layout")
    allSourceGroups = []
    for path in paths:
        source = commands.addSourceVerbose([path])
        allSourceGroups.append(commands.nodeGroup(source))
    commands.setNodeInputs(newLayout, allSourceGroups)
    commands.setViewNode(newLayout)

def playAsSequence(paths):
    newLayout = commands.newNode("RVSequenceGroup", "sequence")
    allSourceGroups = []
    for path in paths:
        source = commands.addSourceVerbose([path])
        allSourceGroups.append(commands.nodeGroup(source))
    commands.setNodeInputs(newLayout, allSourceGroups)
    commands.setViewNode(newLayout)


def playAsCompare(paths):
    newLayout = commands.newNode("RVStackGroup", "stack")
    allSourceGroups = []
    for path in paths:
        source = commands.addSourceVerbose([path])
        allSourceGroups.append(commands.nodeGroup(source))
    commands.setNodeInputs(newLayout, allSourceGroups)
    commands.setViewNode(newLayout)
    wipesShown = MuSymbol("rvui.wipeShown")
    if  wipesShown()!= 2 :
        toggleWipes = MuSymbol("rvui.toggleWipe")
        toggleWipes()



def getPlayMenu():
    return(['Play', 'Compare', 'Layout'])
