from PIL import Image, ImageDraw, ImageFont # Netzplan zeichnen und exportieren
import csv                                # für CVS-Import
import re

# Netzplan berechnen und zeichnen
version = 0.1

###############################################################
# Arbeitspacket-Objekt
class ArbeitsPacket(object):  

    # Konstruktor #############################################
    def __init__(self, ID, Bezeichnung: str, PT: int, Projekt: object):
        self.ID = ID 
        self.Bezeichnung = Bezeichnung
        self.PT = PT # Personentage
        self.Projekt = Projekt # einem Projekt zuordnen
        ###############################
        self.Dauer = self.PT
        self.FAZ = 0 # Früheste Anfangszeit
        self.FEZ = self.Dauer # Früheste Endzeit
        self.SAZ = 0 # Späteste Anfangszeit
        self.SEZ = 0 # Späteste Endzeit
        self.GP  = 0 # Gesamtpuffer
        self.FP  = 0 # Freier Puffer
        self.Nachfolger = [] # Liste der Nachfolger
        self.Vorgänger = [] # Liste der Vorgänger
        self.Knoten     = None # Knoten im Netzplan
        self.Ressourcen = []

    # Vorgänger hinzufügen
    def Folgt(self, Vorgänger: str or list):
        # Unterscheide ob einzelnes Arbeitspacket oder Liste
        if type(Vorgänger) is list:
            for V in Vorgänger:
                self.Vorgänger.append(self.Projekt.ArbeitsPackete[V])
                self.Projekt.ArbeitsPackete[V].Nachfolger.append([self, 1]) # Zum Vorgänger als Nachfolger hinzufügen + Zähler für Nachfolger vorbereiten
        else:
            self.Vorgänger.append(self.Projekt.ArbeitsPackete[Vorgänger]) # Vorgänger hinzufügen
            self.Projekt.ArbeitsPackete[Vorgänger].Nachfolger.append([self, 1]) # Zum Vorgänger als Nachfolger hinzufügen

    # Früheste Anfangs- und Endzeit bestimmen    
    def getFXZ(self):
        # Früheste Anfangszeit
        if len(self.Vorgänger) > 0:
            self.FAZ = max(AP.FEZ for AP in self.Vorgänger)
        # Frühester Endzeitpunkt
        self.FEZ = self.Dauer + self.FAZ


    # Späteste Anfangs- und Endzeit und Puffer bestimmen    
    def getSXZ(self):
        # Späteste Endzeit
        if len(self.Nachfolger) > 0:
            self.SEZ = min(AP[0].SAZ for AP in self.Nachfolger)
        else: # Wenn kein Nachfolger nach früheste Endzeit übernehmen
            self.SEZ = self.FEZ

        # Späteste Anfangszeit
        self.SAZ = self.SEZ - self.Dauer

        # Gesamtpuffer
        self.GP = self.SEZ - self.FEZ

        # Freier Puffer
        if len(self.Nachfolger) > 0:
            self.FP = min(AP[0].FAZ for AP in self.Nachfolger) - self.FEZ


#######################################################################################
# Resource-Objekt

class Ressource(object):
    # Konstrukor
    def __init__(self, Name:str, Projekt:object):
        self.Name = Name
        self.Projekt = Projekt # Projekt zuordnen
        #################
        self.ArbeitsPackete = {} # Arbeitspackete und Kapazität, die der Ressource zugeordnet werden

    def NeuesArbeitsPacket(self, AP: str, Kapazität=100):
        self.ArbeitsPackete[self.Projekt.ArbeitsPackete[AP].ID] = Kapazität
        self.Projekt.ArbeitsPackete[AP].Ressourcen.append(self)
        
        
#######################################################################################
# Projekt-Objekt

