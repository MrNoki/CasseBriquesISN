
import tkinter
import tkinter.ttk
from threading import *
from math import *
import xml.etree.ElementTree as ET
import winsound
import time
import re
import os
import random

class Level():
    '''Initialisation du niveau
    @param l'objet qui appelle cette fonction,
    @param application,
    @param canvas,
    @param numéro de stage/niveau pour charger différent niveaux'''
    def __init__(self, app, boss):
        self.boss = boss
        self.app = app
        self.stage = 0
        self.levelsName= []
        self.briques =[]
        self.editBriques = []
        for i in range(420):
            self.editBriques.append(0)
        self.loadLevelList()
        self.fileName = self.levelsName[self.stage]

    def loadLevelList(self):
        tree = ET.parse("./Ressources/Niveaux/levelList")
        root = tree.getroot()
        
        for level in root.findall('level'):
            self.levelsName.append(level.get('Name'))
        for i in range(len(self.levelsName)-1):
            try:
                ET.parse("./Ressources/Niveaux/" + self.levelsName[i])
            except:
                del self.levelsName[i]
                
    '''Chargement du fichier niveau
    @param l'objet qui appelle cette fonction'''
    def loadFromFile(self):
        tree = ET.parse("./Ressources/Niveaux/" + str(self.fileName))
        root = tree.getroot()
        i = 0
        for tile in root.findall('Tile'):
            posX = tile.get('posX')
            posY = tile.get('posY')
            hardness = tile.get('hardness')#Difficulté à casser le bloc avec la balle, type : int. -1  pour indestructible
            color = tile.get('color')
  self.briques.append(Brique(self.app, self.boss, i, int(posX),    int(posY), int(hardness), color))
            i+=1
        self.stage +=1
        self.fileName = self.levelsName[self.stage]

    def openLevel(self, fileName):
        tree = ET.parse(fileName)
        self.fileName = fileName
        root = tree.getroot()
        i = 0
        for tile in root.findall('Tile'):
            posX = tile.get('posX')
            posY = tile.get('posY')
            hardness = tile.get('hardness')#Difficulté à casser le bloc avec la balle, type : int. -1  pour indestructible
            color = tile.get('color')
            self.editBriques[int(posX)+int(posY)*12] = Brique(self.app,self.boss, i, int(posX), int(posY), int(hardness), color)
            i+=1

    def saveLevel(self, fileName):
        self.briques = []
        self.briques = self.app.getListBriques()
        map = ET.Element('map')
        for brique in self.briques:
            if brique != 0:
                tile = ET.SubElement(map, 'Tile',{'posX':str(brique.x), 'posY':str(brique.y),'hardness':str(brique.health), 'color':brique.color})
        ET.ElementTree(map).write(str(fileName))
        self.fileName = fileName
##        list = ET.Element('levels')
##        self.levelsName.append(fileName)
##        for levels in self.levelsName:
##            level = ET.SubElement(list, 'level',{'Name':levels,})
##        ET.ElementTree(list).write("./Ressources/Niveaux/levelList")
        
    def clearLevel(self):
        self.briques = []

class Score():
    def __init__(self, app):
        self.app = app
        self.score = 0
        self.scores = []
        self.pseudos = []
        self.openHighScoreFile()

    def registerHighScore(self, pseudo):
        i =0
        highScores = ET.Element('Highscores')
        for highScore in self.scores:
            if self.score > highScore:
                self.scores.insert(i, self.score)
                self.pseudos.insert(i, pseudo)
                self.scores.pop()
                self.pseudos.pop()
                self.score = 0
                print(i)
            pseudos = self.pseudos[i]
            scores = str(self.scores[i])
            if self.scores[i] == 0:
                XMLScore = ET.SubElement(highScores, 'highscore',{'vide':'True'})
            else:
                print(pseudos + " " + scores)
                XMLScore = ET.SubElement(highScores, 'highscore',{'score':scores , 'pseudo':pseudos})
            i += 1
        ET.ElementTree(highScores).write("highScore")
        self.app.main.launchMenu()
            
    def openHighScoreFile(self):
        tree = ET.parse("highScore")
        root = tree.getroot()
        i = 0
        pseudo = ''
        score = 0
        for highScore in root.findall('highscore'):
            if highScore.get('vide') == 'True':
                pseudo = '---'
                score = 0
            else:
                pseudo = highScore.get('pseudo')
                if pseudo == "":
                    pseudo = "---"
                score = int(highScore.get('score'))

            self.scores.append(score)
            self.pseudos.append(pseudo)

    def checkIfScoreIsHighScore(self):
        for highScore in self.scores:
            if self.score > highScore:
                print(self.score)
                print(highScore)
                return True
        return False

    def clean(self):
        highScores = ET.Element('Highscores')
        for highScore in self.scores:
                XMLScore = ET.SubElement(highScores, 'highscore',{'vide':'True'})
        ET.ElementTree(highScores).write("highScore")
        for i in range(10):
            self.scores[i] = 0
            self.pseudos[i] = "---"
        self.app.main.activeFen.update()

