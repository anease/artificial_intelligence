## Andrew Nease
## UC Fall 2020
## AI Homework 1 - Task 1

from datetime import datetime, timedelta 
from time import sleep

openList = []
closedList = []

startState = []
goalState = []
currentState = []

nextStateId = 0

openListCount = 0
closedListCount = 0

class Tile:
    def __init__(self, value, x, y):
        self.value = value
        
        #####################
        # BOARD COORDINATES # 
        #####################
        # (1,6) (2,6) (3,6) #
        # (1,5) (2,5) (3,5) #
        # (1,4) (2,4) (3,4) #
        # (1,3) (2,3) (3,3) #
        # (1,2) (2,2) (3,2) #
        # (1,1) (2,1) (3,1) #
        #####################
        
        ## X and Y coordinates on board
        self.x = x
        self.y = y

class State:
    def __init__(self, id, parentId, puzzleBoard, costToNode, costToGoal, solutionCost, priority, numberOfMoves):
        self.id = id
        self.parentId = parentId
        ## Array of tiles
        self.puzzleBoard = puzzleBoard
        ## This is the g(n) value
        self.costToNode = costToNode
        ## This is the h(n) value
        self.costToGoal = costToGoal
        ## This is the f(n) value
        self.solutionCost = solutionCost

        ## For BFS this is the level number
        self.priority = priority

        ## Number of moves to get to this state
        self.numberOfMoves = numberOfMoves


## Find all successor states and generate states to be placed into open list
## Current state is taken as input
def findSucessorStates(parentState):
    movableTileIndexes = []

    board = parentState.puzzleBoard

    for i, tile in enumerate(board):

        ## Collect indexes of tiles that can be moved based on the empty tile's position
        if tile.value == 0:
            emptyIndex = i
            
            if tile.x == 1:
                movableTileIndexes.append(i+1)
            elif tile.x == 2:
                movableTileIndexes.append(i+1)
                movableTileIndexes.append(i-1)
            elif tile.x == 3:
                movableTileIndexes.append(i-1)

            if tile.y == 1:
                movableTileIndexes.append(i-3)
            elif tile.y == 6:
                movableTileIndexes.append(i+3)
            else:
                movableTileIndexes.append(i-3)
                movableTileIndexes.append(i+3)


    ## Create the sucessor board states and compare them to the closed list
    ## If board does not exist on the closed list then generate a new state and place on the open list
    ## Check if a sucessor board matches goal state
    for tileIndex in movableTileIndexes:
        sucessorBoard = board[:]

        moveTile = board[tileIndex]
        emptyTile = board[emptyIndex]

        sucessorBoard[emptyIndex] = Tile(moveTile.value, emptyTile.x, emptyTile.y)
        sucessorBoard[tileIndex] = Tile(0, moveTile.x, moveTile.y)

        ## Check if board is in the goal state
        goalFlag = 0

        for i, _ in enumerate(goalState):
            if goalState[i].value != sucessorBoard[i].value:
                goalFlag = 1

        ## If this board does match the goal, generate the final state and return back to the solvePuzzle loop
        if goalFlag == 0:
            global nextStateId
            moveCost = getTileCost(moveTile.value)
            totalCost = parentState.costToNode + moveCost

            finalMoves = parentState.numberOfMoves + 1

            finalState = State(nextStateId, parentState.id, sucessorBoard, totalCost, 0, totalCost, 0, finalMoves)

            return (0, finalState)


        ## Check the closed list for this sucessor board
        ## Only create a new state if this board is not already on the closed list
        flag = 0
        for i, _ in enumerate(closedList):
            for q, tile in enumerate(closedList[i][1].puzzleBoard):
                if tile.value != sucessorBoard[q].value:
                    flag = 1

        if flag == 1 or not closedList:

            moveCost = getTileCost(moveTile.value)
            totalCost = parentState.costToNode + moveCost

            moves = parentState.numberOfMoves + 1
    
            generateState(parentState.id, sucessorBoard, totalCost, getH1Value(sucessorBoard), moves)

    return (1, None)


## Create new state and add it to the open list
## We only track costToNode in BFS (no heuristics)
## For BFS priority will be the parent's plus one (search tree depth)
def generateState(parentId, board, costToNode, costToGoal, moves):
    global nextStateId
    global openListCount

    newState = State(nextStateId, parentId, board, costToNode, costToGoal, costToGoal+costToNode, costToGoal+costToNode, moves)

    ## Iterate global variable for the next state
    nextStateId += 1

    openList.append((newState.priority, newState))
    openListCount += 1

    ## Sort the open list (list of tuples) by the priority value
    sorted(openList, key=lambda tup: (tup[0]))



