#!/usr/bin/python

# Used to create timers for different tasks

import sys
import os
import time
import re
from datetime import datetime
from datetime import timedelta

class Task:
  '''Create a item of type Task.  Task contains:
     name of the task
     status of the task
     timestamp (of time.time()) of last activity
     elapsed time'''

  def __init__(self):
    self.name = ''
    self.status = ''
    self.timestamp = ''
    self.elapsed = ''
  
  def getElapsedTime(self,returnMS=False) :
    '''Get (calculate) the time elapsed since the task has been started (time is stopped while a task is paused). Boolean to return microseconds.'''

    if type(self.elapsed) is str:
        self.elapsed = self.parseTimeDelta(self.elapsed)

    if self.status == 'In Progress' :
      elapsedTime = datetime.fromtimestamp(time.time()) - self.getLastUpdate()
      if self.elapsed > self.parseTimeDelta('00:00:00') :
        elapsedTime += self.parseTimeDelta(self.elapsed)
    else :
      elapsedTime = self.elapsed 
   
    if not returnMS :
      elapsedTime = elapsedTime - timedelta(microseconds=elapsedTime.microseconds)

    return elapsedTime 

  def getLastUpdate(self):
    return datetime.fromtimestamp(float(self.timestamp))

  def parseTimeDelta(self, s):
    """Create timedelta object representing time delta
       expressed in a string
   
    Takes a string in the format produced by calling str() on
    a python timedelta object and returns a timedelta instance
    that would produce that string.
   
    Acceptable formats are: "X days, HH:MM:SS" or "HH:MM:SS".
    
    From:  http://kbyanc.blogspot.com/2007/08/python-reconstructing-timedeltas-from.html
    """
    if s is None:
        return None
    d = re.match(
            r'((?P<days>\d+) days, )?(?P<hours>\d+):'
            r'(?P<minutes>\d+):(?P<seconds>\d+)',
            str(s)).groupdict(0)
    return timedelta(**dict(( (key, int(value))
                              for key, value in d.items() )))


  def printStatus(self) : 
    '''Print the status of the task (includes all of the task details)'''
    print(' ')  
    print('Task Name:  ', self.name)
    print('Status:  ', self.status)
    print('Last Update:  ', self.getLastUpdate().strftime("%Y-%m-%d %H:%M:%S"))
    print('Elapsed Time:  ', self.getElapsedTime(True))
    print(' ')

def addTask(tname, tstatus, ttimestamp, ttotal):
  '''Add a task to the task list'''
  newTask = Task()
  newTask.name = tname
  newTask.status = tstatus
  newTask.timestamp = ttimestamp
  newTask.elapsed = ttotal 
  
  taskList.append(newTask)

def findTask(tname,newStatus,returnAlways=False):
  '''Look through the tasklist to find the named task.  Task names are unique.  If the user tries to start a task using a name already in use, the task will start if it is paused and not create a new task.'''

  x = 0 
  while x < len(taskList) :
    if taskList[x].name == tname :
      if taskList[x].status == newStatus :
        print(' ')
        print('The new status for that task is the same as the current status.  No changes made.')
        taskList[x].printStatus()
        sys.exit(0)
      elif taskList[x].status != "Stopped" :
        return x 
    x+=1

  if returnAlways == True :
    return -1  

  else:
    print(' ')
    print('Task "%s" not found!  No changes were made.' % tname)
    print(' ')
    sys.exit(0)

def pauseTask(tname=''):
  '''Look through the tasklist to find the task that is currently running, then pause it. If tname is null, then look for any running task and pause it.'''

  x = 0 
  pauseTask = -1

  while x < len(taskList) :
    if tname == '' and taskList[x].status == 'In Progress' :
      print(' ')
      print('Paused the following task:  ', taskList[x].name)
      pauseTask = x
      break;
    elif taskList[x].name == tname and taskList[x].status != 'Stopped' :
      pauseTask = x
      break;
    
    x+=1

  if len(taskList) and pauseTask >= 0:
    taskList[pauseTask].elapsed = taskList[pauseTask].getElapsedTime()
    taskList[pauseTask].status = 'Paused' 
    taskList[pauseTask].timestamp = time.time()

    taskList[pauseTask].printStatus()

