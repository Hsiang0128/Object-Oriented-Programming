import random
import os
import pygame
from pygame.locals import *
class MyObject():
    def __init__(self,rect):
        self.rect = pygame.Rect(rect)
    def setxy(self,x,y):
        self.rect.x = x
        self.rect.y = y
    def drawHitbow(self,surface,color):
        pygame.draw.rect(surface,color,self.rect, 2)
    def isHittingby(self,object):
        return self.rect.contains(object)
class GravityObject(MyObject):
    def __init__(self,rect,accelerationGravity,obstacleList = None):
        MyObject.__init__(self,rect)
        self.obstacleList = obstacleList
        self.accelerationGravity = accelerationGravity
        self.speedGravity = 0
        self.isFalling = True
    def setSpeedGravity(self,val):
        self.speedGravity = val
    def updateGravity(self):
        if(self.obstacleList != None):
            if(not self.obstacleList.isCrashOn(self,"DOWN",self.speedGravity)):
                self.isFalling = True
                self.rect.y += self.speedGravity
                self.speedGravity += self.accelerationGravity
            else:
                if(self.isFalling):
                    self.rect.y = self.obstacleList.getGameObject().rect.top-self.rect.height-1
                self.isFalling = False
                self.speedGravity = self.accelerationGravity
        else:
            self.rect.y += self.speedGravity
            self.speedGravity += self.accelerationGravity

class AnimationObject():
    def __init__(self,fps,rect,isEnable = False):
        self.src = []
        self.rect = rect
        self.isEnable = isEnable
        self.fps = fps
        self.fps_count = 0
        self.frame = 0
        self.folder = None
        self.prevFolder = None
    def appendAnimation(self,folder_name):
        folder = os.listdir(folder_name)
        tmp = [folder_name.split("/")[-1]]
        isExist = False
        for index in self.src:
            if(index[0]==folder_name):
                isExist = True
                break
        for file_name in folder:
            tmp.append(pygame.image.load(folder_name+"/"+file_name))
        if(isExist):
            self.src[index]=tmp
        else:
            self.src.append(tmp)
    def appendAnimationFolder(self,src):
        folder = os.listdir(src)
        for state in folder :
            self.appendAnimation(src + "/" + state)
    def enableAnimation(self,isEnable):
        self.isEnable = isEnable
    def setAnimationState(self,folder_name):
        self.folder = folder_name
    def drawAnimation(self,surface):
        for index in self.src:
            if(index[0]==self.folder):
                break
        if(self.prevFolder == self.folder and self.isEnable):
            if(self.fps_count == 0):
                self.fps_count = 60 / self.fps - 1
                if(self.frame >= len(index)-2):
                    self.frame = 0
                else:
                    self.frame += 1
            else:
                self.fps_count -= 1
        else:
            self.prevFolder = self.folder
            self.frame = 0
        locate = pygame.Rect(self.rect.x-index[self.frame+1].get_rect().width/2+self.rect.width/2,self.rect.y-index[self.frame+1].get_rect().height+self.rect.height,self.rect.width,self.rect.height)
        surface.blit(index[self.frame+1],locate)

class GameObject(GravityObject):
    def __init__(self,x,y,src,accelerationGravity = 0,obstacleList = None):
        self.src = src
        self.image = pygame.image.load(self.src)
        GravityObject.__init__(self,self.image.get_rect(),accelerationGravity,obstacleList)
        self.setxy(x,y)
        self.removed = False
        self.enabledDraw = True
    def isCrashOn(self,object,vector = None,variation = None):
        if (self.rect.colliderect(object)):
            return True
        else:
            return False
    def setEnabledDraw(self,en):
        self.enabledDraw = en
    def isEnabledDraw(self):
        return self.enabledDraw
    def updateGameObject(self,surface):
        pass
    def drawGameObject(self,surface):
        self.updateGameObject(surface)
        if(self.enabledDraw):
            self.updateGravity()
            surface.blit(self.image, (self.rect))
            #self.drawHitbow(surface,(0,0,255))
    def getGameObjectName(self):
        string = self.src
        string = ((string.split("/")[-1]).split(".png")[0]).split("_")[0]
        return string
    def shouldRemove(self):
        return self.removed
    def removeGameObject(self):
        self.removed = True
