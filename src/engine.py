import tkinter
import time
import math



LINES=0
TRIANGLES=1
ORTOGRAPHIC=0
PERSPECTIVE=1
EPSILON=0.0001



class BaseCamera:
	def __init__(self):
		pass



	def __setup_cam__(self,e):
		raise NotImplementedError



	def __update__(self,dt):
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



	def __setup_cam__(self,e):
		pass



	def __update__(self,dt):
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



class OrbitalCamera(BaseCamera):
	def __init__(self,x,y,z,rx,ry,d,ux,uy,uz):
		self.x=x
		self.y=y
		self.z=z
		self.rx=rx
		self.ry=ry
		self.d=d
		self.ux=ux
		self.uy=uy
		self.uz=uz
		self._ra=0
		self._l=True
		self._d=None
		self._u=True



	def lock(self,l):
		self._l=l



	def rotate_around(self,t):
		self._ra=2*math.pi/t



	def __setup_cam__(self,e):
		def _up(_):
			if (self._l):
				self.d=min(self.d+0.05,20)
				self._u=True
		def _down(_):
			if (self._l):
				self.d=max(self.d-0.05,0.05)
				self._u=True
		def _drag(a):
			if (self._d is not None):
				if (self._l):
					self.rx=min(max(self.rx-(a.y-self._d[1])*0.01,EPSILON),math.pi)
					# self.ry+=(a.x-self._d[0])*0.01
					self._u=True
			self._d=(a.x,a.y)
		def _drag_stop(_):
			self._d=None
		e.bind_key("<Up>",_up)
		e.bind_key("<Down>",_down)
		e.bind_key("<B1-Motion>",_drag)
		e.bind_key("<ButtonRelease-1>",_drag_stop)



	def __update__(self,dt):
		self.ry+=self._ra*dt
		if (self._ra):
			self._u=True



	def __updated__(self):
		return self._u



	def __recalc_matrix__(self,e):
		self._u=False
		px=math.sin(self.rx)*math.cos(self.ry)*self.d
		py=math.cos(self.rx)*self.d
		pz=math.sin(self.rx)*math.sin(self.ry)*self.d
		m=math.sqrt(px**2+py**2+pz**2)
		zx=-px/m
		zy=-py/m
		zz=-pz/m
		px+=self.x
		py+=self.y
		pz+=self.z
		xx=self.uy*zz-self.uz*zy
		xy=self.uz*zx-self.ux*zz
		xz=self.ux*zy-self.uy*zx
		m=math.sqrt(xx**2+xy**2+xz**2)
		if (m==0):
			m=1
		xx/=m
		xy/=m
		xz/=m
		yx=zy*xz-zz*xy
		yy=zz*xx-zx*xz
		yz=zx*xy-zy*xx
		return (xx,xy,xz,yx,yy,yz,zx,zy,zz,-xx*px-xy*py-xz*pz,-yx*px-yy*py-yz*pz,-zx*px-zy*py-zz*pz)



class ShapeBuffer(BaseCanvasElement):
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
				ll.append((tp[t[0]][0],tp[t[0]][1],tp[t[1]][0],tp[t[1]][1],self.cl))
				ll.append((tp[t[1]][0],tp[t[1]][1],tp[t[2]][0],tp[t[2]][1],self.cl))
				ll.append((tp[t[2]][0],tp[t[2]][1],tp[t[0]][0],tp[t[0]][1],self.cl))
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
		self._f_u=False
		self._kb={}



	@property
	def window(self):
		return self._r



	def background(self,bg):
		self._c["background"]=bg



	def bind_key(self,k,f):
		def _cb(a,k=k):
			for f in self._kb[k]:
				f(a)
		if (k not in self._kb):
			self._r.bind(k,lambda a:_cb(a))
			self._kb[k]=[f]
		else:
			self._kb[k]+=[f]



	def camera(self,c):
		if (not isinstance(c,BaseCamera)):
			raise RuntimeError(f"Camera of Type '{e.__class__.__name__}' is not compatible!")
		self._cm=c
		self._cm.__setup_cam__(self)



	def projection(self,t,*a):
		if (t==ORTOGRAPHIC):
			if (len(a)!=6):
				raise TypeError(f"Ortographic Projection requires 6 Arguments (top, left, bottom, right, near, far)!")
			self._pm=(t,a[0],a[1],a[2],a[3],a[4],a[5])
		elif (t==PERSPECTIVE):
			if (len(a)!=3):
				raise TypeError(f"Perspective Projection requires 3 Arguments (fov, near, far)!")
			self._pm=(t,math.cos(a[0]/360*math.pi)/math.sin(a[0]/360*math.pi),a[1],a[2])
		else:
			raise NameError(f"Unknown Projection Type Value '{t}'!")
		self._update_p()



	def draw(self,e):
		if (not isinstance(e,BaseCanvasElement)):
			raise RuntimeError(f"Element of Type '{e.__class__.__name__}' is not compatible!")
		if (e.__updated__() or self._f_u):
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
		self._f_u=False
		self._cm.__update__(tm-self._lt)
		if (self._cm.__updated__()):
			self._c_m=self._cm.__recalc_matrix__(self)
			self._f_u=True
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
		if (self._pm[0]==ORTOGRAPHIC):
			t,l,b,r=self._pm[1:5]
			self._p_m=(2/(r-l),0,0,0,2/(t-b),0,0,0,-2/(self._pm[6]-self._pm[5]),-(r+l)/(r-l),-(t+b)/(t-b),(self._pm[6]+self._pm[5])/(self._pm[6]-self._pm[5]))
		else:
			self._p_m=(self._pm[1]/self.w*self.h,0,0,0,self._pm[1],0,0,0,(self._pm[3]+self._pm[2])/(self._pm[3]-self._pm[2]),0,0,(2*self._pm[2]*self._pm[3])/(self._pm[2]-self._pm[3]))



	def _transform(self,x,y,z):
		nx=x*self._c_m[0]+y*self._c_m[3]+z*self._c_m[6]+self._c_m[9]
		ny=x*self._c_m[1]+y*self._c_m[4]+z*self._c_m[7]+self._c_m[10]
		nz=x*self._c_m[2]+y*self._c_m[5]+z*self._c_m[8]+self._c_m[11]
		nnx=(nx*self._p_m[0]+ny*self._p_m[3]+nz*self._p_m[6]+self._p_m[9])/((nz if nz!=0 else EPSILON) if self._pm[0]==PERSPECTIVE else 1)
		nny=(nx*self._p_m[1]+ny*self._p_m[4]+nz*self._p_m[7]+self._p_m[10])/((nz if nz!=0 else EPSILON) if self._pm[0]==PERSPECTIVE else 1)
		return ((nnx*self.w)/(2*nz if nz!=0 else EPSILON)+self.w/2,(nny*self.h)/(2*nz if nz!=0 else EPSILON)+self.h/2,(nx*self._p_m[2]+ny*self._p_m[5]+nz*self._p_m[8]+self._p_m[11])/((nz if nz!=0 else EPSILON) if self._pm[0]==PERSPECTIVE else 1))