class Barre():
    '''Initialisation de la barre
    @param l'objet qui appelle cette fonction,
    @param application,
    @param canvas,
    @param id,
    @param position en X,
    @param position en Y,
    @param couleur'''
    def __init__(self, canevas, x, y, color = 'white', width = 80, height= 10):
        self.canevas = canevas
        ##Couleur de la raquette
        self.color = color
        ##Largeur et longeur de la raquette
        self.width = width
        self.height = height
        ##Position de départ de la raquette
        self.posXdef = x
        self.posYdef = y
        ##Pos du coin supérieur gauche
        self.posX = x
        self.posY = y
        ##Boolean pour savoir si la barre bouge
        self.moving = False
        ##Dessin de la barre
        self.drawing = self.canevas.create_rectangle(x, y, x + self.width, y + self.height, fill = self.color)

    #def __del__(self):
       # self.canevas.delete(self.drawing)
        
    '''Fontion de déplacement Gauche de la barre
    @param l'objet qui appelle cette fonction,
    @param valeur de déplacement en X'''
    def deplacerGauche(self):
        self.posX = max(self.posX-1, 0)
        self.redraw()
        
    def deplacerDroite(self):
        self.posX = min (self.posX+1, 485-self.width)
        self.redraw()

    def redraw(self):
        self.canevas.coords(self.drawing, self.posX, self.posY, self.posX + self.width, self.posY + self.height) 
        
    def reset(self):
        self.posX = self.posXdef
        self.posY = self.posYdef
        self.moving = False
        self.redraw()
        
class Balle():
    '''Initialisation de la balle
    @param l'objet qui appelle cette fonction,
    @param application,
    @param canvas,
    @param id,
    @param position en X,
    @param position en Y,
    @param couleur'''
    def __init__(self, app, canevas, id, x, y, color, rayon = 10, vitesse = 10):
        self.canevas = canevas
        self.app = app
        #Id de la balle
        self.id = id
        ##Angle de la balle
        self.angle = 3*pi/2
        ##Rayon de la balle
        self.rayon = rayon
        ##Positions de départ de la balle (constantes)
        self.posXdef = int(x)
        self.posYdef = int(y)
        ##Positions actuelles de la balle
        self.posX = int(x)
        self.posY = int(y)
        ##Vitesse de la balle par défaut 4
        self.speed = vitesse
        self.vitesseMax = 3
        ##Constante d'acceleration incrémenter à la vitesse
        self.acceleration_brique = 0.001
        self.acceleration_level = 0.05
        ##Vélocité vecteur pour la trajectoire de la balle
        self.vx = int(cos(self.angle)*self.speed)
        self.vy = int(sin(self.angle)*self.speed)
        ##
        self.xMax = int(canevas.cget('width'))
        self.yMax = int(canevas.cget('height'))
        ##Couleur de la balle
        self.color = color
        ##Dessin de la balle
        self.drawing = self.canevas.create_oval(x-self.rayon, y - self.rayon,\
                    x+self.rayon, y+self.rayon, width=1, fill = self.color)
        ##Combo de rebond pour le calcul du score
        self.combo = 1
        ##Timer pour gérer les combo
        self.timeStart = time.clock()
        self.timeEnd = 0
        ##Boolean si la balle est en mouvement
        self.moving = False
        ##Boolean si la balle a touché a autre élément
        self.collide = False

    #def __del__(self):
        #self.canevas.delete(self.drawing)
    
    def deplacer(self):
        '''Déplacement de la balle
    @param l'objet qui appelle cette fonction'''
        global debugMode
        if self.moving:
            if self.timeEnd - self.timeStart >= 1:
                self.combo = 1
                self.timeStart = time.clock()

            self.posX +=self.vx
            self.posY +=self.vy
            
            self.redraw()
            
    
    def sound(self):
        '''Son de la balle
    @param l'objet qui appelle cette fonction'''
        if self.collide:
            winsound.PlaySound(None, winsound.SND_FILENAME)
            winsound.PlaySound('./Ressources/Sons/son ball.wav',winsound.SND_FILENAME)
    
    def redraw(self):
        '''Redessine la balle
    @param l'objet qui appelle cette fonction'''
        self.canevas.coords(self.drawing, self.posX-self.rayon, self.posY-self.rayon, self.posX+self.rayon, self.posY + self.rayon)
        
    def reset(self):
        '''Reset la position de la balle et redessine
    @param l'objet qui appelle cette fonction'''
        self.posX = self.posXdef
        self.posY = self.posYdef
        self.moving = False
        self.redraw()

class Brique():
    def __init__(self, app, canevas, id, x, y, health=1, color='blue', width = 40, height = 20):
        '''Initialisation de la brique
    @param l'objet qui appelle cette fonction,
    @param application,
    @param canvas,
    @param id,
    @param position en X,
    @param position en Y,
    @param difficultée à casser la brique(vie),
    @param couleur'''
        self.canevas = canevas
        self.app = app
        ##Id de la brique
        self.id = id
        ##Largeur et hauteur de la brique, par défaut 40, 20
        self.width = width
        self.height = height
        ##Position de la brique par rapport a un repère (40,20)
        self.x = x
        self.y = y
        ##Position de la brique en pixel
        self.posX = x * self.width
        self.posY = y* self.height
        ##Vie de la brique
        self.health = health
        ##Couleur de la brique
        self.color = color
        ##
        self.xMax = int(canevas.cget('width'))
        self.yMax = int(canevas.cget('height'))
        ##Dessin de la brique
        self.drawing = self.canevas.create_rectangle(x*40+5, y*20+5, x*40 +45, y*20 + 25, fill = color)
        ##Texture de la brique, par défaut None
        self.textureDamage = None
        self.texture = None
        ##Dans le mode éditeur on donne une texture pour afficher la vie de la brique a l'utilisateur
        if inEditMode:
            self.textureDamage = tkinter.PhotoImage(file = "./Ressources/Textures/"+str(self.health) + ".gif")
            self.texture = self.canevas.create_image(self.posX+30, self.posY+15, image = self.textureDamage)
      
    def updateTexture(self):
        if self.health > 0:
            self.textureDamage = tkinter.PhotoImage(file= "./Ressources/Textures/brique_"+ str(self.health) + ".gif")
            self.texture = self.canevas.create_image(self.posX+25, self.posY+15, image = self.textureDamage)
        else:
            self.destroy()

    def update(self):
        self.updateTexture()
        randPop = random.randint(0,10)            
    def destroy(self):
        ##Détruis la texture et le dessin du Canevas
        self.canevas.delete(self.app, self.drawing)
        self.canevas.delete(self.app, self.texture)
        if inGame == True:
            self.app.addBriqueDestroyed()

