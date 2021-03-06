import subprocess
import random
import sys
from os import listdir, mkdir
from os.path import isdir, isfile, join, splitext, expanduser, exists, realpath

config = expanduser('~/.config/Background-Changer/')
cFile = join(config, 'background.cfg')
getcmd = "xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor[screenNo]/workspace0/last-image"
setcmd = "xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor[screenNo]/workspace0/last-image -s [path]"
image = "last-image"
path = "."
monitorCount = 1
files = [f for f in listdir(path) if isfile(
    join(path, f)) and splitext(f)[1] == ".jpg"]

def load():
    files = [f for f in listdir(path) if isfile(
        join(path, f)) and splitext(f)[1] == ".jpg"]

def install():
    if not exists(config):
        mkdir(config)
    file = open(cFile, 'w+')
    path = expanduser(raw_input('Wallpaper directory: '))
    file.write('dir:' + path + '\n')
    monitorCount = int(expanduser(raw_input('Number of displays: ')))
    file.write('monitorCount:' + str(monitorCount) + '\n')
    file.write('set-command:' + setcmd + '\n')
    file.write('get-command:' + getcmd + '\n')
    file.close()
    print('Please edit file at ' + config + ' to finish setup')


# loads in settings from file
def loadFromFile(fileName):
    global monitorCount
    global files
    global path
    global setcmd
    global getcmd
    if isfile(fileName):
        file = open(fileName, 'r')
        settings = file.read().split('\n')
        for setting in settings:
            parts = setting.split(":")
            for i in range(0, len(parts)):
                parts[i] = parts[i].replace("*;", ":")
            if parts[0] == "monitorCount":
                monitorCount = int(parts[1])
            elif parts[0] == "dir":
                path = parts[1]
                files = [f for f in listdir(path) if isfile(join(path, f)) and (
                    splitext(f)[1] == ".jpg" or splitext(f)[1] == ".png")]
            elif parts[0] == "set-command":
                setcmd = parts[1]
            elif parts[0] == "get-command":
                getcmd = parts[1]
    else:
        print("No config file!")
        install()
        main()
    return

# runs the command to change the wallpaper according the the given criteria
def changeWallpaper(screen, type, file):
    print("Setting " + screen + " to " + file)
    bashCommand = setcmd.replace("[screenNo]", screen).replace(
        "[path]", path + "/" + file)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return

# converts an entered string to a list of monitor numbers
def getMonitorList(screens):
    if screens == "all":
        monitors = [None] * monitorCount
        for i in range(0, monitorCount):
            monitors[i] = str(i)
        return monitors
    elif '-' in screens:
        ends = screens.split('-')
        return [str(i) for i in range(int(ends[0]), int(ends[1])+1)]
    else:
        return screens.split(",")

# offset list if it isn't 0 indexed
def checkMonitorList(screens):
    start = int(screens[0])
    end = int(screens[-1])
    delta = end - monitorCount + 1
    if delta > 0 and start - delta >= 0:
        return [str(int(i) - delta) for i in screens]
    elif delta > 0 or start < 0:
        return []
    return screens

# processes given file to pass on to monitor
def setMonitor(monitor, file):
    if file.startswith("f:"):
        file = randomWPrint(getFilteredFiles(file.split(":")[1].split(",")))
    elif file == "random":
        file = randomWPrint(files)
    changeWallpaper(monitor, image, file)
    return

# randomly chooses a file from a list then prints its name
def randomWPrint(files):
    file = random.choice(files)
    return file

# finds all files that are valid under the given filters
def getFilteredFiles(filters):
    options = []
    for filter in filters:
        options += [f for f in files if filter in f]
    return options

# saves the current wallpaper set to file
def saveConfig(configName):
    file = open(path + "/" + configName + ".cfg", 'w')
    for i in range(0, monitorCount):
        if i != 0:
            file.write(",")
        bashCommand = getcmd.replace("[screenNo]", str(i))
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        output = output.rsplit('/', 1)[1]
        output = output.replace("\'", "").replace("\n", "")
        file.write(output)
    file.close()
    return