class Projekt(object):

    # Konstruktor
    def __init__(self, ID: int, Bezeichnung: str):
        self.ID = ID
        self.Bezeichnung = Bezeichnung
        ##############
        self.ArbeitsPackete = {}
        self.KritischerPfad = []
        self.AP_ID = 0 # Arbeitspacket-Identifier automatisch hochzählen
        self.Ressourcen = {}
        
    # Arbeitspaket hinzufügen
    def NeuesArbeitsPacket(self, Bezeichnung: str, PT: int, ID=None):
        self.AP_ID += 1
        AP = ArbeitsPacket(ID if ID else self.AP_ID, Bezeichnung, PT, self)
        self.ArbeitsPackete[str(AP.ID)] = AP

    # Ressource hinzufügen
    def NeueRessource(self, ID:str, Name:str):
        R = Ressource(Name, self)
        self.Ressourcen[ID] = R 

    # Ressource zuweisen
    def RessourceZuweisen(self, RessourcenID: str, ArbeitsPacketID: str, Kapazität = 100):
        self.Ressourcen[RessourcenID].NeuesArbeitsPacket(ArbeitsPacketID, Kapazität)
        
    # Arbeispaketlist als CSV importieren
    def ImportiereArbeitsPacketListeVonCSV(self, Dateiname:str):
        with open(Dateiname, newline='') as csvfile:
            CSV = csv.DictReader(csvfile, delimiter=';', quotechar='"')
            for Zeile in CSV: 
                self.NeuesArbeitsPacket(Zeile["Beschreibung"], int(Zeile["Dauer"]), Zeile["ID"])
                Folgt = Zeile["Folgt"].split(",")
                if len(Folgt) == 1 and not Folgt[0] == '': 
                    self.ArbeitsPackete[Zeile["ID"]].Folgt(Zeile["Folgt"])
                elif Folgt[0] != '':
                    self.ArbeitsPackete[Zeile["ID"]].Folgt(Folgt)
    
    # Ressourcen als CSV importieren
    def ImportiereRessourcenVonCSV(self, Dateiname:str):
        with open(Dateiname, newline='') as csvfile:
            CSV = csv.DictReader(csvfile, delimiter=';', quotechar='"')
            for Zeile in CSV:
                R_ID=Zeile["ID"]
                Name="{VN} {NN}".format(VN=Zeile["Vorname"], NN=Zeile["Nachname"])
                self.NeueRessource(R_ID,Name)
                for AP in Zeile["Arbeitspackete"].split(','):
                    ID_K = AP.split(":", 1) # in ID und Kapazität aufspalten
                    AP_ID = ID_K[0]         # ID 
                    K = 100 if len(ID_K) == 1 else int(ID_K[1]) # Kapazität
                    self.RessourceZuweisen(R_ID,AP_ID,K)

    # Vorwärts- und rückwarts-rechnen
    def DurchRechnen(self):
        #Hilfsfunktionen
        def VorwärtsRechnen(AP: object) -> object:
            AP.getFXZ()
            for NF in AP.Nachfolger:
                VorwärtsRechnen(NF[0])
        def RückwärtsRechnen(AP: object):
            AP.getSXZ()
            if AP.GP == 0 and not AP.ID in self.KritischerPfad:
                self.KritischerPfad.append(AP.ID)
            for VG in AP.Vorgänger:
                for i,NF in enumerate(VG.Nachfolger):
                    if type(NF[0]) is not tuple:
                        if NF[0].ID == AP.ID:   
                            VG.Nachfolger[i] = (AP, 1 if len(AP.Nachfolger) == 0 else max(t[-1] for t in AP.Nachfolger)+1) 
                # Wenn Vorgänger noch nicht berechnet ist dort weitermachen
                RückwärtsRechnen(VG)

        # Kapazität je Arbeitspacket berechnen -> Dauer berechnen
        for AP in list(self.ArbeitsPackete.values()):
            PersonenKapazität = 0  # Personen * Kapazität%
            # Personen-Kapazität berechnen
            for R in AP.Ressourcen:
                PersonenKapazität += R.ArbeitsPackete[AP.ID] / 100
            # Wenn keine Resourchen zugeordnet sind, dann mit einer Person, 100% rechnen
            if PersonenKapazität == 0:
                PersonenKapazität = 1
            # Dauer = PersonenTage / PersonenKapazität
            AP.Dauer = int(AP.PT / PersonenKapazität) + (AP.PT % PersonenKapazität>0) # Aufrunden 
        # Vorwärts- und Rückwärtsrechnen
        AP = list(self.ArbeitsPackete.values())[0]
        VorwärtsRechnen(AP)
        for ap in reversed(list(self.ArbeitsPackete.values())):
            if len(ap.Nachfolger) == 0:
                AP = ap
                break
        RückwärtsRechnen(AP)

    # Kritischen Pfad ausgeben    
    def ZeigeKritischenPfad(self):
        self.DurchRechnen()
        print("Kritischer Pfad: [ ", end="")
        for i, AP_ID in enumerate(reversed(self.KritischerPfad)):
            print(AP_ID, end=" ")
            if i < len(self.KritischerPfad)-1:
                print(" - ", end="")
        print("]")

