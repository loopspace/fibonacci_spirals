import subprocess

SCALE = 1
PHI = 0.5*(5**0.5-1) # scale factor
LEN = 8 # how many iterations
D = 144 # angle (in degrees) for each arc
R = 5. # radius of largest circle
SA = 30 # start angle
TEX = "lualatex" # Use lualatex
OPEN = "xdg-open" # Linux 

# this is a bit wasteful, but I think a simple thing that works is probably better than a complicated calculation. 
def curve(n):
    """Plot a curve that goes in different directions depending on the binary expansion of the argument"""
    r = R
    b = bin(n)[2:] # chop off the 0b at the beginning
    while len(b)<LEN:
        b = "0" + b # make sure the binary numbers are all the same length

    a = SA

    direction = +1 
    out = "\draw[color=black] (0,0) "
    for bi in b:
        if bi == '0':
            out += f"arc[radius={r}, start angle={a}, delta angle={D*direction}] " # continue in the same direction
            a = (a+D*direction) % 360
        else:
            direction *= -1
            a = (a+180) % 360 # switch direction and reduce radius
            r *= PHI
            out += f"arc[radius={r}, start angle={a}, delta angle={D*direction}] "
            a = (a+direction*D) % 360
        r *= PHI # reduce radius
    return out + ";"

def curves():
    """plot all of the possible curves"""
    return "\n".join([curve(i) for i in range(2**LEN)])

def full_file():
    """Use standalone class for single-image documents."""
    out = r"""\documentclass[border=10pt,tikz]{standalone}
\begin{document}

"""

    for f in [curves]:
        out += "\\begin{tikzpicture}[x=" +  f"{SCALE}cm, y={SCALE}cm]\n" + f() + "\n\\end{tikzpicture}\n\n"
    out += r"\end{document}"
    return out
    
fn = "fibo"
tfn =   fn + ".tex"
ofn = fn + ".pdf"
with open(tfn,'w') as f:
    f.write(full_file())

# compile it


subprocess.call(f"{TEX} {tfn} -o {ofn}", shell =True, executable = '/bin/zsh')
#subprocess.call(f"{OPEN} {ofn}",shell =True, executable = '/bin/zsh')