class Application():
    def __init__(self, width, height):
        '''Initialisation de la Fenêtre principale
    @param l'objet qui appelle cette fonction,
    @param largeur de la fenêtre Frame,self.width/2, height-75,
    @param hauteur de la fenêtre Frame'''  
        self.width = width
        self.height = height
        ##Fenêtre active
        self.main = Fenetre(self, width, height)
        ##Constantes pour le début du jeu.
        self.healthMax = 3
        self.health = self.healthMax
        self.stage = 0
        self.score = Score(self)
        self.briqueDestroyed = 0
        ##Flags (booleans de départ).
        self.launch = False
        self.pause = False
        self.pos_init = True
        self.sound = False
        self.loose = False
        self.win = False
        ##Thread pour le son.
        self.soundThread = Thread(None, self.soundLoop, None)
        ##Fonction qui met a jour les actions sur l'interface tkinter.
        self.main.main.update()
        
    def start(self):
        '''Démarre l'application en activant les flags, et thread.'''
        self.loose = False
        self.win = False
        self.pos_init = False
        if self.sound == False:
            self.soundThread.start()
            self.sound = True
            
        if self.launch == False:
            self.launch = True
            self.pause = False
            self.run()
            
        elif self.launch == True:
            self.launch = False
            self.pause = True

    def stop(self):
        '''Stoppe l'application et éteint les flags, et reset.'''
        self.launch = False
        self.pause = False
        self.pos_init = True
        self.reset()

    def pauseGame(self):
        '''Met le jeu en pause'''
        if not self.pos_init:
            if self.pause == False:
                self.pause = True
                self.launch = False
                
            elif self.pause == True:
                self.pause = False
                self.launch = True
                self.run()
        
    def prepareStage(self):
        '''Prépare l'application pour le jeu, et prépare le 1er niveau'''
        self.level = Level(self, self.main.activeFen.canevas)
        self.barre = Barre(self.main.activeFen.canevas, self.width/2-40, self.height-54, "grey")
        self.balle = Balle(self,self.main.activeFen.canevas, 1, self.width/2, self.height-65, "white")
        self.briques = self.level.briques
        self.level.loadFromFile()

    def run(self):
        '''Boucle principale'''
        if self.launch == True:
            self.balle.deplacer()
            self.testCollisions()
            self.checkWin()
            self.main.activeFen.update()
            self.main.main.after(10, self.run)
    
    def soundLoop(self):
        '''Boucle pour le son(Thread)'''
        while True:
            self.balle.sound()
            time.sleep(0.010)

    def gagne(self):
        '''Appelé lorsque qu'on gagne un niveau, réinitialise le niveau'''
        self.reset()
        try:
            ##charge le niveau suivant si possible.
            self.level.loadFromFile()
            self.briques = self.level.briques
            self.briqueDestroyed = 0
            self.stage+=1
        except:
            ##Si il y a une erreur et qu'on ne peut pas charger le prochain niveau, on affiche la fenetre de fin de jeu.
            self.main.activeFen.displayEndGame(True)##True = Gagné
            self.stop()
            self.win = True##Flag
        
    def perdu(self):
        '''Appelé lorsqu'on a perdu ses vies.'''
        self.main.activeFen.displayEndGame(False)##False = Perdu
        self.stop()
        self.loose = True##Flag

    def checkWin(self):
        '''Vérifie si on a cassé toutes les briques du niveau''' 
        if self.briqueDestroyed == len(self.briques):
            self.gagne()
        
    def addBriqueDestroyed(self):
        '''Appelé lorsque l'on détruit une brique.'''
        self.briqueDestroyed +=1

    def reset(self):
        '''Réinitialise le jeu, entre chaques niveau'''
        self.level.clearLevel()
        self.barre.reset()
        self.balle.reset()
        self.launch= False
        self.pos_init = True
        self.brique = []
    
    def press(self, event):
        '''Appelé a chaque fois que l'on appui sur le clavier, on effectue une action en fonction de la touche pressée'''
        key = event.keysym
        if key == 'Escape':
            self.main.main.quit()
        if inGame == True:
            if key == 'Return':
                if self.win == True:
                    self.win = False
                    self.health = self.healthMax
                    if self.score.checkIfScoreIsHighScore():
                        self.main.activeFen.displayHighScoreEntry()
                    else:
                        self.main.launchMenu()
                        
                elif self.loose == False:
                    self.pauseGame()
                else:
                    self.loose = False
                    self.health = self.healthMax
                    if self.score.checkIfScoreIsHighScore():
                        self.main.activeFen.displayHighScoreEntry()  
                    else:
                        self.main.launchMenu()
                                    
            if key == 'c':#c for Cheat...
                for brique in self.briques:
                    brique.destroy()
                self.briqueDestroyed = len(self.briques)
                
            if self.loose == False:
                if self.pause == False:
                    if key == 'Left':
                        for i in range(10):
                            self.barre.deplacerGauche()
                            self.barre.moving = True
                            if self.launch == False:
                                if debugMode == True:
                                    self.balle.angle = pi
                                else:
                                    self.balle.angle = 4*pi/3
                                self.balle.vx = int(cos(self.balle.angle)*self.balle.speed)
                                self.balle.vy = int(sin(self.balle.angle)*self.balle.speed)
                                self.balle.moving = True
                                self.start()      
                            
                    if key == 'Right':
                        for i in range(10):
                            self.barre.deplacerDroite()
                            self.barre.moving = True
                            if self.launch == False:
                                if debugMode ==True:
                                    self.balle.angle = 2*pi
                                else:
                                    self.balle.angle = 4*pi/3
                                self.balle.vx = -int(cos(self.balle.angle)*self.balle.speed)
                                self.balle.vy = int(sin(self.balle.angle)*self.balle.speed)
                                self.balle.moving = True
                                self.start()
                    if key == 'Up':
                        if debugMode ==True:
                            self.balle.angle = -pi/2
                            self.balle.vx = int(cos(self.balle.angle)*self.balle.speed)
                            self.balle.vy = int(sin(self.balle.angle)*self.balle.speed)
                            self.balle.moving = True
                            self.start()


    def release (self, event):
        '''Appelé lorsque l'on relache l'appui d'une touche'''
        key = event.keysym
        if key == 'Left':
            self.barre.moving = False
        if key == 'Right':
            self.barre.moving = False

    def testCollisions(self):
        '''On test toute les collisions de la balle, avec la barre, les bordures du canvas et les briques.'''
    ##Collisions bordures du Canvas
        #Colision Mur Gauche
        if self.balle.posX + self.balle.rayon >= self.width+5:
            if debugMode:
                print("collisionMurXMax")
            self.balle.vx = int(cos(self.balle.angle)*self.balle.speed)
            self.balle.speed += 0.05
            self.balle.collide = True
        #Collision Mur Bas
        if self.balle.posY + self.balle.rayon >= self.height+5:
            if debugMode:
                 print("collisionMurYMax")
            self.health -=1
            if self.health == 0:
                self.perdu()
            else:
                self.reset()
        #Collision Mur Haut
        if self.balle.posY - self.balle.rayon <= 0:
            if debugMode:
                print("collisionMurMinY")
            self.balle.vy = -int(sin(self.balle.angle)*self.balle.speed)
            self.balle.speed += 0.05
            self.balle.collide = True
        #Collision Mur Droite
        if self.balle.posX - self.balle.rayon <= 0:
            if debugMode:
                print("collisionMurMinX")
            self.balle.vx = -int(cos(self.balle.angle)*self.balle.speed)
            self.balle.speed += 0.05
            self.balle.collide = True
    ##Collision Barre
        if self.balle.posY + self.balle.rayon >= self.barre.posY and self.balle.posY - self.balle.rayon <= self.barre.posY and self.balle.posX+self.balle.rayon > self.barre.posX and self.balle.posX-self.balle.rayon < self.barre.posX + 80:
                        self.balle.vy = int(sin(self.balle.angle)*self.balle.speed)
                        self.balle.speed -= 0.05
                        self.balle.collide = True
                        if debugMode:
                            print("collisionBarreHaut")
    ##Collisions Briques
        for brique in self.briques:
            if brique.health > 0:
                #Collision Brique Bas
                if self.balle.collide == False and self.balle.posY - self.balle.rayon <= brique.posY + brique.height and self.balle.posY + self.balle.rayon >= brique.posY+ brique.height and self.balle.posX + self.balle.rayon > brique.posX and self.balle.posX-self.balle.rayon < brique.posX + brique.width:
                    brique.health -=1
                    brique.update()
                    self.score.score += 15*self.balle.combo
                    self.balle.combo+=1
                    self.balle.speed += 0.05
                    if debugMode:
                        print("collisionBriqueBas")
                        brique.printBriqueInfos()
                        self.balle.printBalleInfos()
                    self.balle.vy = -int(sin(self.balle.angle)*self.balle.speed)
                    self.balle.collide = True
                #Collision Brique Haut        
                elif self.balle.collide == False and self.balle.posY - self.balle.rayon  <= brique.posY and self.balle.posY + self.balle.rayon >= brique.posY and self.balle.posX + self.balle.rayon > brique.posX and self.balle.posX-self.balle.rayon < brique.posX + brique.width:
                    brique.health -= 1
                    brique.update()
                    self.score.score += 15*self.balle.combo
                    self.balle.combo+=1
                    self.balle.speed += 0.05
                    if debugMode:
                        print("collisionBriqueHaut")
                        brique.printBriqueInfos()
                        self.balle.printBalleInfos()
                    self.balle.vy = int(sin(self.balle.angle)*self.balle.speed)
                    self.balle.collide = True
                #Collision Brique Droite
                elif self.balle.collide == False and self.balle.posX- self.balle.rayon <= brique.posX + brique.width and self.balle.posX+ self.balle.rayon >= brique.posX + brique.width and self.balle.posY - self.balle.rayon < brique.posY + brique.height and self.balle.posY +self.balle.rayon > brique.posY:
                    brique.health -=1
                    brique.update()
                    self.score.score += 15*self.balle.combo
                    self.balle.combo+=1
                    self.balle.speed += 0.05
                    if debugMode:
                        print("collisionBriqueDroite")
                        brique.printBriqueInfos()
                        self.balle.printBalleInfos()
                    self.balle.vx = -int(cos(self.balle.angle)*self.balle.speed)
                    self.balle.collide = True
                #Collision Brique Gauche
                elif self.balle.collide == False and self.balle.posX + self.balle.rayon >= brique.posX and self.balle.posX - self.balle.rayon <= brique.posX and self.balle.posY- self.balle.rayon < brique.posY + brique.height and self.balle.posY +self.balle.rayon > brique.posY:                                         
                    brique.health -=1
                    brique.update()
                    self.score.score += 15*self.balle.combo
                    self.balle.combo+=1
                    self.balle.speed += 0.05
                    if debugMode:
                        print("collisionBriqueGauche")
                        brique.printBriqueInfos()
                        self.balle.printBalleInfos()
                    self.balle.vx = int(cos(self.balle.angle)*self.balle.speed)
                    self.balle.collide = True

        self.balle.collide = False
        self.timeEnd = time.clock()

    def setvie(self, vie):
        self.vie = vie
        
    def setLevel(self, level):
        points= self.score+ 100*self.vie +level*10
        self.level = level

    def getListBriques(self):
        return self.briques

