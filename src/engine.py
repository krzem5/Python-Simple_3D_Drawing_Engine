import tkinter
import time
import math



LINES=0
TRIANGLES=1
ORTOGRAPHIC=0
PERSPECTIVE=1



class BaseCamera:
	def __init__(self):
		pass



	def update(self,dt):
		raise NotImplementedError



	def __updated__(self):
		raise NotImplementedError



	def __recalc_matrix__(self,e):
		raise NotImplementedError



class BaseCanvasElement:
	def __init__(self):
		pass



	def __updated__(self):
		raise NotImplementedError



	def __recalc_flatten__(self,e):
		raise NotImplementedError



	def __flatten_data__(self):
		raise NotImplementedError



class StaticCamera(BaseCamera):
	def __init__(self,x,y,z,tx,ty,tz,ux,uy,uz):
		self.x=x
		self.y=y
		self.z=z
		self.tx=tx
		self.ty=ty
		self.tz=tz
		self.ux=ux
		self.uy=uy
		self.uz=uz
		self._u=True



	def update(self,dt):
		pass



	def __updated__(self):
		return self._u



	def __recalc_matrix__(self,e):
		self._u=False
		zx=self.tx-self.x
		zy=self.ty-self.y
		zz=self.tz-self.z
		m=math.sqrt(zx**2+zy**2+zz**2)
		zx/=m
		zy/=m
		zz/=m
		xx=self.uy*zz-self.uz*zy
		xy=self.uz*zx-self.ux*zz
		xz=self.ux*zy-self.uy*zx
		m=math.sqrt(xx**2+xy**2+xz**2)
		xx/=m
		xy/=m
		xz/=m
		yx=zy*xz-zz*xy
		yy=zz*xx-zx*xz
		yz=zx*xy-zy*xx
		return (xx,xy,xz,yx,yy,yz,zx,zy,zz,-xx*self.x-xy*self.y-xz*self.z,-yx*self.x-yy*self.y-yz*self.z,-zx*self.x-zy*self.y-zz*self.z)



class ShapeBuffer(BaseCanvasElement):
	__slots__=["vl","il","_m","_u","_dt"]



	def __init__(self,vl,il,m=LINES,cl="#ffffff"):
		self.vl=vl
		self.il=il
		self.m=m
		self.cl=cl
		self._u=True
		self._dt=(tuple(),tuple())



	def __updated__(self):
		return self._u



	def __recalc_flatten__(self,e):
		self._u=False
		tp=[]
		for k in self.vl:
			tp.append(e._transform(*k))
		if (self.m==LINES):
			ll=[]
			for i in range(0,len(self.il),3):
				t=self.il[i:i+3]
				if ((tp[t[0]][2]>=0 and tp[t[0]][2]<=1) or (tp[t[1]][2]>=0 and tp[t[1]][2]<=1)):
					ll.append((tp[t[0]][0],tp[t[0]][1],tp[t[1]][0],tp[t[1]][1],self.cl))
				else:
					print(f"Skip: {tp[t[0]]} -> {tp[t[1]]}")
				if ((tp[t[1]][2]>=0 and tp[t[1]][2]<=1) or (tp[t[2]][2]>=0 and tp[t[2]][2]<=1)):
					ll.append((tp[t[1]][0],tp[t[1]][1],tp[t[2]][0],tp[t[2]][1],self.cl))
				else:
					print(f"Skip: {tp[t[1]]} -> {tp[t[2]]}")
				if ((tp[t[2]][2]>=0 and tp[t[2]][2]<=1) or (tp[t[0]][2]>=0 and tp[t[0]][2]<=1)):
					ll.append((tp[t[2]][0],tp[t[2]][1],tp[t[0]][0],tp[t[0]][1],self.cl))
				else:
					print(f"Skip: {tp[t[2]]} -> {tp[t[0]]}")
			self._dt=(tuple(ll),tuple())
		elif (self.m==TRIANGLES):
			print("Tri")



	def __flatten_data__(self):
		return self._dt