class GameObjectList():
    def __init__(self):
        self.gameObjectList=[]
        self.touchedObject = None
    def appendGameObject(self,obstacle):
        self.gameObjectList.append(obstacle)
    def tidyFromGameObjectList(self,object = None):
        if(object !=None):
            object.removeGameObject()
            self.tidyFromGameObjectList()
        else:
            for item in self.gameObjectList:
                if(item.shouldRemove()):
                    self.gameObjectList.remove(item)
    def drawGameObject(self,surface):
        self.tidyFromGameObjectList()
        for item in self.gameObjectList:
                item.drawGameObject(surface)
    def isCrashOn(self,object,vector = None,variation = None,mask = []):
        self.tidyFromGameObjectList()
        for item in self.gameObjectList:
            if(mask.count(item.getGameObjectName())==0):
                if(item.isCrashOn(object,vector,variation)):
                    self.touchedObject = item
                    return True
        return False
    def getGameObject(self):
        return self.touchedObject
class MyBar():
    def __init__(self,folder,width,health):
        self.rect = pygame.Rect(0,0,width,16)
        self.appendMyBar(folder)
        self.health = health
        self.maxHealth = 3
        self.shieldTimes = 0
    def setxy(self,x,y):
        self.rect.x=x
        self.rect.y=y
    def appendMyBar(self,folder):
        self.itemBar = []
        file_names = os.listdir(folder)
        for item in file_names:
            self.itemBar.append([(item.split("/")[-1]).split(".png")[0],pygame.image.load(folder + "/" + item)])
    def getItemBar(self,index):
        for item in (self.itemBar):
            if(item[0] == index):
                return item[1]
    def drawBar(self,surface):
        self.drawBarHealth(surface)
        self.drawBarShield(surface)
        self.drawBarScore(surface)
    def drawBarHealth(self,surface):
        for i in range (self.maxHealth):
            if(i<self.health):
                item = self.getItemBar("Health_1")
            else:
                item = self.getItemBar("Health_2")
            surface.blit(item,(self.rect.x+i*20,self.rect.y,16,16))
    def drawBarShield(self,surface):
        font = pygame.font.Font(None, 20)
        text = "x "+str(self.shieldTimes)
        text_surface = font.render(text, True, (48, 48, 48)) 
        text_rect = pygame.Rect(self.rect.x+(self.maxHealth+1)*20,self.rect.y+(16-text_surface.get_rect().height),text_surface.get_rect().width,text_surface.get_rect().height)
        surface.blit(self.getItemBar("Shield"),(self.rect.x+self.maxHealth*20,self.rect.y,16,16))
        surface.blit(text_surface,text_rect)
    def drawBarScore(self,surface):
        font = pygame.font.Font(None, 20)
        text = "SCORE: "+str(int(pygame.time.get_ticks()/1000))
        text_surface = font.render(text, True, (48, 48, 48)) 
        text_rect = pygame.Rect(self.rect.x+self.rect.width-text_surface.get_rect().width,self.rect.y+(16-text_surface.get_rect().height),text_surface.get_rect().width,text_surface.get_rect().height)
        surface.blit(text_surface,text_rect)
    def adjustBarHealth(self,var):
        self.health += var
    def adjustBarShieldTimes(self,var):
        self.shieldTimes += var
    def getBarHealth(self):
        return self.health
    def getBarShieldTimes(self):
        return self.shieldTimes
class MyMedkit(GameObject):
    def __init__(self,x,y,src,accelerationGravity,obstacleList):
        GameObject.__init__(self,x,y,src,accelerationGravity,obstacleList)
        self.timer = 300
    def updateGameObject(self,surface):
        if(self.rect.y >= surface.get_rect().height or self.timer <= 0):
            self.removeGameObject()
        else:
            self.timer -= 1
class MyShield(GameObject):
    def __init__(self,x,y,src,accelerationGravity,obstacleList):
        GameObject.__init__(self,x,y,src,accelerationGravity,obstacleList)
        self.timer = 300
    def updateGameObject(self,surface):
        if(self.rect.y >= surface.get_rect().height or self.timer <= 0):
            self.removeGameObject()
        else :
            self.timer -= 1