class Fenetre :
    def __init__(self , app, width = 400 , height = 600):
        """Constructeur de l'interface"""
        ## Classe Application qui invoque la fenêtre
        self.app=app
        ## Instantiation de tkinter.
        self.main = tkinter.Tk()
        self.main.title("Casse Briques")
        ## Constantes pour la fenêtre.
        self.width = width
        self.height = height
        ## Fenêtre active par défaut menu.
        self.activeFen = menu(self, self.app, self.width, self.height)
        ## Binding des touches du clavier pour les associer a des actions.
        self.activeFen.canevas.bind_all('<KeyPress>', self.app.press)
        self.activeFen.canevas.bind_all('<KeyRelease>', self.app.release)
        
    def launchGame(self):
        '''Lance la fenêtre du Jeu.'''
        global inGame
        global inEditMode
        inEditMode = False
        inGame = True
        #Detruis la fenêtre active, et donc tous les objet tkinter associés
        self.activeFen.destroy()
        #Creer une nouvelle fenêtre a partir d'une class.
        self.activeFen = Game(self, self.app, self.width, self.height)
        self.app.prepareStage()
        
    def launchEditor(self):
        '''Lance la fenêtre de l'éditeur.'''
        global inGame
        global inEditMode
        inGame = False
        inEditMode = True
        #Detruis la fenêtre active, et donc tous les objet tkinter associés
        self.activeFen.destroy()
        #Creer une nouvelle fenêtre a partir d'une class.
        self.activeFen = EditMode(self, self.app, self.width, self.height)

    def launchMenu(self):
        '''Lance la fenêtre du Menu.'''
        global inGame
        global inEditMode
        inGame = False
        inEditMode = False
        #Detruis la fenêtre active, et donc tous les objet tkinter associés
        self.activeFen.destroy()
        #Creer une nouvelle fenêtre a partir d'une class.
        self.activeFen = menu(self, self.app, self.width, self.height)

    def launchHighScore(self):
        '''Lance la fenêtre des HighScores.'''
        global inGame
        global inEditMode
        inGame = False
        inEditMode = False
        #Detruis la fenêtre active, et donc tous les objet tkinter associés
        self.activeFen.destroy()
        #Creer une nouvelle fenêtre a partir d'une class.
        self.activeFen = HighScore(self, self.app, self.width, self.height)

    def launchAbout(self):
        '''Lance la fenêtre "a propos".'''
        global inGame
        global inEditMode
        inGame = False
        inEditMode = False
        #Detruis la fenêtre active, et donc tous les objet tkinter associés
        self.activeFen.destroy()
        #Creer une nouvelle fenêtre a partir d'une class.
        self.activeFen = About(self, self.app, self.width, self.height)

    def launchOptions(self):
        '''Lance la fenêtre des options.'''
        global inGame
        global inEditMode
        inGame = False
        inEditMode = False
        #Detruis la fenêtre active, et donc tous les objet tkinter associés
        self.activeFen.destroy()
        #Creer une nouvelle fenêtre a partir d'une class.
        self.activeFen = Options(self, self.app, self.width, self.height)

    def exit(self):
        '''Quitte le programme.'''
        self.main.quit()
        quit()
              
