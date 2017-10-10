import networkx as nx
import numpy as np

class Grid:
    class Rect:
        def __init__(self, x, y, text, charh, charw):
            #self.x = x
            #self.y = y
            top = y - charh*0.5
            bot = y + charh*0.5
            left = x - (charw * len(text))*0.5
            right = x + (charw * len(text))*0.5
            self.vpos = np.array([y,top,bot])
            self.hpos = np.array([x,left,right])
            self.text = text

        def overlapsh(self, other):
            return self.hpos[1] < other.hpos[2] and self.hpos[2] > other.hpos[1]

        def overlapsv(self, other):
            return self.vpos[1] < other.vpos[2] and self.vpos[2] > other.vpos[1]

        def overlaps(self, other):
            return self.overlapsh(other) and self.overlapsv(other)

        @property
        def x(self):
            return self.hpos[0]
        @property
        def y(self):
            return self.vpos[0]
        
        def align(self, other, farther=False):
            #oh = self.overlaps(other)
            #ov = self.overlapsv(other)

            if self.overlaps(other):
                offxa = other.hpos[1] - self.hpos[2]
                offxb = other.hpos[2] - self.hpos[1]
                if np.abs(offxa) < np.abs(offxb):
                    offx = offxa
                else:
                    offx = offxb
                
                offya = other.vpos[1] - self.vpos[2]
                offyb = other.vpos[2] - self.vpos[1]
                if np.abs(offya) < np.abs(offyb):
                    offy = offya
                else:
                    offy = offyb
                    
                if farther:
                    a = np.random.randint(0,3)
                    offx = [0,offxa,offxb][a]
                    a = np.random.randint(0,3)
                    offy = [0,offya,offyb][a]
                    self.move(offx,offy)
                    
                elif np.abs(offx) < np.abs(offy):
                    self.move(offx,0)
                else:
                    self.move(0,offy)

                return True
            return False

        def move(self, offx, offy):
            self.hpos += offx
            self.vpos += offy
            
        def __repr__(self):
            return '{} ({:0.04f},{:0.04f})@({:0.04f},{:0.04f})'.format(self.text,self.hpos[1],self.vpos[1],self.hpos[2],self.vpos[2])
        
    def __init__(self,charh, charw):
        self.charh = charh
        self.charw = charw
        
        self.labels = []
        self.fixed = []
        
    def add_label(self,x,y,text):
        label = Grid.Rect(x,y,text,self.charh,self.charw)
        self.labels.append(label)
        return label
    
    def add_fixed_box(self,x,y,text):
        label = Grid.Rect(x,y,text,self.charh,self.charw)
        self.fixed.append(label)
        return label
    
    def resolve(self):
        for it in range(1000):
            moved = False
            has_moved = set()
            for i in self.fixed:
                for j in self.labels:
                    if j in has_moved:
                        if j.align(i,farther=True):
                            moved = True
                        
                    elif j.align(i):
                        moved = True
                        has_moved.add(j)
            
            for idx,i in enumerate(self.labels,start=1):
                for j in self.labels[idx:]:
                    if i in has_moved and j not in has_moved:
                        if j.align(i):
                            moved = True
                            has_moved.add(j)
                    elif i.align(j, farther=(i in has_moved)):
                        moved = True
                        has_moved.add(i)
            if not moved:
                break
                
def get_annotations(x,y,text,Kx,Ky,k,arrowhead=0,gKx=None,gKy=None):
    ann = []
    G=nx.Graph()

    data_nodes = []
    init_pos = {}
    node2ano = {}
    for j,(xi,yi,ti) in enumerate(zip(x,y,text)):
        data_str = 'data_{0}'.format(j)
        ano_str = 'ano_{0}'.format(j)
        G.add_node(data_str)
        G.add_node(ano_str)
        G.add_edge(data_str, ano_str)
        data_nodes.append(data_str)
        xi *= Kx
        yi *= Ky

        init_pos[data_str] = (xi, yi)
        node2ano[data_str] = (ti,ano_str)
        init_pos[ano_str] = (xi, yi)

    pos = nx.spring_layout(G, pos=init_pos, fixed=data_nodes, k=k)
    
    # Now do the grid solve
    if gKx is None:
        gKx = Kx*10.
    if gKy is None:
        gKy = Ky*15.
    
    grid = Grid(gKy,gKx)
    for i in data_nodes:
        if i not in node2ano:
            continue
        ti,ano = node2ano[i]
        
        px = pos[ano][0]/Kx
        py = pos[ano][1]/Ky
        grid.add_label(px,py,ti)
        
        #px = pos[i][0]/Kx
        #py = pos[i][1]/Ky
        #grid.add_fixed_box(px,py,'x')

    grid.resolve()
    resolved_pos = {}
    for label in grid.labels:
        resolved_pos[label.text] = [label.x,label.y]
    
    for i in data_nodes:
        if i not in node2ano:
            continue
        ti,ano = node2ano[i]
        ann.append(
            dict(
                x=pos[i][0]/Kx,
                y=pos[i][1]/Ky,
                xref='x',
                yref='y',
                text=ti,
                showarrow=True,
                arrowhead=arrowhead,
                ax=resolved_pos[ti][0], #pos[ano][0]/Kx,
                ay=resolved_pos[ti][1], #pos[ano][1]/Ky,
                arrowcolor='rgba(150,150,150,0.5)',
                bgcolor='rgba(255,255,255,0.4)',
                #ax=-(pos[i][0]-pos[ano][0])/Kx,
                #ay=(pos[i][1]-pos[ano][1])/Ky,
                axref='x',
                ayref='y',
                align='center',
                #font=dict(color=team_color[tm]),
                #arrowcolor=team_color[tm],
                arrowsize=0
            ))
    return ann