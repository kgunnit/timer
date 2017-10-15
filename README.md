timer.py
=======

Simple cli app to track time spent on tasks. Program is geared toward single-tasking (starting a new task will automatically pause the last one)

## Commands

  'start'	      start a new task
  'pause'	      pause a running task
  'stop'	      Stop time on named task (mark it as done) - this will disable further updates for the given task (essentially freezes the task indefinitely)
  'done'	      same as 'stop'
  'pause              Pause time on named task
  'status             Show status of named task
  'delete             Delete the named task from the list
  'rename             Rename a task (preserves timestamps)
  'archive            Archive the tasks stored in the csv (rename the csv with date appended to the filename
  'time               Show current time