class menu(tkinter.Frame):
    def __init__(self, boss, app, width = 400, height = 600):
        '''Initialisation de la Fenêtre principale
        @param l'objet qui appelle cette fonction,
        @param le maitre de l'objet, 
        @param largeur de la fenêtre Frame,
        @param hauteur de la fenêtre Frame'''
        ## Instantiation de l'objet hérité.
        tkinter.Frame.__init__(self)
        self.app = app
        self.boss =boss
        ## Variable Constante
        self.width = width
        self.height = height
        ## Canevas
        self.canevas = tkinter.Canvas(self , bg = 'grey' , width = self.width , height = self.height)
        ## Bouttons
        self.playButton = tkinter.Button(self, text='Nouvelle Partie', command = self.boss.launchGame, background = "black", foreground = 'white', relief = tkinter.FLAT, overrelief = tkinter.FLAT, font = "Courrier 11 bold", activebackground = 'white', activeforeground = 'black')
        self.editButton = tkinter.Button(self, text = 'Editeur de niveau', command = self.boss.launchEditor, background = "black", foreground = 'white', relief = tkinter.FLAT, overrelief = tkinter.FLAT, font = "Courrier 11 bold", activebackground = 'white', activeforeground = 'black')
        self.highScoreButton = tkinter.Button(self, text='HighScores', command = self.boss.launchHighScore, background = "black", foreground = 'white', relief = tkinter.FLAT, overrelief = tkinter.FLAT, font = "Courrier 11 bold", activebackground = 'white', activeforeground = 'black')
        self.optionsButton = tkinter.Button(self, text='Commandes', command = self.boss.launchOptions, background = "black", foreground = 'white', relief = tkinter.FLAT, overrelief = tkinter.FLAT, font = "Courrier 11 bold", activebackground = 'white', activeforeground = 'black')
        self.aboutButton = tkinter.Button(self, text='A Propos', command = self.boss.launchAbout, background = "black", foreground = 'white', relief = tkinter.FLAT, overrelief = tkinter.FLAT, font = "Courrier 11 bold", activebackground = 'white', activeforeground = 'black')
        self.quitButton = tkinter.Button(self, text = 'Quitter', command = self.boss.exit, background = "black", foreground = 'white', relief = tkinter.FLAT, overrelief = tkinter.FLAT, font = "Courrier 11 bold", activebackground = 'white', activeforeground = 'black')
        ## Placement des widgets
        self.pack()
        self.canevas.grid(row = 1 , column = 1 , columnspan = 10, rowspan = 10)
        self.playButton.grid(row = 8, column = 7, padx =0, pady = 0, sticky = 'S')
        self.editButton.grid(row = 8, column = 8, padx = 30, pady = 0, sticky = 'S')
        self.highScoreButton.grid(row = 9, column = 7, padx=0, pady = 0)
        self.optionsButton.grid(row = 9, column = 8, padx = 0, pady = 0)
        #self.aboutButton.grid(row = 10, column = 7, padx = 0, pady = 0, sticky = 'W')
        self.quitButton.grid(row = 10, column = 8, padx = 0 , pady =  0, sticky = 'E')
        ## Texture pour le fond de l'écran menu.
        self.textureDamage = tkinter.PhotoImage(file = "./Ressources/Textures/ecrantitre.gif")
        self.texture = self.canevas.create_image(480/2, 700/2, image = self.textureDamage)

