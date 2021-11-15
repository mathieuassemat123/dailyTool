from rv import commands, rvtypes
from pymu import MuSymbol


def playSingleMedia(path):
    source = commands.addSourceVerbose([path])
    sourceGroup = commands.nodeGroup(source)
    commands.setViewNode(sourceGroup)    

def playAsLayout(paths):
    print(paths)
    newLayout = commands.newNode("RVLayoutGroup", "layout")
    allSourceGroups = []
    for path in paths:
        source = commands.addSourceVerbose([path])
        allSourceGroups.append(commands.nodeGroup(source))
    commands.setNodeInputs(newLayout, allSourceGroups)
    commands.setViewNode(newLayout)

def playAsSequence(paths):
    print(paths)
    newLayout = commands.newNode("RVSequenceGroup", "sequence")
    allSourceGroups = []
    for path in paths:
        source = commands.addSourceVerbose([path])
        allSourceGroups.append(commands.nodeGroup(source))
    commands.setNodeInputs(newLayout, allSourceGroups)
    commands.setViewNode(newLayout)


def playAsCompare(paths):
    print(paths)
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