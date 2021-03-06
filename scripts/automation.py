#!python3
# -*- coding:utf-8 -*-

import sys
import time

from uiautomation import (Win32API, Logger, ControlFromCursor, GetRootControl, GetFocusedControl,
                          VERSION, EnumAndLogControlAncestors, EnumAndLogControl, ConsoleColor)


def usage():
    Logger.ColorfulWrite("""usage
<Color=Cyan>-h</Color>      show command <Color=Cyan>help</Color>
<Color=Cyan>-t</Color>      delay <Color=Cyan>time</Color>, default 3 seconds, begin to enumerate after Value seconds, this must be an integer
        you can delay a few seconds and make a window active so automation can enumerate the active window
<Color=Cyan>-d</Color>      enumerate tree <Color=Cyan>depth</Color>, this must be an integer, if it is null, enumerate the whole tree
<Color=Cyan>-r</Color>      enumerate from <Color=Cyan>root</Color>:desktop window, if it is null, enumerate from foreground window
<Color=Cyan>-f</Color>      enumerate from <Color=Cyan>focused</Color> control, if it is null, enumerate from foreground window
<Color=Cyan>-c</Color>      enumerate the control under <Color=Cyan>cursor</Color>, if depth is < 0, enumerate from its ancestor up to depth
<Color=Cyan>-a</Color>      show <Color=Cyan>ancestors</Color> of the control under cursor
<Color=Cyan>-n</Color>      show control full <Color=Cyan>name</Color>
<Color=Cyan>-m</Color>      show <Color=Cyan>more</Color> properties

if <Color=Red>UnicodeError</Color> or <Color=Red>LookupError</Color> occurred when printing,
try to change the active code page of console window by using <Color=Cyan>chcp</Color> or see the log file <Color=Cyan>@AutomationLog.txt</Color>
chcp, get current active code page
chcp 936, set active code page to gbk
chcp 65001, set active code page to utf-8

examples:
automation.py -t3
automation.py -t3 -r -d1 -m -n
automation.py -c -t3

""", writeToFile = False)


def main():
    # if not IsPy3 and sys.getdefaultencoding() == 'ascii':
    # reload(sys)
    # sys.setdefaultencoding('utf-8')
    import getopt
    Logger.Write('UIAutomation {} (Python {}.{}.{}, {} bit)\n'.format(VERSION, sys.version_info.major,
                                                                      sys.version_info.minor, sys.version_info.micro,
                                                                      64 if sys.maxsize > 0xFFFFFFFF else 32))
    options, args = getopt.getopt(sys.argv[1:], 'hrfcamnd:t:',
                                  ['help', 'root', 'focus', 'cursor', 'ancestor', 'showMore', 'showAllName', 'depth=',
                                   'time='])
    root = False
    focus = False
    cursor = False
    ancestor = False
    showAllName = False
    showMore = False
    depth = 0xFFFFFFFF
    seconds = 3
    for (o, v) in options:
        if o in ('-h', '-help'):
            usage()
            exit(0)
        elif o in ('-r', '-root'):
            root = True
        elif o in ('-f', '-focus'):
            focus = True
        elif o in ('-c', '-cursor'):
            cursor = True
        elif o in ('-a', '-ancestor'):
            ancestor = True
        elif o in ('-n', '-showAllName'):
            showAllName = True
        elif o in ('-m', '-showMore'):
            showMore = True
        elif o in ('-d', '-depth'):
            depth = int(v)
        elif o in ('-t', '-time'):
            seconds = int(v)
    if seconds > 0:
        Logger.Write('please wait for {0} seconds\n\n'.format(seconds), writeToFile=False)
        time.sleep(seconds)
    Logger.Log('Starts, Current Cursor Position: {}'.format(Win32API.GetCursorPos()))
    control = None
    if root:
        control = GetRootControl()
    if focus:
        control = GetFocusedControl()
    if cursor:
        control = ControlFromCursor()
        if depth < 0:
            while depth < 0:
                control = control.GetParentControl()
                depth += 1
            depth = 0xFFFFFFFF
    if ancestor:
        control = ControlFromCursor()
        if control:
            EnumAndLogControlAncestors(control, showAllName, showMore)
        else:
            Logger.Write('IUIAutomation return null element under cursor\n', ConsoleColor.Yellow)
    else:
        if not control:
            control = GetFocusedControl()
            controlList = []
            while control:
                controlList.insert(0, control)
                control = control.GetParentControl()
            if len(controlList) == 1:
                control = controlList[0]
            else:
                control = controlList[1]
        EnumAndLogControl(control, depth, showAllName, showMore)
    Logger.Log('Ends\n')

if __name__ == '__main__':
    main()
    # control = GetForegroundControl()
    # del control
    # If use control object in global area, must del the control when not use it, otherwise it may throw an exception.
    # The exception is ctypes was None when control's __del__ was called!
    # It seems that the module ctypes was deleted before control's __del__ was called.
    # _automationClient and control are all global objects, _automationClient may be deleted before control,
    # but control's __del__ uses _automationClient's member.
    # You'd better not use control object in global area.

    # https://docs.python.org/3/reference/datamodel.html

    # Warning

    # Due to the precarious circumstances under which __del__() methods are invoked,
    # exceptions that occur during their execution are ignored,
    # and a warning is printed to sys.stderr instead.
    # Also, when __del__() is invoked in response to a module being deleted(e.g., when execution of the program is done),
    # other globals referenced by the __del__() method may already have been deleted
    # or in the process of being torn down (e.g. the import machinery shutting down).
    # For this reason, __del__() methods should do the absolute minimum needed to maintain external invariants.
    # Starting with version 1.5, Python guarantees that globals whose name begins
    # with a single underscore are deleted from their module before other globals are deleted;
    # if no other references to such globals exist,
    # this may help in assuring that imported modules are
    # still available at the time when the __del__() method is called.

