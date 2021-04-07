import subprocess
import math
import argparse
import platform

parser = argparse.ArgumentParser(description="Generate a Fibonacci spiral")

parser.add_argument('-l','--lua',help="Use lualatex to compile document", action="store_true")
parser.add_argument('-x','--xe',help="Use xelatex to compile document", action="store_true")
parser.add_argument('-v','--view',help="View PDF afterwards", action="store_true")
parser.add_argument('-t','--tikz',help="Create TikZ code", action="store_true")
parser.add_argument('-s','--svg',help="Create SVG code", action="store_true")
parser.add_argument('-c','--colour','--color',nargs='?', default='black', help="Set the line colour")
parser.add_argument('-w','--linewidth','--line-width', '--strokewidth', '--stroke-width',nargs='?', default='1', help="Set the line width")

args = parser.parse_args()

SCALE = 1
PHI = 0.5*(5**0.5-1) # scale factor
LEN = 8 # how many iterations
D = 144 # angle (in degrees) for each arc
R = 5. # radius of largest circle
SA = 30 # start angle

# Set line colour
if args.colour:
    COLOUR = args.colour
else:
    COLOUR = "black"

# Set line width
if args.linewidth:
    WIDTH = args.linewidth
else:
    WIDTH = 1

# Set TeX engine
TEX = "pdflatex"
if args.lua:
    TEX = "lualatex"
if args.xe:
    TEX = "xelatex"

# If requested, how to view the PDF afterwards
SHOW = args.view

if platform.system() == "Linux":
    OPEN = "xdg-open" # Linux
elif platform.system() == "Darwin":
    OPEN = "open" # Mac OS
else:
    OPEN = "" # Dunno what to do for Windows
    SHOW = False

if args.svg:
    R *= 10
    TIKZ = False
    curve_start = r'<path d="'
    curve_end = r'" />'
    picture_start = f'<g stroke="{COLOUR}" fill="none" stroke-width="{WIDTH}">'
    picture_end = r'</g>'
    preamble = r"""<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTDSVG1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="-150 -150 300 300" width="100%" height="100%">
"""
    postamble = r"</svg>"
    move = lambda x,y: f"M {x:.2f} {y:.2f} "
    arc = lambda r,a,D,d,x,y: f"A {r:.2f} {r:.2f} 0 0 {int((d+1)/2)} {x:.2f} {y:.2f} "
else:
    TIKZ = True
    curve_start = r"\draw "
    curve_end = r";"
    picture_start = "\\begin{tikzpicture}" + f"[linewidth={WIDTH} pt, color={COLOUR}, x={SCALE}cm, y={SCALE}cm]\n"
    picture_end = "\n\\end{tikzpicture}\n\n"
    preamble = r"""\documentclass[border=10pt,tikz]{standalone}
\begin{document}

"""
    postamble = r"\end{document}"
    move = lambda x,y: f"({x},{y}) "
    arc = lambda r,a,D,d,x,y: f"arc[radius={r}, start angle={a}, delta angle={D*d}] "

# this is a bit wasteful, but I think a simple thing that works is probably better than a complicated calculation. 
def curve(n):
    """Plot a curve that goes in different directions depending on the binary expansion of the argument"""
    r = R
    a = SA
    direction = +1
    out = curve_start
    x = 0
    y = 0
    if n == 0:
        out += move(0,0)
    
    for i in range(LEN):
        if n%2 == 1:
            direction *= -1
            a = (a+180) % 360 # switch direction and reduce radius
            r *= PHI
        if n == 1: # are we ready to start drawing?
            out += move(x,y)
        # update starting point of next maybe-arc
        x += -r*math.cos(a * math.pi/180) + r*math.cos( (a + D*direction) * math.pi/180)
        y += -r*math.sin(a * math.pi/180) + r*math.sin( (a + D*direction) * math.pi/180)
        if n <= 1: # are we drawing?
            out += arc(r,a,D,direction,x,y)
        a = (a+direction*D) % 360
        r *= PHI # reduce radius
        n >>= 1
    return out + curve_end

def curves():
    """plot all of the possible curves"""
    return "\n".join([curve(i) for i in range(2**LEN)])

def full_file():
    """Use standalone class for single-image documents."""
    out = preamble

    for f in [curves]:
        out += picture_start + f() + picture_end
    out += postamble
    return out
    
fn = "fibo"
if TIKZ:
    tfn =   fn + ".tex"
    ofn = fn + ".pdf"
else:
    tfn =   fn + ".svg"
    ofn = tfn
    
with open(tfn,'w') as f:
    f.write(full_file())

# compile it

if TIKZ:
    subprocess.call(f"{TEX} {tfn} -o {ofn}", shell =True, executable = '/bin/zsh')
if SHOW:
    subprocess.call(f"{OPEN} {ofn}",shell =True, executable = '/bin/zsh')
