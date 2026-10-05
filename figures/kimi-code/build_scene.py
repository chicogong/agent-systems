"""Build the editable Kimi Code steer-boundary diagram."""
import json
from pathlib import Path
E=[]
def base(t,i,x,y,w,h,c='#24324a',f='transparent',r=1,sw=2):
 return dict(id=i,type=t,x=x,y=y,width=w,height=h,angle=0,strokeColor=c,backgroundColor=f,fillStyle='solid',strokeWidth=sw,strokeStyle='solid',roughness=r,opacity=100,groupIds=[],frameId=None,roundness={'type':3} if t=='rectangle' else None,seed=sum(map(ord,i)),version=1,versionNonce=1,isDeleted=False,boundElements=None,updated=1,link=None,locked=False)
def box(i,x,y,w,h,c,f): E.append(base('rectangle',i,x,y,w,h,c,f))
def label(i,x,y,w,h,s,z=23,c='#1e293b'):
 d=base('text',i,x,y,w,h,c,r=0,sw=1);d.update(text=s,originalText=s,fontSize=z,fontFamily=8,textAlign='left',verticalAlign='top',lineHeight=1.25,autoResize=False,containerId=None);E.append(d)
def arrow(i,x,y,X,Y,c='#2563a6'):
 d=base('arrow',i,x,y,X-x,Y-y,c,sw=3);d.update(points=[[0,0],[X-x,Y-y]],lastCommittedPoint=None,startBinding=None,endBinding=None,startArrowhead=None,endArrowhead='arrow',elbowed=False);E.append(d)
label('title',50,28,1190,47,'Kimi Code：忙时收下新要求，下一步再处理',34,'#172554')
label('subtitle',53,82,1160,34,'当前一步继续运行；下一步开始前，取出新要求。',22,'#475569')
box('upper',45,143,1190,258,'#d3e4f4','#f8fbff');label('upper-label',65,157,500,34,'工作回合正在进行（turn）',23,'#1d4f75')
for i,x,w,c,f,s in [('incoming',66,195,'#7aa9d5','#e7f2fc','补充新要求\nsteer(input)'),('buffer',316,205,'#7aa9d5','#e7f2fc','忙时先存输入\nsteerBuffer'),('flush',580,230,'#3b8a79','#e2f4ec','下一步前取输入\nbeforeStep'),('model',871,329,'#3b8a79','#e2f4ec','准备模型消息\nexecuteLoopStep')]:
 box(i,x,217,w,108,c,f);label(i+'-text',x+12,239,w-24,62,s,22)
for i,x,X in [('a',261,311),('b',521,575),('c',810,866)]:arrow(i,x,271,X,271)
label('not-interrupt',326,341,870,38,'当前模型请求或工具继续，新要求等待下一步。',22,'#58677b')
box('lower',45,421,1190,229,'#e5dcf2','#fcfaff');label('lower-label',65,435,700,34,'准备结束时，再检查输入等待区',23,'#644b86')
box('stop',68,494,250,89,'#a791c7','#f0e9f9');label('stop-text',89,507,210,60,'模型未请求工具\n非 tool_use',22)
box('check',395,494,278,89,'#a791c7','#f0e9f9');label('check-text',417,507,234,60,'取出等待输入\n检查 steerBuffer',22)
box('yes',775,475,425,67,'#3b8a79','#e2f4ec');label('yes-text',795,492,380,39,'有新要求 → 继续一步（step）',22)
box('no',775,565,425,67,'#c98a89','#fff0ed');label('no-text',795,573,380,55,'无新要求 → 检查目标结果\n与 Stop 回调，再决定继续或结束',21)
arrow('d',318,539,390,539,'#7656a3');arrow('e',673,519,770,510,'#3b8a79');arrow('f',673,559,770,599,'#b35e5e')
label('guard',70,664,1140,38,'取消、步数上限或异常 → 提前结束回合（turn）',22,'#6b4d46')
scene={'type':'excalidraw','version':2,'source':'agent-systems/kimi-code','elements':E,'appState':{'viewBackgroundColor':'#ffffff'},'files':{}}
(Path(__file__).parent/'scene.excalidraw').write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