####################################################################       
# Netzplan-Object 
class Netzplan(object):

    # Kontruktor
    def __init__(self, Name: str):
        self.Name = Name # Name der Exportdatei
        # A4-Seite als Leinwand
        self.x = 3508                       # X-Länge der Leinwand        
        self.y = 2480                       # Y-Länge der Leinwand        
        self.a4image = Image.new('RGB',
                         (self.x, self.y),       # A4 bei 72dpi
                         (255, 255, 255))  # Weiß
        # Schriftart
        self.font = ImageFont.truetype("SourceCodePro-Light.ttf", 24, 0)
        self.bold_font = ImageFont.truetype("SourceCodePro-Bold.ttf", 24)
        self.heading_font = ImageFont.truetype("SourceCodePro-Bold.ttf", 36)

        # Zeichnung um Netzplan aufzunehmen
        self.Zeichnung = ImageDraw.Draw(self.a4image)
        # Listen: Knoten Raster
        self.Knoten = [] # Knoten auf der Zeichnung
        self.Raster = [] # Liste der Belegten Positionen im Raster um Überschneidungen zu vermeiden

    # Knoten hinzufügen    
    def NeuerKnoten(self, x: int, y:int, AP: object):    
        # Knoten-Objekt …
        K = Knoten(AP.ID, x, y, AP, self.Zeichnung)    # … anlegen
        K.Zeichnen()                                   # … zeichnen
        self.Knoten.append(K.ID)                       # … (ID) in Knoten-Liste des Netzplans eintragen
        self.Raster.append(str(x)+str(y))
        AP.Knoten = K                                  # … dem ArbeitsPacket zuordnen
        
    # Netzplan zeichnen    
    def Zeichnen(self, Projekt: object):
        x = .5
        y = .5        
        Projekt.DurchRechnen()
        AP = list(Projekt.ArbeitsPackete.values())[0]
        self.NeuerKnoten(x,y, AP) 
        # Hilfsfunktion
        def NachfolgerZeichnen(x: int, y: int, AP: object):
            x += 1
            # Wenn Rasterpunkt belegt, dann neue Zeile anfangen.
            for NF in reversed(sorted(AP.Nachfolger, key=lambda liste: liste[-1])) :
                if NF[0].ID not in self.Knoten:
                    y += 1
                    while str(x)+str(y) in self.Raster:
                        y += 1 
                    self.NeuerKnoten(x,y, NF[0])
                    # Nachfolger zeichnen
                    NachfolgerZeichnen(x,y-1, NF[0])
                # Verbinder Zeichnen
                fill = (255 if AP.GP == 0 and NF[0].GP == 0 else 0,0,0) # rot für kritischen Pfad
                width = (3 if AP.GP == 0 and NF[0].GP == 0 else 1) # fett für kritischen Pfad
                xa, ya = AP.Knoten.aus # Startpunkt des Verbinders
                xb,yb = NF[0].Knoten.ein  # Endpunkt des Verbinders
                ux = AP.Knoten.ux      # X-Größe eines Kästchens 
                uy = AP.Knoten.uy      # X-Größe eines Kästchens 
                ry = 0 if yb-ya == 0 else 1 if yb-ya > 0 else -1 # Hoch/runter/geradeaus
                rx = 1 if xb-xa >= 0 else 0 # Links/rechts
                xm = (xa+xb)/2         # Mitte (X-Achse) zwischen Start- und Endpunkt 
                self.Zeichnung.line((xa,ya, xa+ux+rx,
                                     ya+(ry*3*uy)-10*ry),
                                    fill=fill, width = width)
                self.Zeichnung.line((xa+ux+rx, ya+(ry*3*uy)-10*ry,
                                     xb-(rx*ux), ya+(ry*3*uy)-10*ry),
                                    fill=fill, width = width)
                self.Zeichnung.line((xb-(rx*ux), ya+(ry*3*uy)-10*ry,
                                     xb-ux, ya+(ry*6*uy)-10*ry),
                                    fill=fill, width = width)
                self.Zeichnung.line((xb-ux, ya+(ry*6*uy)-10*ry,
                                     xb-ux, yb-10*ry),
                                    fill=fill, width = width)
                self.Zeichnung.line((xb-ux, yb-10*ry,
                                     xb, yb-10*ry),
                                    fill=fill, width = width)

        NachfolgerZeichnen(x,y-1, AP)
        ##########################################
        # Legende
        L = Legende()
        self.NeuerKnoten(8.5,11.25, L)
        x = 10.5*AP.Knoten.dx - (30*12)
        y = 11.25 * AP.Knoten.dy - AP.Knoten.uy
        for Label, Erklärung in [
                ["ID", "Identifier"],
                ["D", "Dauer"],
                ["FAZ/FEZ", "Früheste Anfangs-, bzw. Endzeit"],
                ["SAZ/SEZ", "Späteste Anfangs-, bzw. Endzeit"],
                ["GP/FP", "Gesamt-, bzw. Freier Puffer"]
        ]:
            y += 30
            self.Zeichnung.text((x,y), "{Label:<10}: {Erklärung:<20}".format(Label=Label, Erklärung=Erklärung), (0,0,0), font=self.font)
        ##########################################
        # Arbeitspacket-Liste
        y = self.y - AP.Knoten.dy - (30*(len(self.Knoten)+1)) - 35 # Unterer Seitenrand - 30px pro Zeile - 35px für Projektname
        x = AP.Knoten.dx                                           # Auf X-Achse am ersten Knoten ausrichten 
        R = "Ressourcen" if len(Projekt.Ressourcen) > 0 else "" # Spalte Ressourcen nur, wenn Ressourcen geplant
        self.Zeichnung.text((x,y),"Projekt: {Name:<60}".format(Name=Projekt.Bezeichnung), (0,0,0), font=self.heading_font)
        y += 40
        self.Zeichnung.text((x,y),"ID {A:<6}: {B:<25}: {C:^7}: {D:<40}".format(A="", B="Bezeichnung", C="Dauer", D=R), (0,0,0), font=self.bold_font)
        for AP in list(Projekt.ArbeitsPackete.values()):
            y += 30
            # Ressourcen checken
            Ressourcen = ""
            i = 0 # zähle Ressourcen des Arbeitspackets
            for R in list(Projekt.Ressourcen.values()):
                if str(AP.ID) in R.ArbeitsPackete.keys():
                    i += 1
                    if i > 1:
                        Ressourcen += ', '
                    Ressourcen += R.Name
                    if R.ArbeitsPackete[str(AP.ID)] != 100:
                        Ressourcen += "("+str(R.ArbeitsPackete[str(AP.ID)])+"%)"
            self.Zeichnung.text((x,y),"AP {ID:<6}: {Bezeichnung:<25}: {Dauer:7}: {Ressourcen:<40} ".format(ID=AP.ID, Bezeichnung=AP.Bezeichnung, Dauer=AP.Dauer, Ressourcen=Ressourcen), (0,0,0), font=self.font)
                    
        
    # PDF-Export
    def PdfExport(self):
        ## als PDF speichern
        self.a4image.save(self.Name+'.pdf', 'PDF', dpi=(300,300))

    # JPG-Export
    def JPGExport(self):
        ## als JPG speichern
        self.a4image.save(self.Name+'.jpg', dpi=(300,300))

