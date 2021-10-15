from PIL import Image, ImageDraw, ImageFont # Netzplan zeichnen und exportieren

# Netzplan berechnen und zeichnen
version = 0.1

###############################################################
# Arbeitspacket-Objekt
class ArbeitsPacket(object):  

    # Konstruktor #############################################
    def __init__(self, ID, Bezeichnung: str, PT: int):
        self.ID = ID 
        self.Bezeichnung = Bezeichnung
        self.PT = PT # Personentage
        ###############################
        self.Dauer = self.PT
        self.FAZ = 0 # Früheste Anfangszeit
        self.FEZ = self.Dauer # Früheste Endzeit
        self.SAZ = 0 # Späteste Anfangszeit
        self.SEZ = 0 # Späteste Endzeit
        self.GP  = 0 # Gesamtpuffer
        self.FP  = 0 # Freier Puffer
        self.Nachfolger = [] # Liste der Nachfolger
        self.Vorgaenger = [] # Liste der Vorgänger
        self.Knoten     = None # Knoten im Netzplan
        self.Ressourcen = []

    # Vorgänger hinzufügen
    def Folgt(self, Vorgaenger: object or list):
        # Unterscheide ob einzelnes Arbeitspacket oder Liste
        if type(Vorgaenger) is list:
            self.Vorgaenger.extend(Vorgaenger) # Vorgänger-Liste hinzufügen
            for V in Vorgaenger:
                V.Nachfolger.append([self, 1]) # Zum Vorgänger als Nachfolger hinzufügen + Zähler für Nachfolger vorbereiten
        else:
            self.Vorgaenger.append(Vorgaenger) # Vorgänger hinzufügen
            Vorgaenger.Nachfolger.append([self, 1]) # Zum Vorgänger als Nachfolger hinzufügen

    # Früheste Anfangs- und Endzeit bestimmen    
    def getFXZ(self):
        # Früheste Anfangszeit
        if len(self.Vorgaenger) > 0:
            self.FAZ = max(AP.FEZ for AP in self.Vorgaenger)
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
    def __init__(self, Name:str):
        self.Name = Name
        #################
        self.ArbeitsPackete = {} # Arbeitspackete und Kapazität, die der Ressource zugeordnet werden

    def NeuesArbeitsPacket(self, AP: object, Kapazitaet=100):
        self.ArbeitsPackete[str(AP.ID)] = Kapazitaet
        AP.Ressourcen.append(self)
        
        
#######################################################################################
# Projekt-Objekt