class HighScore(tkinter.Frame):
    def __init__(self, boss, app, width = 400, height = 600):
        '''Initialisation de la Fenêtre principale
        @param l'objet qui appelle cette fonction,
        @param largeur de la fenêtre Frame,
        @param hauteur de la fenêtre Frame'''
        ## Instantiation de l'objet hérité.
        tkinter.Frame.__init__(self, bg = "black")
        self.app = app
        self.boss = boss
        self.width = width
        self.height = height
        ## Instantiation du Canvas
        self.canevas = tkinter.Canvas(self, bg = 'black', width =self.width, height = self.height, relief = tkinter.FLAT)
        ## Instantiation des widgets
        self.labelHighscore = []
        self.labelPseudo = []
        self.backButton = tkinter.Button(self, text = 'Retour', command = self.boss.launchMenu, background = "black", foreground = 'white', relief = tkinter.FLAT, overrelief = tkinter.FLAT, font = "Courrier 11 bold", activebackground = 'white', activeforeground = 'black')
        #self.effacerButton = tkinter.Button(self, text = 'Effacer les meilleurs scores', command = self.app.score.clean(), background = "black", foreground = 'white', relief = tkinter.FLAT, overrelief = tkinter.FLAT, font = "Courrier 11 bold", activebackground = 'white', activeforeground = 'black')
        
        ## Positionnement des widgets dans la fenêtre
        self.pack()
        #self.canevas.grid(row= 1, column = 1)
        self.backButton.grid(row = 10, column = 2, sticky = tkinter.W)
        #self.effacerButton.grid(row = 1, column = 1, sticky = tkinter.S)
        self.labelPseudoScore = self.canevas.create_text(240, 20, text = ' Pseudo                 Score ', font = "Courrier 18 bold", fill = 'white')
        self.canevas.grid(row = 1, rowspan = 10, column =1, columnspan = 15)
        for i in range(10):
            self.labelPseudo.append(self.canevas.create_text(120, 100+55*i, anchor = 'center', justify ='center', text = str(self.app.score.pseudos[i]), font = "Courrier 18 bold" , fill ="white"))
            self.labelHighscore.append(self.canevas.create_text(360, 100+55*i, anchor = 'center', justify ='center', text = str(self.app.score.scores[i]), font = "Courrier 18 bold" , fill ="white"))
    
    def update(self):
        for i in range(10):
            self.canevas.delete(labelPseudo[i])
            self.canevas.delete(labelHighscore[i])
            self.labelPseudo = []
            self.labelHighScore = []
            self.labelPseudo.append(self.canevas.create_text(120, 100+55*i, anchor = 'center', justify ='center', text = str(self.app.score.pseudos[i]), font = "Courrier 18 bold" , fill ="white"))
            self.labelHighscore.append(self.canevas.create_text(360, 100+55*i, anchor = 'center', justify ='center', text = str(self.app.score.scores[i]), font = "Courrier 18 bold" , fill ="white"))

            
class About(tkinter.Frame):
    def __init__(self, boss, app, width = 400, height = 600):
        '''Initialisation de la Fenêtre principale
        @param objet qui appelle cette fonction,
        @param largeur de la fenêtre Frame,
        @param hauteur de la fenêtre Frame'''
        ## Instantiation de l'objet hérité.
        tkinter.Frame.__init__(self)
        self.app = app
        self.boss = boss
        self.width = width
        self.height = height
        ## Instantiation du Canvas
        self.canevas = tkinter.Canvas(self, bg = 'grey', width =self.width, height = self.height)
        ## Instantiation des widgets
        self.backButton = tkinter.Button(self, text = 'Retour', command = self.boss.launchMenu, background = "black", foreground = 'white', relief = tkinter.FLAT, overrelief = tkinter.FLAT, font = "Courrier 11 bold", activebackground = 'white', activeforeground = 'black')
        ## Positionnement des widgets dans la fenêtre
        self.pack()
        self.canevas.grid(row= 1, column = 1)
        self.backButton.grid(row = 1, column = 1)