class MySprShield(GameObject):
    def __init__(self,x,y,src,player,weaponList):
        GameObject.__init__(self,x,y,src)
        self.player = player
        self.weaponList= weaponList
        self.waitingMySprShield = 100
        self.countWaiting = 0
        self.setEnabledDraw(False)
    def updateGameObject(self,surface):
        keys = pygame.key.get_pressed()
        if(keys[K_DOWN] and self.player.playerBar.getBarShieldTimes() > 0 and (not self.isEnabledDraw()) and self.countWaiting == 0):
            self.player.playerBar.adjustBarShieldTimes(-1)
            self.setEnabledDraw(True)
        else:
            if(self.waitingMySprShield >= self.countWaiting and self.isEnabledDraw()):
                self.countWaiting += 1
            else:
                if(not keys[K_DOWN]):
                    self.countWaiting = 0
                self.setEnabledDraw(False)
        if(self.isEnabledDraw()):
            Player_x = self.player.rect.center[0]
            Player_y = self.player.rect.center[1]
            self.rect.x = Player_x - (self.rect.width/2)
            self.rect.y = Player_y - (self.rect.height/2)
            if(self.weaponList.isCrashOn(self)):
                touchedObject = self.weaponList.getGameObject().getGameObjectName()
                if(touchedObject == "Sword"):
                        self.setEnabledDraw(False)
                        self.weaponList.getGameObject().removeGameObject()
class MyLader(GameObject):
    def __init__(self,x,y,src):
        GameObject.__init__(self,x,y,src)
    def isCrashOn(self,object,vector = None,variation = None):
        Top = self.rect.top
        Left = self.rect.left
        Right = self.rect.right
        Bottom = self.rect.bottom
        if(vector == None and variation == None):
            return (self.rect.colliderect(object))
        else:
            Top = self.rect.top
            Left = self.rect.left
            Right = self.rect.right
            Bottom = self.rect.bottom
            if(vector == "UP"):
                return (object.rect.bottom > Top and object.rect.bottom + variation - Top  > 0)
            elif(vector == "DOWN"):
                return (object.rect.bottom < Bottom and object.rect.bottom + variation - Bottom < 0)
class MyGround(GameObject):
    def __init__(self,x,y,src):
        GameObject.__init__(self,x,y,src)
    def isCrashOn(self,object,vector,variation):
        Top = self.rect.top
        Left = self.rect.left
        Right = self.rect.right
        Bottom = self.rect.bottom
        if(vector == "DOWN"):
            if((object.rect.bottom <= Top and object.rect.bottom + variation - Top > -1) and object.rect.right >= Left and object.rect.left <= Right):
                return True
            return False
        elif(vector == "RIGHT"):
            if((object.rect.right  <= Left and object.rect.right + variation - Left > -1)  and object.rect.bottom >= Top and object.rect.top <= Bottom):
                return True
            return False
        elif(vector == "LEFT"):
            if((object.rect.left >= Right and object.rect.left - variation -Right < 1)  and object.rect.bottom >= Top and object.rect.top <= Bottom):
                return True
            return False

class Sword(GameObject):
    def __init__(self,x,y,src):
        GameObject.__init__(self,x,y,src,0.3)
    def updateGameObject(self,surface):
        if(self.rect.y >= surface.get_rect().height):
            self.setSpeedGravity(0)
            self.rect.y = -50
            if(random.randint(0,1440)!=0):
                self.removeGameObject()
class Sea(GameObject):
    def __init__(self,x,y,src):
        GameObject.__init__(self,x,y,src,0)

    