def removeTask(taskIndex):
  '''Remove a task (based on given task index) from the task list.'''

  print('')
  tcount = len(taskList)
  taskList.pop(taskIndex)
  
  if tcount > len(taskList):
    print('Task Removed')
  else:
    print('An error has occurred removing the task.  No changes were made!')     
 
def archiveTasks(csvPath):
  '''Move (via rename) current csv file with current date appended to it. If archive file with same date already exists, append a revision (digit) to the new file. Example: tasks.csv-19700101-1 '''
  appendTime=datetime.now().strftime("%Y%m%d")
  archiveCSV = os.path.basename(csvPath) + "-" + appendTime
  archivePath = os.path.join(os.path.dirname(csvPath), archiveCSV)

  x = 1
  while os.path.exists(archivePath) :
    archiveCSV = os.path.basename(csvPath) + "-" + appendTime + "-" + str(x)
    archivePath = os.path.join(os.path.dirname(csvPath), archiveCSV)
    x+=1
    
  os.rename(csvPath, archivePath)

  if os.path.exists(archivePath) :
    print(' ')
    print('Tasks successfully archived to: ', archivePath)
  else:
    print(' ')
    print('An error has occurred while archive. Archive path does not exist: ', archivePath)
  
def writeTaskCSV(csvPath):
  '''Write task list items to csv file.  This file is called upon each time the script is launched.'''

  csvPath = os.path.join(os.path.expanduser("~"),'tasks.csv')
  
  with open(csvPath, 'w') as saveCSV:
    for taskitem in taskList :  
      taskItem = taskitem.name
      taskItem += '|'
      taskItem += taskitem.status
      taskItem += '|'
      taskItem += str(taskitem.timestamp)
      taskItem += '|'
      taskItem += str(taskitem.elapsed)
      taskItem += '\n'
      saveCSV.write(taskItem)    

def startOfWeek(date):
  '''Returns the date (in datetime) for the start of the week (Sunday)'''

  # subtract days until we reach Sunday (int=6)
  while date.weekday() != 6 :
    date = date - timedelta(days=1)
  
  return date.replace(hour=00, minute=00, second=00, microsecond=000000)

def startOfMonth(date):
  '''Returns the date (in datetime) for the start of the month.'''

  date = date.replace(hour=00, minute=00, second=00, microsecond=00, day=1)

  return date

def validateTaskAction(arguments) :
  '''Parse the arguments provided and look for a valid action and associated task name if needed. Provide an error message if something is missing.'''

  # store the action and taskName items here
  action = ''
  taskName = ''

  #taskOptions are commands that require a task
  #genOptions are comamnds that don't require a task associated with it
  taskOptions = ('start', 'stop', 'done', 'pause', 'delete', 'rename', 'status')
  genOptions = ('list', 'time', 'archive')

  #parse arguments and look for relevant information
  # First, remove this from arguments since we won't be needing it
  arguments.pop(0)

  # if there are no at this point arguments, then we'll want to show the description
  if len(arguments) < 1:
    action = ''
  # Otherwise, look at first and last item for an action
  # if found, set to action and remove from arguments since we won't be needing it going forward
  elif arguments[0] in taskOptions or arguments[0] in genOptions :
    action = arguments[0].lower()
    arguments.pop(0)
  elif arguments[len(arguments)-1] in taskOptions or arguments[len(arguments)-1] in genOptions:
    action = arguments[len(arguments)-1].lower()
    arguments.pop(len(arguments)-1)

  # now set the remaining item(s) to the taskName - this allows for spaces in a task item
  # look at first and last item for an action
  for arg in arguments:
    if len(taskName) > 0:
      taskName += ' '
    taskName += arg.replace(' ', '')
  
  # if task list is empty, only option should be to add a task or display the time 
  if action == '' :
    showDescription()
    sys.exit(0)

  if action != 'start' and action != 'time' and len(taskList) == 0 :
    print(' ')
    print('Please add tasks before running other task commands.')
    print('Use "timer [taskName] start" or "timer start [taskName]" to start a task')
    print(' ')
    sys.exit(0)

  # check to see if action is in either option group (genOptions and taskOptions)
  # at this point we don't care if a task is included or not, we just want to know if the command is valid
  elif action not in genOptions and action not in taskOptions and len(action) > 0:
    print(' ')
    print('Invalid command:  ', action)
    showDescription()
    sys.exit(0)

  # check to see if action is in taskOptions and check to make sure a task was included
  elif action in taskOptions and len(taskName) <= 0 :
    print(' ')
    print('This command requires a taskname.  Please include a task name and try again.')
    print('Usage:  timer [taskname]', action) 
    print(' ')
    showDescription()
    sys.exit(0)

  # everything checks out - return taskName,action
  else :
    # if action is set to done, change to stop since we are using both interchangeably
    if action == 'done' :
      action = 'stop'

    return taskName,action

