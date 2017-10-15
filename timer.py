#!/usr/bin/python

# Used to create timers for different tasks

import sys
import os
import time
import re
from datetime import datetime
from datetime import timedelta
from enum import Enum

#CSV format: id|task|created|status|statustime||elapsed|tags|project

class Status(Enum):
  '''Available status types for a task'''
  new = 'New' # When a task is created, but has not started (no elapsed time)
  active = 'Active'  # A task that is currently active (time is ticking)
  stopped = 'Paused' # A task that was previously started, but now paused
  completed = 'Completed' # A task that has been completed

class Task:
  '''Create a item of type Task.  Task contains:
     id of the task (unique)
     description of the task
     created date task was created
     status of the task
     statustime (time of status change. In other words, time task was started or completed)
     elapsed time (time elapsed while task was active - in effect, the time spent on the task thus far) Only update when status changes from active
     tags (adds meta data to a task)
     project (add tasks to a specific project)
     '''

  def __init__(self):
    self.id = -1
    self.descr = ''
    self.created = time.time()
    self.status = Status.new
    self.statusTime = ''
    self.elapsed = 0
    self.tags = ''
    self.project = ''
 
  def validate(self):
    '''Validate values in task'''
    if "|" in self.descr :
      sys.exit("Error: Task description contained illegal character: |\nProgram terminated")
    if self.descr == '' :
      sys.exit('Error: Task description is blank. Program terminated')
    if self.id == -1 :
      sys.exit("Error: Task id undetermined, program terminated")
    if not (self.status == Status.new or self.status == Status.stopped or self.status == Status.active or self.status == Status.completed) :
      sys.exit("Error: Task contains invalid status. Program terminated")

  def getElapsedTime(self) :
    '''Get (calculate) the time elapsed since the task has been started (time is stopped while a task is paused)'''

    if self.status == Status.Active :
      elapsedTime = datetime.fromtimestamp(time.time()) - datetime.fromtimestamp(float(self.statusTime))
      elapsedTime += parseTimeDelta(self.elapsed)
    else :
      elapsedTime = self.elapsed
    return elapsedTime

  def start(self) :
     self.status = Status.active 
     self.statusTime = time.time()

  def stop(self) :  
    if self.status == Status.active :
      self.elapsed = self.getElapsedTime()
      self.status = Status.stopped 
      self.statusTime = time.time()
   
    self.printStatus()
 
  def complete() :
    if self.status != Status.completed :
      if self.status == Status.active :
        self.stopTask()
      self.status = Status.completed
      self.statusTime = time.time()

    self.printStatus()

  def modify(modifiedTask) :
    if self.status != Status.completed :
      self.descr = modifiedTask.descr
      self.tags = modifiedTask.tags
      self.project = modifiedTask.project

      self.printStatus()
    else :
      sys.exit("Task is already completed, can't modify completed tasks")


  def printStatus(self) : 
    '''Print the status of the task (includes all of the task details)'''
    print(' ')  
    print('Task id:  ', self.id)
    print('Description:  ', self.descr)
    print('Task Created:  ', self.created)
    print('Status:  ', self.status)
    if self.status == Status.completed :
      print('Task Completed:  ', self.statusTime)
    print('Elapsed time:  ', self.getElapsedTime())
    print('Tags:  ', self.tags)
    print('Project:  ', self.project)
    print(' ')

  def parseTimeDelta(s):
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

class TaskList:
  '''Class for creating a list of tasks'''

  def __init__(self):
    self.tasks = []

  def addTask(self, task):
    task.validate() #before adding task to list, validate values
    self.tasks.append(task)

  def findTaskID(self, taskId):
    for task in self.tasks :
      if task.id == taskId :
        return task
  
  def findTaskDescr(self, taskDescr):
    for task in self.tasks :
      if task.descr == taskDescr :
        return task

  def getCompleted(self):
    '''return completed tasks'''
    completedList = TaskList()
    for task in self.tasks :
      if task.status == Status.completed :
        completedList.addTask(task)
    return completedList

  def getActive(self):
    '''return active tasks'''
    activeList = TaskList()
    for task in self.tasks :
      if task.status == Status.completed :
       activeList.addTask(task)
    return activeList

  def writeTaskCSV(taskList, pathToCSV):
    '''Write task list items to csv file.  This file is called upon each time the script is launched.'''

    pathToCSV.write('id|descr|created|status|statusTime|elapsed|tags|project')
    with open(pathToCSV, 'w') as saveCSV:
      for taskItem in taskList :  
        taskItem.validate() #validate task before writing to file
        saveCSV.write(taskItem.id, '|', taskItem.descr, '|', taskItem.created, '|', taskItem.status, '|', str(taskItem.statustime), '|', str(taskItem.elapsed), '|', taskItem.tags, '|', taskItem.project, '\n')

def isInteger(x) :
  try:
    int(x)
    return True
  except ValueError :
    return False

