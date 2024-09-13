from blessed import Terminal

term = Terminal()

with term.fullscreen():
    print(term.bold('This is fullscreen mode!'))
    print(term.move_y(term.height // 2) + 'Centered text')
    input('Press any key to exit fullscreen...')