class Graphics:
	def __init__(self,w,h,bg="#000000"):
		self.w=w
		self.h=h
		self._r=tkinter.Tk()
		self._r.title("")
		self._r.geometry(f"{w}x{h}")
		self._c=tkinter.Canvas(self._r,width=w,height=h,highlightthickness=0,background=bg)
		self._c.pack()
		self._r.update_idletasks()
		self._cm=None
		self._c_m=()
		self._pr=()
		self._p_u=False
		self._p_m=()
		self._cb=None
		self._lt=0
		self._ll=[]
		self._tl=[]



	@property
	def window(self):
		return self._r



	def background(self,bg):
		self._c["background"]=bg



	def camera(self,c):
		if (not isinstance(c,BaseCamera)):
			raise RuntimeError(f"Camera of Type '{e.__class__.__name__}' is not compatible!")
		self._cm=c



	def projection(self,t,*a):
		if (t==ORTOGRAPHIC):
			raise RuntimeError
		elif (t==PERSPECTIVE):
			if (len(a)!=3):
				raise TypeError(f"Perspective Projection requires 3 Arguments (FOV, near, far)!")
			self._pm=(t,a[0],a[1],a[2])
		else:
			raise NameError(f"Unknown Projection Type Value '{t}'!")
		self._update_p()



	def draw(self,e):
		if (not isinstance(e,BaseCanvasElement)):
			raise RuntimeError(f"Element of Type '{e.__class__.__name__}' is not compatible!")
		if (e.__updated__()):
			e.__recalc_flatten__(self)
		ll,tl=e.__flatten_data__()
		self._ll.extend(ll)
		self._tl.extend(tl)



	def display(self,cb):
		self._cb=cb
		self._r.after(1,self._loop)
		self._r.mainloop()



	def close(self):
		self._r.destroy()



	def _loop(self):
		tm=time.time()
		if (self._lt==0):
			self._lt=tm
		self._ll=[]
		self._tl=[]
		self._cm.update(tm-self._lt)
		if (self._cm.__updated__()):
			self._c_m=self._cm.__recalc_matrix__(self)
		self._cb(tm-self._lt)
		self._c.delete(tkinter.ALL)
		if (self._p_u):
			self._p_u=False
			self._update_p()
		for e in self._ll:
			self._c.create_line(e[0],e[1],e[2],e[3],fill=e[4])
		for e in self._tl:
			self._c.create_polygon(*e,fill="#00ff00")
		self._lt=tm
		self._r.after(1,self._loop)



	def _update_p(self):
		yScale=math.cos(self._pm[1]/360*math.pi)/math.sin(self._pm[1]/360*math.pi)
		xScale=yScale/self.h*self.w
		self._p_m=(xScale,0,0,0,yScale,0,0,0,(self._pm[3]+self._pm[2])/(self._pm[3]-self._pm[2]),0,0,(2*self._pm[2]*self._pm[3])/(self._pm[2]-self._pm[3]))



	def _transform(self,x,y,z):
		nx=x*self._c_m[0]+y*self._c_m[3]+z*self._c_m[6]+self._c_m[9]
		ny=x*self._c_m[1]+y*self._c_m[4]+z*self._c_m[7]+self._c_m[10]
		nz=x*self._c_m[2]+y*self._c_m[5]+z*self._c_m[8]+self._c_m[11]
		nnx=(nx*self._p_m[0]+ny*self._p_m[3]+nz*self._p_m[6]+self._p_m[9])/nz
		nny=(nx*self._p_m[1]+ny*self._p_m[4]+nz*self._p_m[7]+self._p_m[10])/nz
		return ((nnx*self.w)/(2*nz)+self.w/2,(nny*self.h)/(2*nz)+self.h/2,(nx*self._p_m[2]+ny*self._p_m[5]+nz*self._p_m[8]+self._p_m[11])/nz)