class Projekt(object):

    # Konstruktor
    def __init__(self, ID: int, Bezeichnung: str):
        self.ID = ID
        self.Bezeichnung = Bezeichnung
        ##############
        self.ArbeitsPackete = []
        self.KritischerPfad = []
        self.AP_ID = 0 # Arbeitspacket-Identifier automatisch hochzählen
        self.Ressourcen = []
        
    # Arbeitspaket hinzufügen
    def NeuesArbeitsPacket(self, Bezeichnung: str, PT: int, ID=None) -> object:
        self.AP_ID += 1
        AP = ArbeitsPacket(ID if ID else self.AP_ID, Bezeichnung, PT)
        self.ArbeitsPackete.append(AP)
        return(AP)

    def NeueRessource(self, Name:str) -> object:
        R = Ressource(Name)
        self.Ressourcen.append(R)
        return(R)

    # Vorwärts- und rückwarts-rechnen
    def DurchRechnen(self):
        #Hilfsfunktionen
        def VorwaertsRechnen(AP: object) -> object:
            AP.getFXZ()
            for NF in AP.Nachfolger:
                VorwaertsRechnen(NF[0])
        def RueckwaertsRechnen(AP: object):
            AP.getSXZ()
            for VG in AP.Vorgaenger:
                # ???
                for i,NF in enumerate(VG.Nachfolger):
                    if type(NF[0]) is not tuple:
                        if NF[0].ID == AP.ID:   
                            VG.Nachfolger[i] = (AP, 1 if len(AP.Nachfolger) == 0 else max(t[-1] for t in AP.Nachfolger)+1) 
                # Wenn Vorgänger noch nicht berechnet ist dort weitermachen
                RueckwaertsRechnen(VG)

        # Kapazität je Arbeitspacket berechnen -> Dauer berechnen
        for AP in self.ArbeitsPackete:
            PersonenKapazitaet = 0  # Personen * Kapazität%
            # Personen-Kapazität berechnen
            for R in AP.Ressourcen:
                PersonenKapazitaet += R.ArbeitsPackete[str(AP.ID)] / 100
            # Wenn keine Resourchen zugeordnet sind, dann mit einer Person, 100% rechnen
            if PersonenKapazitaet == 0:
                PersonenKapazitaet = 1
            # Dauer = PersonenTage / PersonenKapazität
            AP.Dauer = int(AP.PT / PersonenKapazitaet) + (AP.PT % PersonenKapazitaet>0) # Aufrunden 
        # Vorwärts- und Rückwärtsrechnen
        AP = self.ArbeitsPackete[0]
        VorwaertsRechnen(AP)
        for ap in reversed(self.ArbeitsPackete):
            if len(ap.Nachfolger) == 0:
                AP = ap
                break
        RueckwaertsRechnen(AP)

    # Kritischen Pfad ausgeben    
    def ZeigeKritischenPfad(self):
        self.DurchRechnen()
        print("Kritischer Pfad: [ ", end="")
        for AP in reversed(self.KritischerPfad):
            print(AP.ID, end=" ")
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
        self.font = ImageFont.truetype("SourceCodePro-Light.ttf", 24)
        self.bold_font = ImageFont.truetype("SourceCodePro-Bold.ttf", 24)

        # Zeichnung um Netzplan aufzunehmen
        self.Zeichnung = ImageDraw.Draw(self.a4image)
        # Liste der Knoten
        self.IDs = 0 # Knoten-IDs
        self.Knoten = []

    # Knoten hinzufügen    
    def NeuerKnoten(self, x: int, y:int, AP: object):    
        self.IDs = AP.ID # ID des Knotens entspricht der, des dargestellten Knotens
        # Knoten-Objekt …
        K = Knoten(self.IDs, x, y, AP, self.Zeichnung) # … anlegen
        K.Zeichnen()                                   # … zeichnen
        self.Knoten.append(K.ID)                       # … (ID) in Knoten-Liste des Netzplans eintragen
        AP.Knoten = K                                  # … dem ArbeitsPacket zuordnen
        
    # Netzplan zeichnen    
    def Zeichnen(self, Projekt: object):
        x = .5
        y = .5
        Projekt.DurchRechnen()
        AP = Projekt.ArbeitsPackete[0]
        self.NeuerKnoten(x,y, AP) 
        # Hilfsfunktion
        def NachfolgerZeichnen(x: int, y: int, AP: object):
            x += 1
            for NF in reversed(sorted(AP.Nachfolger, key=lambda liste: liste[-1])) :
                if NF[0].ID not in self.Knoten:
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
        # Arbeitspacket-Liste
        y = self.y - y*AP.Knoten.dy - (30*(len(self.Knoten)+1))
        x = x*AP.Knoten.dx
        R = "Ressourcen" if len(Projekt.Ressourcen) > 0 else "" # Spalte Ressourcen nur, wenn Ressourcen geplant
        self.Zeichnung.text((x,y),"ID {A:<6}: {B:<25}: {C:^7}: {D:<40}".format(A="", B="Bezeichnung", C="Dauer", D=R), (0,0,0), font=self.bold_font)
        for AP in Projekt.ArbeitsPackete:
            y += 30
            # Ressourcen checken
            Ressourcen = ""
            i = 0 # zähle Ressourcen des Arbeitspackets
            for R in Projekt.Ressourcen:
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
        self.Zeichnung.text((xa+2,ya+1), "{a:^12}".format(a='AP '+str(self.AP.ID)) ,(0,0,0), font=self.font)
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

        
