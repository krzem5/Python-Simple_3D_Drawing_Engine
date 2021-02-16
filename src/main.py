import engine



CUBE=engine.ShapeBuffer([(-1,-1,-1),(-1,-1,1),(-1,1,1),(-1,1,-1),(1,-1,-1),(1,-1,1),(1,1,1),(1,1,-1)],[0,1,2,0,2,3,2,3,7,2,7,6,1,2,5,2,5,6,0,1,4,1,4,5,4,5,6,4,6,7,3,7,4,4,3,0],m=engine.LINES,cl="#000000")
c=engine.OrbitalCamera(0,0,0,0,0,4,0,1,0)
# c.lock(False)
# c.rotate_around(2)



def loop(dt):
	e.draw(CUBE)



__import__("ctypes").windll.user32.SetProcessDPIAware()
e=engine.Graphics(960,540)
e.background("#ffffff")
# e.camera(engine.StaticCamera(0,0,-4,0,0,0,0,1,0))
e.camera(c)
# e.projection(engine.ORTOGRAPHIC,1,-1,-1,1,0.01,1000)
e.projection(engine.PERSPECTIVE,45,0.01,1000)
e.window.attributes("-topmost",True)
e.window.resizable(False,False)
e.window.overrideredirect(True)
e.window.bind("<Escape>",lambda _:e.close())
w=e.window.winfo_screenwidth()
h=e.window.winfo_screenheight()
e.window.geometry(f"+{w//2-480}+{h//2-270}")
e.window.update_idletasks()
e.display(loop)