class Player(GravityObject,AnimationObject):
    def __init__(self,src,x,y,playerBar,obstacleList,weaponList,prposList):
        HitBox = pygame.Rect(x,y,34,47)
        self.playerBar = playerBar
        self.obstacleList = obstacleList
        self.weaponList = weaponList
        self.prposList = prposList
        GravityObject.__init__(self,HitBox,0.87,self.obstacleList)
        AnimationObject.__init__(self,10,HitBox)
        self.appendAnimationFolder(src)
        self.speedWalk = 3
        self.isAlive = True
        self.effectList = None
    def setEffectList(self,effectList):
        self.effectList = effectList
    def updateActivate(self):
        keys = pygame.key.get_pressed()
        if(keys[K_SPACE] or keys[K_UP]):
            if(not self.isFalling):
                self.setSpeedGravity(-10)
        if(not((keys[K_LEFT] or keys[K_a]) ^ (keys[K_RIGHT] or keys[K_d]))):
            self.enableAnimation(False)
            self.setAnimationState("Stay")
        elif (keys[K_LEFT] or keys[K_a]):
            if(not self.obstacleList.isCrashOn(self,"LEFT",self.speedWalk)):
                if(self.rect.x <= 0):
                    self.rect.x = 0
                else:
                    self.rect.x -= self.speedWalk
            else:
                self.rect.x = self.obstacleList.getGameObject().rect.right
            self.enableAnimation(True)
            self.setAnimationState("Left")
        elif (keys[K_RIGHT] or keys[K_d]):
            if(not self.obstacleList.isCrashOn(self,"RIGHT",self.speedWalk)):
                if(self.rect.x+self.rect.width >= 1440):
                    self.rect.x = 1440 - self.rect.width
                else:
                    self.rect.x += self.speedWalk
            else:
                self.rect.x = self.obstacleList.getGameObject().rect.left-self.rect.width
            self.enableAnimation(True)
            self.setAnimationState("Right")
        if(self.prposList.isCrashOn(self)):
            touchedObject = self.prposList.getGameObject()
            objectName = touchedObject.getGameObjectName()
            if(objectName == "Lader"):
                if(keys[K_w] and keys[K_s]):
                    self.setSpeedGravity(0)
                elif(keys[K_w]):
                    self.setSpeedGravity(0)
                    if(touchedObject.isCrashOn(self,"UP",-5)):
                        self.rect.y -= 5
                    else:
                        self.rect.y = touchedObject.rect.top - self.rect.height + 1
                elif(keys[K_s]):
                    self.setSpeedGravity(0)
                    if(touchedObject.isCrashOn(self,"DOWN",5)):
                        self.rect.y += 5
                    else:
                        self.rect.y = touchedObject.rect.bottom - self.rect.height -1
    def updatePrpos(self):
        if(self.prposList.isCrashOn(self,mask=["Lader"])):
            touchedObject = self.prposList.getGameObject()
            objectName = touchedObject.getGameObjectName()
            if(objectName == "Shield"):
                self.playerBar.adjustBarShieldTimes(1)
                touchedObject.removeGameObject()
            elif(objectName == "Medkit"):
                if(self.playerBar.getBarHealth()<3):
                    self.playerBar.adjustBarHealth(1)
                touchedObject.removeGameObject()
        pass
    def updateDamage(self):
        if(self.weaponList.isCrashOn(self)):
            touchedObject = self.weaponList.getGameObject()
            objectName = touchedObject.getGameObjectName()
            if(objectName == "Sword"):
                touchedObject.removeGameObject()
                self.playerBar.adjustBarHealth(-1)
            elif(objectName == "Sea"):
                self.playerBar.adjustBarHealth(-10)
            if(self.playerBar.getBarHealth() <= 0):
                self.isAlive = False
    def drawEffect(self,surface):
        if(self.effectList != None):
            self.effectList.drawGameObject(surface)

    def drawPlayer(self,surface):
        self.updateActivate()
        self.updateGravity()
        self.drawAnimation(surface)
        self.drawEffect(surface)
        self.updatePrpos()
        self.updateDamage()
        self.playerBar.drawBar(surface)
        #self.drawHitbow(surface,(255,128,255))

    def alive(self):
        return self.isAlive
    
class Camera():
    def __init__(self,player,map,camera,background,playerBar):
        self.player = player
        self.map = map
        self.background = background
        self.cameraSize = camera.get_rect()
        self.playerBar = playerBar
    def drawCamera(self):
        if(self.player.rect.x+(self.player.rect.width/2)-(self.cameraSize.width/2) <= 0):
            clip_rect_x = 0
        elif(self.player.rect.x+(self.player.rect.width/2)+(self.cameraSize.width/2)>= self.map.get_rect().width):
            clip_rect_x = self.map.get_rect().width - self.cameraSize.width
        else:
            clip_rect_x = self.player.rect.x+(self.player.rect.width/2)-(self.cameraSize.width/2)
        if(self.player.rect.y+(self.player.rect.height/2)-(self.cameraSize.height*0.65) <= 0):
            clip_rect_y = 0
        elif(self.player.rect.y+(self.player.rect.height/2)+(self.cameraSize.height*(1-0.65))>= self.map.get_rect().height):
            clip_rect_y = self.map.get_rect().height - self.cameraSize.height
        else:
            clip_rect_y = self.player.rect.y+(self.player.rect.height/2)-(self.cameraSize.height*0.65)
        self.clip_rect = pygame.Rect(clip_rect_x,clip_rect_y,self.cameraSize.width,self.cameraSize.height)
        self.playerBar.setxy(clip_rect_x+10,clip_rect_y+10)
        self.map.blit(background.subsurface(self.clip_rect),self.clip_rect)
    def getCameraSurface(self):
        clip_image = self.map.subsurface(self.clip_rect)
        return clip_image