def showDescription() :
  '''Show the description and tips for using this script'''
  print(' ')
  print('Timer.py - track tasks that are worked on and the time spent on those tasks.')
  print(' ')
  print('Description:')
  print('Timer.py is meant to keep track of time on various tasks to give insight into how time is being spent and how much time is spent on various tasks. To create a task, simply type "timer [taskName] start". Commands and task names are interchangeable, so "timer start [taskName]" and "timer [taskName] start" are the same thing, they both will start the specified tasks. Task names can be any string, including spaces. The program will look at the first and last argument for the action to perform, the remaining values will be included in the task name. The items are stored in a simple CSV, should you need to manually edit the file or import it elsewhere. A stopped task designates a task that was completed, and since no further action is neeed, it is essentially frozen in time. It cannot be started or removed.  Trying to start a stopped task will result in a new task being created.')
  print(' ')
  print('Usage:  timer [taskName] [start|stop|done|pause|status|delete|rename]')
  print('Usage:  timer [list]')
  print('Usage:  timer time|archive')
  print(' ')
  print('Options:')
  print('  start              Start time on named task')
  print('  stop,done          Stop time on named task (mark it as done) - this will disable further updates for the given task (essentially freezes the task indefinitely)')
  print('  pause              Pause time on named task')
  print('  status             Show status of named task')
  print('  delete             Delete the named task from the list')
  print('  rename             Rename a task (preserves timestamps)')
  print('  archive            Archive the tasks stored in the csv (rename the csv with date appended to the filename')
  print('  time               Show current time')
  print(' ')
  print('Examples:')
  print('  timer new task start')
  print('  timer start taskitem')
  print('  timer archive')
  print('  timer list')
  print(' ')
  sys.exit(0)