def showDescription() :
  '''Show the description and tips for using this script'''

  print(' ')
  print('Usage:  ', os.path.basename(sys.argv[0]),' add taskName [+tag|*project]')
  print('Usage:  ', os.path.basename(sys.argv[0]),' modify taskId [taskName|+tag|*project]')
  print('Usage:  ', os.path.basename(sys.argv[0]),' [start|stop|done|status] [taskName|taskId] ')
  print('Usage:  ', os.path.basename(sys.argv[0]),' list [all|new|active|stopped|completed]')
  print('Usage:  ', os.path.basename(sys.argv[0]),' time')
  print(' ')
  print('Description:')
  print('  start              Start time on named task')
  print('  stop               Stop time on named task - this will then remove the task from the list')
  print('  pause              Pause time on named task - task will remain in list of tasks')
  print('  status             Show status of named task')
  print('  time               Show current time')
  print('  list               Show the list of tasks in the specified status. If status type is excluded, all tasks not completed will be shown')
  print(' ')
  sys.exit(0)

def errors() :
  '''Set of errors that can occur and their standardized output'''

  def noTasks() :
    sys.exit('Task list is empty. Please add tasks to the list before trying to start a task.')

def main():
  '''The main event. First step is to load tasks from csv into a TaskList. Tasks can be called with name or id (unique). Task status can be of Status. Unlike v1 of timer, this version will keep tasks indefinitely in the csv (for recalling completed tasks).'''

  taskList = TaskList()

  csvPath = os.path.join(os.path.expanduser("~"),'tasks2.csv')


  if os.path.exists(csvPath) :
    with open(csvPath, 'rb') as taskCSV:
      taskContent = taskCSV.read().splitlines()
    
    for taskRow in taskContent :
      taskRaw = str.split(taskRow.decode('utf-8'),'|') 
      taskItem = Task()
      try:
        taskItem.id = int(taskRaw[0])
      except ValueError :
        sys.exit('Error: Unable to load id for task. \nData: ', taskRaw, '\nProgram terminated')

      taskItem.descr = taskRaw[1]
      taskItem.created = taskRaw[2]
      taskItem.status = taskRaw[3]
      taskItem.statusTime = taskRaw[4]
      taskItem.elapsed = taskRaw[5]
      taskItem.tags = taskRaw[6]
      taskItem.project = taskRaw[7]

      taskList.addTask(taskItem)


  # Declare empty variables for arguments
  taskDo = ''       #  The action to perform (start, stop, etc)
  task = Task()     #  To store task related arguments

  for arg in sys.argv :
    if (arg.lower() == 'time' arg.lower() == 'add') or (arg.lower() == 'start') or (arg.lower() == 'stop') or (arg.lower() == 'done') or (arg.lower() == 'modify') or (arg.lower() == 'status') or (arg.lower() == 'list') :
      taskDo = arg.lower()
    elif arg.lower()[:1] == '+' :
      if len(task.tags) > 0 :
        task.tags = task.tags , ', '
      task.tags = task.tags , arg
    elif arg.lower()[:1] == '*' :
      task.proj = arg
    else :
      if isInteger(arg) :  # if arg is int, then set task id (for recalling specific task by id rather than descr)
        task.id = int(arg)
      else :  # otherwise, assume non-int is task descr
        task.descr = arg

  #  Verify that taskDo is a valid action, if not, show program description/hints and exit
  if taskDo not in ('add', 'time', 'list', 'start', 'stop', 'done', 'modify') :
    print(' ')
    print('Invalid command: ', taskDo)
    print(' ')
    showDescription()
    sys.exit()

  
  if taskDo == 'add' :
    if task.descr == '':
      sys.exit('Invalid task description.\nTo add task, use: ', os.path.basename(sys.argv[0]), ' add "task descriptoin"')
    if not taskList.tasks :
      task.id = 0
    else :
      task.id = taskList.tasks[len(taskList.tasks)-1].id + 1
    taskList.addTask(task)

  elif taskDo == 'time' :
    print(' ')
    print('Current system time is: ')
    print(' ')
    print('  ' , datetime.fromtimestamp(time.time()))
    print(' ')


  # If tasklist is empty, stop the program HERE
  # ANYTHING past this POINT should depend on 1+ item(s) in the list (otherwise add above)
  elif len(taskList) == 0:
    sys.exit('Task list is empty. Please add tasks to the list before trying to start a task.')
 
  elif taskDo == 'list' :
    elif task.descr == 'new' :
      ## TODO - list completed tasks
    elif task.descr == 'active' :
      ## TODO - list active tasks
    elif task.descr == 'stopped' :
      ## TODO - list stopped tasks
    elif task.descr == 'completed' :
      ## TODO - list completed tasks
    else :
      ## TODO - list all tasks

  # Get the index of the task within taskList (makes calling the task easier later) 
  else:
    taskIndex = -1
    if task.descr != '':
      taskIndex = taskList.index(taskList.findTaskDescr(task.descr))
    elif task.id > -1 :
      taskIndex = taskList.index(taskList.findTaskId(task.id))
    else :
      sys.exit('Unable to search for task. Try again. Use: ', os.path.basename(sys.argv[0]), ' add [id|descr]')

    # if taskIndex is it's default value, exit the program with error
    if taskIndex == -1 :
      sys.exit('Unable to find the task. Try again. To view tasks, use: ', os.path.basename(sys.argv[0]), ' list')

  # START task specific items, such as starting, stopping, or getting status
  if taskDo == 'start':
    taskList.index(taskIndex).start()

  elif taskDo == 'stop':
    taskList.index(taskIndex).stop()

  elif taskDo == 'done' :
    taskList.index(taskIndex).complete()

  elif taskDo == 'modify' :
    taskList.index(taskIndex).modify(task)

  elif taskDo == 'status' :
    taskList.index(taskIndex).printStatus()


if __name__ == '__main__':
  main()