class Options(tkinter.Frame):
    def __init__(self, boss, app, width = 400, height = 600):
        '''Initialisation de la Fenêtre principale
        @param l'objet qui appelle cette fonction,
        @param largeur de la fenêtre Frame,
        @param hauteur de la fenêtre Frame'''
        ## Instantiation de l'objet hérité.
        tkinter.Frame.__init__(self, bg = 'black')
        self.app = app
        self.boss = boss
        self.width = width
        self.height = height
        ## Instantiation des widgets
        self.backButton = tkinter.Button(self, text = 'Retour', command = self.boss.launchMenu, background = "black", foreground = 'white', relief = tkinter.FLAT, overrelief = tkinter.FLAT, font = "Courrier 11 bold", activebackground = 'white', activeforeground = 'black')
        ## Positionnement des widgets dans la fenêtre
        texte ="""
                                                            Commandes :
=========================================================================
                                    
                                    - Flèche gauche : Lance la balle à gauche
                                    
                                    - Flèche droite : Lance la balle à droite
                                    
                                    - Entrée/Return : Met le jeu en pause
                                    
                                    - Escape : Quitter"""
        commandTexte = tkinter.Text(self, font= 'Courrier 12',bg='black',fg='white')
        
        self.pack()
        commandTexte.grid(row=0, column = 1, rowspan =2)
        self.backButton.grid(row = 2, column = 1)
        
        commandTexte.insert(tkinter.END, texte)
        
class Game(tkinter.Frame):
    def __init__(self, boss, app, width = 400, height = 600):
        '''Initialisation de la Fenêtre principale
        @param l'objet qui appelle cette fonction,
        @param largeur de la fenêtre Frame,self.width/2, height-75,
        @param hauteur de la fenêtre Frame'''
        ## Instantiation de l'objet hérité.
        tkinter.Frame.__init__(self, bg = 'black')
        ## Initialisation des constantes
        self.app = app
        self.boss = boss
        self.width = width
        self.height = height
        self.health = self.app.health
        self.score = self.app.score.score
        self.lifeDraw = []
        ## Instantiation du Canvas
        self.canevas = tkinter.Canvas(self, width = self.width, height = self.height, bg = 'black', bd= 3, relief = tkinter.SUNKEN)
        self.screen = tkinter.Canvas(self, width = self.width, height = 25, bg = 'black', bd= 3, relief = tkinter.SUNKEN)
        ## Positionnement des widgets dans la fenêtre
        self.pack()
        self.canevas.grid(row = 0, column = 0)
        self.screen.grid(row = 1, column = 0)
        for i in range (self.app.health):
            self.lifeDraw.append(self.screen.create_oval(5+ 25*i, 5,  25+25*i, 25,  width=1, fill = 'white'))
            
        self.scoreText = self.screen.create_text(240, 15, text = self.app.score.score, font = "Courrier 15 bold", fill = 'white')
    
    def update(self):
        '''Met à jour l'affichage de l'écran.'''
        if not self.health == self.app.health: 
            for i in range (self.health):
                self.screen.delete(self.lifeDraw[i])
            self.lifeDraw = []
            for i in range (self.app.health):
                self.lifeDraw.append(self.screen.create_oval(5+ 25*i, 5,  25+25*i, 25,  width=1, fill = 'white'))
            self.health = self.app.health
        if not self.score == self.app.score.score:
            self.score = self.app.score.score
            self.screen.delete(self.scoreText)
            self.scoreText = self.screen.create_text(240, 15, text = self.app.score.score, font = "Courrier 15 bold", fill = 'white')

    def displayEndGame(self, boolean):
        '''Affiche l'écran de fin de jeu en fonction du boolean (True/False)(Gagné/Perdu).'''
        if boolean:
            self.text = self.canevas.create_text(240, 350, text = "You Win !!\n\nPress Enter.", font = "Courrier 15 bold", fill = 'white')
        else: 
            self.text = self.canevas.create_text(240, 350, text = "Game Over !\n\nPress Enter.", font = "Courrier 15 bold", fill = 'white')

    def displayHighScoreEntry(self):
        '''Affiche l'écran d'entrée de score.'''
        self.canevas.destroy()
        self.screen.destroy()
        self.canevas = tkinter.Canvas(self, width = self.width, height = self.height, bg = 'black', bd= 3, relief = tkinter.SUNKEN)
        self.entry = tkinter.Entry(self, bg = 'black', fg='white', font = 'Courrier 18 bold' )
        self.validate = tkinter.Button(self, text = 'Valider', command = lambda:self.app.score.registerHighScore(self.entry.get()), background = "black", foreground = 'white', relief = tkinter.FLAT, overrelief = tkinter.FLAT, font = "Courrier 11 bold", activebackground = 'white', activeforeground = 'black')

        self.canevas.create_text(240, 175, text = "Nouveau meilleur score !\n\nEntrez votre pseudo.", font = "Courrier 18 bold", fill ='white')

        self.canevas.grid(row=1, rowspan = 10, column = 1)
        self.entry.grid(row = 5, column =1)
        self.validate.grid(row = 9, column = 1, sticky = tkinter.S)
    