def main():
  '''This script is used to create timers for different tasks.  While a task is in the "In Progress" status, the elapsed time is accrued.  Elapsed time is paused while a task is paused.  Once a task is stopped, the task is removed from the list of tasks and shows the total time spent on the named task.'''

  global taskList
  taskList = []
  taskName = '' 
  csvPath = os.path.join(os.path.expanduser("~"),'tasks.csv')

  # load the csv
  if os.path.exists(csvPath) :
    with open(csvPath, 'rb') as taskCSV:
      taskContent = taskCSV.read().splitlines()
    
    for taskRow in taskContent :
      taskItem = str.split(taskRow.decode('utf-8'),'|') 
      addTask(taskItem[0],taskItem[1],taskItem[2],taskItem[3]) 

  # check to make sure taskDo is valid and requirements are met (task included when needed)
  # program will end here if invalid command
  taskName,taskDo = validateTaskAction(sys.argv)

  # now that we know action is valid, start processing commands
  if taskDo == 'list':
    elapsedTotal = timedelta(0, 0, 0)

    #format the output - grows/shrinks depending on taskname lengths - keeps everything aligned
    maxLen = max(len(task.name) for task in taskList)
    width = maxLen+10
    output = "{1:<{0}} {2:<15} {3:12} {4:26}".format(width,'Task Name', 'Status', 'Time', 'Last Update')
    print(' ')
    print(output)

    # create horizontal line and get the length of output from above to set for line
    hl = '-'
    while len(hl) < len(output):
      hl += '-'
    print(hl)
    print('')
    x = 0

    #output the tasks (use same format style from above
    while x < len(taskList) :
      output = " {1:<{0}} {2:<15} {3:12} {4:26}".format(width,taskList[x].name, taskList[x].status, str(taskList[x].getElapsedTime()), taskList[x].getLastUpdate().strftime("%Y-%m-%d %H:%M:%S"))
      print(output)
      elapsedTotal = elapsedTotal + taskList[x].getElapsedTime()
      x = x+1
    
    print(' ')
    # create totals horizontal line (replace chars for same line as above)
    print(hl.replace('-', '='))

    #output the totals using the same format style
    output = "{1:<{0}}  {2:<15} {3:12}".format(width, 'Total','', str(elapsedTotal))
    print(output)
 
  #elif taskDo == 'time' :
    #print(' ')
    #print('Current system time is: ')
    #print(' ')
    #print('  ' , datetime.fromtimestamp(time.time()))
    #print(' ')

  elif taskDo == 'archive' :
    archiveTasks(csvPath)
   
  elif taskDo == 'start' :
    x = findTask(taskName,'In Progress',True)

    pauseTask()

    if x >= 0 :   
     taskList[x].status = 'In Progress' 
     taskList[x].timestamp = time.time()

    else:
      addTask(taskName, 'In Progress', time.time(), datetime.fromtimestamp(time.time()) - datetime.fromtimestamp(time.time()))
      print(' ')
      print('New task created.')
      x = len(taskList) -1
   
    writeTaskCSV(csvPath) 
    print(' ')
    print('Task started.')
    taskList[x].printStatus() 

  elif taskDo == 'status' :
    x = findTask(taskName,'',False)
    if x >= 0 :
      taskList[x].printStatus()

  elif taskDo == 'stop' :
    x = findTask(taskName,'')
   
    if taskList[x].status == "In Progress" :
      taskList[x].elapsed = taskList[x].getElapsedTime()
      taskList[x].timestamp = time.time()
    
    taskList[x].status = "Stopped"
    taskList[x].printStatus() 
    
    writeTaskCSV(csvPath)

  elif taskDo == 'delete':
    x = findTask(taskName, '')

    print(' ')
    print('Removing task...')

    print(' ')
    taskList[x].printStatus()

    removeTask(x)
    writeTaskCSV(csvPath)
 
  elif taskDo == 'rename' :
    x = findTask(taskName,'Rename')

    print(' ')

    # prompt for new name for task
    newName = input('Enter the new name for the task "' + taskList[x].name +'":  ')

    #make sure newName is not already used by a task
    y = findTask(newName,'',True)
    
    if y > 0:
      print(' ')
      print(' ')
      print('A task by the name "' + newName + '" already exists.')
      print(' ')
      print('No changes were made.')
      sys.exit(0)
    else:
      # task not found, make the change
      taskList[x].name = newName
      
      print(' ')
      print('Task renamed successfully.')
      taskList[x].printStatus()

      writeTaskCSV(csvPath)

  elif taskDo == 'pause' :
    x = findTask(taskName,'Paused')
   
    pauseTask(taskList[x].name)

    writeTaskCSV(csvPath)

  print(' ')
  print(' ')
  print('System Time:  ' , datetime.strftime(datetime.fromtimestamp(time.time()), "%Y-%m-%d %H:%M:%S"))
  print(' ')

if __name__ == '__main__':
  main()