# loads a previously saved wallpaper set from file
def loadConfig(configName):
    location = path + "/" + configName + ".cfg"
    if isfile(location):
        file = open(location, 'r')
        backgrounds = file.read().split(",")
        for i in range(0, len(backgrounds)):
            changeWallpaper(str(i), image, backgrounds[i])
        file.close()
    else:
        print("The provided config does not exist!")
    return

# prints out a help dialog briefly explaining all commands
def help(args):
    print("Usage:")
    print("Commands:")
    for cmd in commands:
        print(cmd.help)
        print('\t' + cmd.helpStr)
    print("Options:")
    print("[monitors]\tall or comma separated list")
    print("[images]\tfile name in given directory, random, or a filter defined by f:[filter]")
    print("(filters)\toptional list of filters to sort with")
    print("[config name]\ta name for the config file")
    return

def setBackground(args):
    i = 3
    monitors = checkMonitorList(getMonitorList(sys.argv[2]))
    if len(monitors) <= 0:
        print('Invalid list of monitors!')
    for monitor in monitors:
        if len(args) - 3 >= len(monitors):
            setMonitor(monitor, sys.argv[i])
            i = i + 1
        else:
            setMonitor(monitor, sys.argv[3])

def listAvailable(args):
    if len(args) > 2:
        filters = [sys.argv[i] for i in range(2, len(args))]
        print("Files under " + ''.join(filters) + " in " + path)
        for f in getFilteredFiles(filters):
            print(f)
    else:
        print("Files in " + path)
        for f in files:
            print(f)

def listConfigs(args):
    filters = [sys.argv[i] for i in range(2, len(args))]
    print("Configs under " + ''.join(filters) + " in " + path)
    for f in [f for f in listdir(path) if isfile(
        join(path, f)) and splitext(f)[1] == ".cfg"]:
        print(f)
        with open(join(path, f), 'r') as file:
            for image in file.read().split(','):
                print('\t' + image)

def doSaveConfig(args):
    if len(args) > 2:
        saveConfig(sys.argv[2])
    else:
        print("A config name must be provided!")

def doLoadConfig(args):
    if len(args) > 2:
        loadConfig(sys.argv[2])
    else:
        print("A config name must be provided!")

def configSum(args):
    print("Monitors: " + str(monitorCount))
    print("Background location: " + path)

def unknown():
    print("Unknown Command")
    help([])

class Cmd:
    def __init__(self, name, helpEx, helpStr, function):
        self.name = name
        self.help = helpEx
        self.helpStr = helpStr
        self.function = function

commands = [
    Cmd('set', "set [monitors] [images]", 'Set the background images of a given set of monitors. A list (1-3), set (1,3), or all (all) monitors can be provided.', setBackground),
    Cmd('list', "list (filters)", 'List all known wallpapers, results can be filtered by a string.', listAvailable),
    Cmd('search', "search (filters)", 'List all known wallpapers, results can be filtered by a string.', listAvailable),
    Cmd('list-configs', "list-configs", 'List all previously saved wallpaper configurations.', listConfigs),
    Cmd('save', "save [config name]", 'Save the current set of wallpapers as a configuration.', doSaveConfig),
    Cmd('load', "load [config name]", 'Load a previously saved wallpaper configuration.', doLoadConfig),
    Cmd('config', "config", 'Give a summary of the current configuration.', configSum),
    Cmd('rebuild', "rebuild", 'Rebuild the configuration settings.', install),
    Cmd('help', "help", 'Display this help message', help),
]

# start actual script
def main():
    loadFromFile(cFile)

    length = len(sys.argv)

    # checks if there are any command arguments
    if length == 1:
        help([])
        sys.exit(0)

    # responds to the given command
    command = sys.argv[1]
    for cmd in commands:
        if cmd.name == command:
            cmd.function(sys.argv)
            return
    
    unknown()

if not exists(config):
    install()

main()