## Get the H1 heuristic value by counting the number of tiles not in their goal position
def getH1Value(board):
    tilesNotInPosition = 0

    for i, _ in enumerate(goalState):
            if goalState[i].value != board[i].value:
                tilesNotInPosition += 1
    
    return tilesNotInPosition


## This is the main loop that will coordinate the expansion of the openList and trigger the final output when puzzle is solved
def solvePuzzle():
    global closedListCount

    ## Get start time for search timeout
    initTime = datetime.now()

    while openList:
        ## Search is configured to time out after one minute
        timeElapsed = datetime.now() - initTime
        if timeElapsed > timedelta(minutes=1):
            print("Search has Timed Out")
            break
        
        ## Remove first state off the open list
        stateTuple = openList.pop(0)

        ## Find the sucessor states of this node from the openList
        retVal = findSucessorStates(stateTuple[1])

        ## Place the state into closed list after sucessors are found
        closedList.append(stateTuple)
        closedListCount += 1

        ## This condition is triggered when goal state is found
        if retVal[0] == 0:
            printGoalPath(retVal[1])
            break


## Open input file and create the expected search objects
def initInputFile():
    ## Open input file and process start and goal states
    file = open('input.txt', 'r')
    allLines = file.readlines()
    file.close()

    ## Clean up and convert inputs to Tile lists with coordinates
    ## Start State
    global startState
    startState = allLines[0].strip().replace('[','').replace(']','').split()

    y = 6
    x = 1
    for i, value in enumerate(startState):
        if (i % 3 == 0) & (i != 0):
            x = 1
            y = y - 1

        startState[i] = Tile(int(value), x, y)
        x = x + 1


    ## Goal State
    global goalState
    goalState = allLines[1].strip().replace('[','').replace(']','').split()

    y = 6
    x = 1
    for i, value in enumerate(goalState):
        if (i % 3 == 0) & (i != 0):
            x = 1
            y = y - 1

        goalState[i] = Tile(int(value), x, y)
        x = x + 1

    ## Need to generate start state after goal state is init so we can get H1 value
    generateState(0, startState, 0, getH1Value(startState), 0)


## Cost for a tile numbered 1 to 6 is 1 unit
## Cost for a tile numbered 7 to 16 is 3 units
## Cost for a tile numbered 17 is 15 unit
def getTileCost(value):
    if value >= 1 and value <= 6:
        return 1
    elif value >= 7 and value <= 16:
        return 3
    elif value == 17:
        return 15


## Trace the path from start to goal and print info
## Input parameter is the state that was found that matches the goal
def printGoalPath(state):

    path = []
    path.append(state)

    ## Search for parent states in the closed list and append to path list
    while state.id != 0:

        for s in closedList:          
            if s[1].id == state.parentId:
                path.append(s[1])
                state = s[1]

    ## Reverse so print out is from start to finish
    path.reverse()

    for x in path:
        printBoard(x)
        print("\n")

    print("Number of Moves:", path[len(path)-1].numberOfMoves)
    print("Nodes added to Open List:", openListCount)
    print("Nodes added to Closed List:", closedListCount)
    print("\n")


## Utility function to print board for puzzle visualization
def printBoard(state):
    b = state.puzzleBoard[:]

    print("State ID:", state.id)
    print("Value of g(n):", state.costToNode)
    print("Value of h(n):", state.costToGoal)
    print("Value of f(n):", state.solutionCost)

    for i, x in enumerate(b):
        if x.value == 0:
            b[i].value = '_'

    print("%-4s %-4s %-4s" % (str(b[0].value), str(b[1].value), str(b[2].value)))
    print("%-4s %-4s %-4s" % (str(b[3].value), str(b[4].value), str(b[5].value)))
    print("%-4s %-4s %-4s" % (str(b[6].value), str(b[7].value), str(b[8].value)))
    print("%-4s %-4s %-4s" % (str(b[9].value), str(b[10].value), str(b[11].value)))
    print("%-4s %-4s %-4s" % (str(b[12].value), str(b[13].value), str(b[14].value)))
    print("%-4s %-4s %-4s" % (str(b[15].value), str(b[16].value), str(b[17].value)))

    ## Assign blank space back to zero to address weird referencing bug
    for i, x in enumerate(b):
        if x.value == "_":
            b[i].value = 0


## Execution starts here
initInputFile()
solvePuzzle()