def init_Obstacle(folder):
    file_names = os.listdir(folder)
    obstacle = GameObjectList()
    for file_name in file_names:
        locate = file_name.split("_")
        locate[1]=locate[1].split(".png")[0]
        obstacle.appendGameObject(MyGround(int(locate[0]),int(locate[1]),(folder+"/"+file_name)))
    return obstacle


# 初始化pygame
pygame.init()
# 設置視窗的寬度和高度
width = 1440
height = 720

scale_factor = 1.6  # 放大两倍

# 计算放大后的尺寸
new_width = 300 * scale_factor
new_height = 450 * scale_factor

# 缩放 Surface



# 創建視窗
screen = pygame.display.set_mode((new_width,new_height ))
background = pygame.image.load("./image/background.png")
Map = pygame.Surface((width, height))
Camera1 = pygame.Surface((300, 450))
# 加載圖片

# 设置目标帧率
clock = pygame.time.Clock()
target_fps = 60

# 設置視窗標題
pygame.display.set_caption("Final Profect")



MapObstacle = init_Obstacle("./image/Obstacle")

MyWeaponList = GameObjectList()
MyWeaponList .appendGameObject(Sword(random.randint(40,680),10,"./image/Weapon/Sword.png"))
MyWeaponList .appendGameObject(Sea(0,656,"./image/Weapon/Sea.png"))

MyPrposList = GameObjectList()

MyPrposList.appendGameObject(MyLader(569,242,"./image/Props/Lader_569_242.png"))
MyPrposList.appendGameObject(MyLader(1019,242,"./image/Props/Lader_1019_242.png"))

PlayerBar = MyBar("./image/Bar",280,2)

p1 = Player("./image/Player",400,100,PlayerBar,MapObstacle,MyWeaponList,MyPrposList)

MyEffectList = GameObjectList()
MyEffectList.appendGameObject(MySprShield(1019,0,"./image/Props/SprShield.png",p1,MyWeaponList))

p1.setEffectList(MyEffectList)

c1 = Camera(p1,Map,Camera1,background,PlayerBar)

# 遊戲主迴圈
running = True
count = 0
while(p1.alive()and running):
    # 事件處理迴圈
    for event in pygame.event.get():
        # 檢查是否為退出事件
        if event.type == pygame.QUIT:
            running = False
    # 更新遊戲狀態
    Map.fill((255, 255, 255))
    c1.drawCamera()
    #Map.blit(background, (0,0))
    MapObstacle.drawGameObject(Map)
    MyWeaponList.drawGameObject(Map)
    MyPrposList.drawGameObject(Map)
    p1.drawPlayer(Map)
    if(count == 100):
        MyPrposList.appendGameObject(MyShield(random.randint(10,1440) ,10,"./image/Props/Shield.png",0.5,MapObstacle))
        MyPrposList.appendGameObject(MyMedkit(random.randint(10,1440) ,10,"./image/Props/Medkit.png",0.5,MapObstacle))
        count = 0
    else:
        count += 1
    if(count%10==0):
        MyWeaponList.appendGameObject(Sword(random.randint(10,1440) ,10,"./image/Weapon/Sword.png"))
    # 更新視窗
    #screen.blit(Map,(0,0))
    scaled_surface = pygame.transform.scale(c1.getCameraSurface(), (new_width, new_height))
    screen.blit(scaled_surface,(0,0))
    pygame.display.flip()
    clock.tick(target_fps)
# 退出遊戲
while (running):
    for event in pygame.event.get():
        # 檢查是否為退出事件
        if event.type == pygame.QUIT:
            running = False
pygame.quit()