################################################################
# Pseudo-Object für Legende
class Legende(object):  
        ID = "ID" 
        Bezeichnung = "Bezeichnung"
        ###############################
        Dauer = "D"
        FAZ = "FAZ" # Früheste Anfangszeit
        FEZ = "FEZ" # Früheste Endzeit
        SAZ = "SAZ" # Späteste Anfangszeit
        SEZ = "SEZ" # Späteste Endzeit
        GP  = "GP" # Gesamtpuffer
        FP  = "FP" # Freier Puffer

        
#################################################################
# Knoten-Object
class Knoten(object):
    def __init__(self, ID: int, x: int, y: int, AP: object, Zeichnung: object):
        self.ID = ID # ID des Knotens
        self.x = x   # X im Knotenraster
        self.y = y   # Y im Knotenraster
        self.AP = AP # Arbeitspacket, das der Knoten darstellt
        self.Zeichnung = Zeichnung # Zeichnungs-Objekt, auf dem der Knoten dargestellt wird
        ##
        # Einheiten für das Zeichnen
        self.ux = 60 # Breite eines Kästchens 14px ~ 0,75cm
        self.uy = 30 # Höhe eines Kästchens 14px ~ 0,50cm
        self.dx = self.ux * 3 + self.ux * 2 # X-Raster: ~2.25cm/Knoten + ~1cm Abstand 
        self.dy = self.uy * 4 + self.uy * 2 # Y-Raster: ~2cm/Knoten + ~1cm Abstand
        # Eingang- / Ausgang für Verbinder
        self.ein = (self.x * self.dx, self.y * self.dy + 2*self.uy)
        self.aus = (self.x * self.dx + 3*self.ux, self.y * self.dy + 2*self.uy)
        # Schriftart
        self.font = ImageFont.truetype("SourceCodePro-Light.ttf", 24)
        self.bold_font = ImageFont.truetype("SourceCodePro-Bold.ttf", 24)
        
    # Knoten zeichnen
    def Zeichnen(self):
        # FAZ
        xa = self.dx* self.x
        ya = self.dy* self.y
        xb = xa + self.ux
        yb = ya + self.uy
        self.Zeichnung.rectangle((xa,ya,xb,yb), fill=(255,255,255), outline=(0,0,0,0))
        self.Zeichnung.text((xa+2,ya+1), "{a:^4}".format(a=str(self.AP.FAZ)) ,(0,0,0), font=self.font)
        # FEZ
        xa = xb + self.ux
        # ya = ya 
        xb = xa + self.ux
        # yb = ya + self.uy
        self.Zeichnung.rectangle((xa,ya,xb,yb), fill=(255,255,255), outline=(0,0,0,0))
        self.Zeichnung.text((xa+2,ya+1), "{a:^4}".format(a=str(self.AP.FEZ)) ,(0,0,0), font=self.font)
        # ID
        xa = self.dx* self.x
        ya = yb
        xb = xa + 3*self.ux
        yb = ya + self.uy
        self.Zeichnung.rectangle((xa,ya,xb,yb), fill=(255,255,255), outline=(0,0,0,0))
        self.Zeichnung.text((xa+2,ya+1), "{a:^12}".format(a=str(self.AP.ID)) ,(0,0,0), font=self.font)
        # Dauer
        xa = self.dx* self.x
        ya = yb
        xb = xa + self.ux
        yb = ya + self.uy
        self.Zeichnung.rectangle((xa,ya,xb,yb), fill=(255,255,255), outline=(0,0,0,0))
        self.Zeichnung.text((xa+2,ya+1), "{a:^4}".format(a=str(self.AP.Dauer)) ,(0,0,0), font=self.font)
        # GP
        xa = xa + self.ux
        # ya = ya
        xb = xa + self.ux
        # yb = ya + self.uy
        self.Zeichnung.rectangle((xa,ya,xb,yb), fill=(255,255,255), outline=(0,0,0,0))
        self.Zeichnung.text((xa+2,ya+1), "{a:^4}".format(a=str(self.AP.GP)) ,(255 if self.AP.GP == 0 else 0,0,0), font=self.bold_font)
        # FP
        xa = xa + self.ux
        # ya = ya
        xb = xa + self.ux
        # yb = ya + self.uy
        self.Zeichnung.rectangle((xa,ya,xb,yb), fill=(255,255,255), outline=(0,0,0,0))
        self.Zeichnung.text((xa+2,ya+1), "{a:^4}".format(a=str(self.AP.FP)) ,(0,0,0), font=self.font)
        # SAZ
        xa = self.dx* self.x
        ya = yb
        xb = xa + self.ux
        yb = ya + self.uy
        self.Zeichnung.rectangle((xa,ya,xb,yb), fill=(255,255,255), outline=(0,0,0,0))
        self.Zeichnung.text((xa+2,ya+1), "{a:^4}".format(a=str(self.AP.SAZ)) ,(0,0,0), font=self.font)
        # SEZ
        xa = xb + self.ux
        # ya = ya 
        xb = xa + self.ux
        # yb = ya + self.uy
        self.Zeichnung.rectangle((xa,ya,xb,yb), fill=(255,255,255), outline=(0,0,0,0))
        self.Zeichnung.text((xa+2,ya+1), "{a:^4}".format(a=str(self.AP.SEZ)) ,(0,0,0), font=self.font)

        
