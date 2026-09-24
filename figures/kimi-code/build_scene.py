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
label('title',50,28,1190,47,'Kimi Code：新指令何时被模型看见？',34,'#172554')
label('subtitle',53,82,1160,34,'steer 在 step 边界进入上下文；停止前还会检查缓冲。',22,'#475569')
box('upper',45,143,1190,258,'#d3e4f4','#f8fbff');label('upper-label',65,157,500,34,'进行中的 turn',23,'#1d4f75')
for i,x,w,c,f,s in [('incoming',66,195,'#7aa9d5','#e7f2fc','新指令\nsteer(input)'),('buffer',316,205,'#7aa9d5','#e7f2fc','活动 turn\n写入缓冲'),('flush',580,230,'#3b8a79','#e2f4ec','beforeStep\n刷新缓冲'),('model',871,329,'#3b8a79','#e2f4ec','上下文更新\n下一 step 模型请求')]:
 box(i,x,217,w,108,c,f);label(i+'-text',x+21,239,w-42,62,s)
for i,x,X in [('a',261,311),('b',521,575),('c',810,866)]:arrow(i,x,271,X,271)
label('not-interrupt',326,341,870,38,'缓冲不取消正在运行的 step。',22,'#58677b')
box('lower',45,421,1190,229,'#e5dcf2','#fcfaff');label('lower-label',65,435,590,34,'模型原本准备停止时',23,'#644b86')
box('stop',68,494,250,89,'#a791c7','#f0e9f9');label('stop-text',89,518,210,40,'非 tool_use 停止',22)
box('check',395,494,278,89,'#a791c7','#f0e9f9');label('check-text',417,514,234,57,'停止前刷新缓冲\n还有 steer？',22)
box('yes',775,475,425,67,'#3b8a79','#e2f4ec');label('yes-text',795,492,380,39,'有 → 继续下一 step',22)
box('no',775,565,425,67,'#c98a89','#fff0ed');label('no-text',795,582,380,38,'无 → 检查其他续跑条件／结束',22)
arrow('d',318,539,390,539,'#7656a3');arrow('e',673,519,770,510,'#3b8a79');arrow('f',673,559,770,599,'#b35e5e')
label('guard',70,664,1140,38,'取消、步数上限或异常仍可终止 turn。',22,'#6b4d46')
scene={'type':'excalidraw','version':2,'source':'agent-systems/kimi-code','elements':E,'appState':{'viewBackgroundColor':'#ffffff'},'files':{}}
(Path(__file__).parent/'scene.excalidraw').write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
