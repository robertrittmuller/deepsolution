import sys
import time
import pathlib
import os
import os.path
import shutil
import time

# function to extract a variable from checkpoint file
def extract_variable(textToSearch, variableName):
    for eachLine in textToSearch:
        if(variableName in eachLine):
            extractedLineData = eachLine.split("=")
            extractedLineData = extractedLineData[1].replace(";","")
            extractedLineData = extractedLineData.replace(" ","")
        
    return str(extractedLineData).rstrip()

# function to extract a variable from checkpoint file
def extract_parameter(textToSearch, variableName):
    for eachLine in textToSearch:
        if(variableName in eachLine):
            extractedLineData = eachLine.split(":")
            extractedLineData = extractedLineData[1].replace(",","")
            extractedLineData = extractedLineData.replace(" ","")
        
    return str(extractedLineData).rstrip()

# get the target path where the data is stored and where we need to save the output
args = sys.argv[1:]
dataPath = pathlib.Path(args[0])
outputPath = pathlib.Path(args[1])

# define the pattern for the folder strucutre that contains the data
currentPattern = "net*"
checkpointPattern = "net*.js"

# let's create a file to dump our data to
outputfile = open(outputPath, "w")
outputfile.write("RowID, Date/Time, Generation, Version, Epoc, Single Car Score, Multi-Car Score, lanesSide, patchesAhead, patchesBehind, trainIterations, opt.gamma, opt.epsilon_min, opt.experience_size, learning_rate, momentum, batch_size, l2_decay")
outputfile.write('\n')

# need to define a unique key for each line
lineCount = 0

# loop through all the folders to locate each data run's files
for currentDirectory in dataPath.glob(currentPattern):
    filepathComponents = str(currentDirectory).split("\\")
    filenameComponents = str(filepathComponents[-1]).split("_")
    runComponents = str(filenameComponents[0]).split("-")

    # now extract the data we need
    runGeneration = runComponents[1]
    runVersion = runComponents[2]
    runDateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(filenameComponents[1], '%Y%m%d-%H%M%S'))
    
    # now we need to extract the filname data from each of the run checkpoints
    for currentFile in currentDirectory.glob(checkpointPattern):
        filepathComponents = str(currentFile).split("\\")
        filenameComponents = str(filepathComponents[-1]).split("-")
        checkpointComponents = str(filenameComponents[-1]).split("_")
        
        # Extract the data points we need from the filename
        checkpointEpoc = filenameComponents[3]
        checkpointSingleScore = checkpointComponents[0]
        checkpointMultipleScore = str(checkpointComponents[1].replace(".js",""))
        # remove the "mp" that was a bug in early runs
        checkpointMultipleScore = checkpointMultipleScore.replace("mp", "")
        
        # Now let's grab the hyperparameters from each file
        with open(currentFile, 'r') as myfile:
            # checkpointFile=myfile.read()
            checkpointFile = []
            for line in myfile:
                checkpointFile.append(line)
        
        # grab each of the hyperparameters
        checkpoint_LanesSide = extract_variable(checkpointFile, "lanesSide =")
        checkpoint_patchesAhead = extract_variable(checkpointFile, "patchesAhead =")
        checkpoint_patchesBehind = extract_variable(checkpointFile, "patchesBehind =")
        checkpoint_trainIterations = extract_variable(checkpointFile, "trainIterations =")
        checkpoint_optgamma = extract_variable(checkpointFile, "opt.gamma =")
        checkpoint_optepsilon = extract_variable(checkpointFile, "opt.epsilon_min =")
        checkpoint_optexperiance_size = extract_variable(checkpointFile, "opt.experience_size =")
        checkpoint_learning_rate = extract_parameter(checkpointFile, "learning_rate:")
        checkpoint_momentum = extract_parameter(checkpointFile, "momentum:")
        checkpoint_batch_size = extract_parameter(checkpointFile, "batch_size:")
        checkpoint_l2_decay = extract_parameter(checkpointFile, "l2_decay:")

        # output the full data set to a file
        outputfile.write(str(lineCount) + "," + runDateTime + "," + runGeneration + "," + runVersion + "," + checkpointEpoc + "," \
            + checkpointSingleScore + "," + checkpointMultipleScore + "," + checkpoint_LanesSide + "," + checkpoint_patchesAhead \
                + "," + checkpoint_patchesBehind + "," + checkpoint_trainIterations + "," + checkpoint_optgamma \
                    + "," + checkpoint_optepsilon + "," + checkpoint_optexperiance_size + "," + checkpoint_learning_rate \
                        + "," + checkpoint_momentum + "," + checkpoint_batch_size + "," + checkpoint_l2_decay)
        outputfile.write('\n')
        lineCount = lineCount + 1

# close out the file gracefully
outputfile.close()
