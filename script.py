import mdl
import os
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass( commands ):
    command_frames = False
    command_basename = False
    command_vary = False
    frames = 1
    basename = 'default_file_name'

    for command in commands:
        c = command[0]
        args = command[1:]
        
        if c == 'frames':
            command_frames = True
            frames = args[0]
            
        elif c == 'basename':
            command_basename = True
            basename = args[0]

        elif c == 'vary':
            command_vary = True

    if (command_frames and not command_basename):
        print 'No basename given. Using filename "default_file_name"'

    if (command_vary and not command_frames):
        print 'Need frames command if using vary'
        exit

    return (frames, basename)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames):
    symbols = [{} for i in range(num_frames)]
    
    for command in commands:
        print command
        c = command[0]
        args = command[1:]

        if c == 'set':
            name = args[0]
            val = args[1]
            for i in range(num_frames):
                symbols[i][name] = val
        if c == 'setall':
            val = args[0]
            for i in range(num_frames):
                for key in symbols[i]:
                    symbols[i][key] = val
        if c == 'vary':
            name = args[0]
            ti = args[1] #start frame
            tf = args[2] + 1 #end frame
            xi = args[3] #start value
            xf = args[4] #end value
            for i in range(ti, tf):
                val = xi + 1.0*(xf - xi)*(i - ti)/(tf - ti)
                symbols[i][name] = (val, 'knob')

    #print symbols
    return symbols

def run(filename):
    "function runs an mdl file"
    color = [255, 255, 255]
  
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    screen = new_screen()
    tmp = []
    step = 0.1

    (frames, basename) = first_pass(commands)
    print "frames: " + str(frames)
    print "basename: " + basename

    if frames > 1:
        symbols = second_pass(commands, frames)
        os.chdir('anim')

    for i in range(frames):
        clear_screen( screen)
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        print stack

        
        if frames > 1:
            file_name = basename + "%03d"%i + ".png"
        else:
            file_name = basename + ".png"
            
        #print file_name
        is_saved = False

        if frames > 1: symbol_vals = symbols[i]
        print symbol_vals
        for command in commands:
            #print command
            c = command[0]
            args = command[1:]
                
            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp, args[0], args[1], args[2], args[3], step)
                #print tmp
                #print stack[-1]
                matrix_mult( stack[-1], tmp )
                #print "\n"*5 + str(tmp)
                draw_polygons(tmp, screen, color)
                #print screen
                tmp = []
            elif c == 'torus':
                add_torus(tmp, args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                if args[3] == None:
                    tmp = make_translate(args[0], args[1], args[2])
                else:
                    if args[3] in symbol_vals:
                        knob = symbol_vals[args[3]][0]
                    else: knob = 0
                    knob = symbol_vals[args[3]][0]
                    tmp = make_translate(knob*args[0], knob*args[1], knob*args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if  args[3] == None:
                    tmp = make_scale(args[0], args[1], args[2])
                else:
                    if args[3] in symbol_vals:
                        knob = symbol_vals[args[3]][0]
                    else: knob = 0
                    #print "\n\n \t -- knob = " + str(knob)
                    tmp = make_scale(knob*args[0], knob*args[1], knob*args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if args[2] == None:
                    knob = 1
                elif args[2] in symbol_vals:
                    knob = symbol_vals[args[2]][0]
                else: knob = 0
                
                theta = knob * args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                file_name = args[0] if args[0] != None else file_name
                save_extension(screen, file_name)
                is_saved = True

        if (not is_saved):
            #print screen
            save_extension(screen, file_name)
                                
    make_animation(basename)