class EditMode(tkinter.Frame):
    def __init__(self, boss, app, width = 400, height = 600):
        '''Initialisation de la Fenêtre principale
        @param l'objet qui appelle cette fonction,
        @param largeur de la fenêtre Frame,
        @param hauteur de la fenêtre Frame'''
        ## Instantiation de l'objet hérité.
        tkinter.Frame.__init__(self)
        #Initialisation des constantes
        self.app = app
        self.boss = boss
        self.width = width
        self.height = height
        self.fileName = None
        ## Instantiation du Canvas
        self.canevas = tkinter.Canvas(self, width = self.width, height = self.height, bg = 'black', bd= 3, relief =tkinter.SUNKEN)
        ## Instanciation des objets
        self.level = Level(self, self.canevas)
        self.briques = []
        for i in range(420):
            self.briques.append(0)
        ## Instantiation des Widgets
            ##Bind les touches et les associes a des fonctions. 
        self.canevas.bind('<Key>', self.clavier)
        self.canevas.bind("<Button-1>", self.putBrique)
        self.canevas.bind("<Button-3>", self.deleteBrique)
            ##Tableau de valeurs pour les ComboBox
        self.colorValuesSelected = tkinter.StringVar()
        self.colorValues = ('red','blue','yellow','orange', 'pink', 'purple', 'green','dark grey', 'light green', 'light blue','dark red', 'white', 'grey', 'ivory', 'magenta', 'cyan', 'brown', 'dark blue')
        self.vieValuesSelected = tkinter.StringVar()
        self.vieValues = ('1','2','3','4')
            ##Label (chaine de caractères affichée a l'écran)
        self.labelColor = tkinter.Label(self, text='Couleur')
        self.labelVie = tkinter.Label(self, text='Vie')
        self.label = tkinter.Label(self, text='Caractéristiques de la brique : ')
        self.labelApercu = tkinter.Label(self, text='Aperçu : ')
            #ComboBox (Liste déroulante de tableaux de valeurs).
        self.dropdownboxColor = tkinter.ttk.Combobox(self, textvariable = self.colorValuesSelected, values = self.colorValues, state = 'readonly')
        self.dropdownboxVie = tkinter.ttk.Combobox(self, textvariable = self.vieValuesSelected, values = self.vieValues, state = 'readonly')
            #Boutton
        self.backButton = tkinter.Button(self, text = 'Retour', command = self.boss.launchMenu)
        ## Mise en place des menus
            ## Menu pricipal.
        self.mainmenu = tkinter.Menu(self.master)
        self.master.config(menu = self.mainmenu)
                ## Sous menu fichier.
        self.menuFichier = tkinter.Menu(self.mainmenu)
        self.menuFichier.add_command(label= "Nouveau", command = self.clear)
        self.menuFichier.add_command(label= "Ouvrir", command = self.ouvrir)
        self.menuFichier.add_command(label= "Enregistrer", command = self.enregistrer)
        self.menuFichier.add_command(label= "Quitter", command = self.onExit)
                ## Sous menu jouer.
        self.menuJouer = tkinter.Menu(self.mainmenu)
        self.menuJouer.add_command(label= "Essayer ce niveau", command = self.test)
        ## Ajoute l'onglet au menu.
        self.mainmenu.add_cascade(label="Fichier", menu =self.menuFichier)
        self.mainmenu.add_cascade(label="Jouer", menu = self.menuJouer)
        ## Mise en place des Widgets
        
        self.canevas.focus_set()
        self.master.title("Casse Briques-Edit Mode")
        
        self.colorValuesSelected.set(self.colorValues[0])
        self.vieValuesSelected.set(self.vieValues[0])       
        ## Positionnement des Widgets grâce a la méthode grid()
        self.pack()
        self.label.grid(row =0, column = 1, sticky = tkinter.S+tkinter.W)
        #self.labelApercu.grid(row = 3, column = 1, sticky =tkinter.S +tkinter.W)
        self.labelColor.grid(row =1, sticky =tkinter.E)
        self.labelVie.grid(row =2, sticky =tkinter.E)
        self.canevas.grid(row = 0, column =4, rowspan = 20)
        self.dropdownboxColor.grid(row = 1, column = 1, sticky = tkinter.E)
        self.dropdownboxVie.grid(row = 2, column = 1, sticky = tkinter.E)
        #self.backButton.grid(row = 19, column = 1, sticky = W)

    def ouvrir(self):
        '''Ouvre un fichier niveau existant'''
        for i in range (420):
            if self.briques[i] != 0:
                self.briques[i].destroy()
                self.briques[i] = 0
                
        self.fileName = tkinter.filedialog.askopenfilename(filetypes = [("Fichiers Niveaux","*.lvl")])
        self.level.openLevel(self.fileName)    
        self.briques = self.level.editBriques

    def clear(self):
        '''Nettoie la surface de dessin de niveau'''
        for i in range (420):
            if self.briques[i] != 0:
                self.briques[i].destroy()
                self.briques[i] = 0

    def test(self):
        ## ATTENTION NON FONCTIONNEL !!!
        '''Permet de jouer le niveau creer'''
        print("jouer")
        
        
    def enregistrer(self):
        '''Enregistre le niveau créer dans un nouveau fichier.lvl'''
        self.fileName = tkinter.filedialog.asksaveasfilename(filetypes = [("Fichiers Niveaux","*.lvl")])
        self.level.saveLevel(self.fileName)

    def onExit(self):
        '''Appeler lorsqu'on quitte l'éditeur via le menu "Quitter"'''
        self.master.quit()

    def clavier(self,event):
        '''Récupère les évenement clavier'''
        key = event.keysym
        
    def putBrique(self, event):
        '''Insère une brique dans la surface de dessin de niveau'''
        if self.briques[int(event.x/40)+int(event.y/20)*12] != 0:
            self.briques[int(event.x/40)+int(event.y/20)*12].destroy()

        self.briques[int(event.x/40)+int(event.y/20)*12] = Brique(self, self.canevas, 1, int(event.x/40), int(event.y/20), self.vieValuesSelected.get(), self.colorValuesSelected.get())

    def deleteBrique(self, event):
        '''Supprime une brique de la surface de dessin de niveau'''
        if self.briques[int(event.x/40)+int(event.y/20)*12] != 0:
            self.briques[int(event.x/40)+int(event.y/20)*12].destroy()
            self.briques[int(event.x/40)+int(event.y/20)*12] = 0
        
    def getListBriques(self):
        '''Récupère la liste des briques.'''
        return self.briques



		
if __name__ == '__main__':
    debugMode = False
    inEditMode = False
    inGame = False
    app = Application(480,700)
    app.main.activeFen.mainloop()






