#!/usr/bin/env python3
from netzplan import Projekt, Netzplan

###################################################################
# Beispiel

P1 = Projekt(1, "Beispiel") 

# Arbeits-Packete: Bezeichnung, Aufwand, ID (optional)
P1.NeuesArbeitsPacket("Anfangen", 5, '1.1.1'),
P1.NeuesArbeitsPacket("Weitermachen", 7, '1.1.2')
P1.NeuesArbeitsPacket("Einkaufen", 1, '1.1.3')
P1.NeuesArbeitsPacket("Ganz anders weitermachen", 4, '1.2.2')
P1.NeuesArbeitsPacket("Aufhören", 7, '1.2.3')
P1.NeuesArbeitsPacket("Anders weitermachen", 5, '1.2.1')
P1.NeuesArbeitsPacket("Pause", 8, '1.3.1')
P1.NeuesArbeitsPacket("Erholung", 6, '1.3.2')
P1.NeuesArbeitsPacket("Feiern", 6, '1.3.3')

# Abhängigkeiten 
P1.ArbeitsPackete["1.1.2"].Folgt("1.1.1")
P1.ArbeitsPackete["1.1.3"].Folgt("1.1.2")
P1.ArbeitsPackete["1.2.1"].Folgt("1.1.1")
P1.ArbeitsPackete["1.2.2"].Folgt("1.2.1")
P1.ArbeitsPackete["1.2.3"].Folgt("1.2.2")
P1.ArbeitsPackete["1.3.1"].Folgt("1.2.1")
P1.ArbeitsPackete["1.3.2"].Folgt("1.3.1")
P1.ArbeitsPackete["1.3.3"].Folgt(["1.1.3","1.2.3","1.3.2"]) # Mehrere Arbeitspackete in einer Liste
                                                                                                                      # (in eckigen Klammern) zusammenfassen
################################################################################
# Ressourcen: Name
P1.NeueRessource("FM" , "Frank Müller")
P1.NeueRessource("PL", "Pipi Langstrumpf")


# Hr. Meier:  Ressource, Arbeitspacket, Kapazität (Default 100%)
P1.RessourceZuweisen("FM", "1.1.1")
P1.RessourceZuweisen("FM", "1.1.2", 50)
P1.RessourceZuweisen("FM", "1.2.1", 50)
P1.RessourceZuweisen("FM", "1.2.3")
P1.RessourceZuweisen("FM", "1.1.3")
P1.RessourceZuweisen("FM", "1.3.2")
P1.RessourceZuweisen("FM", "1.3.3")

# Pipi: Ressource, Arbeitspacket, Kapazität (Default 100%)
P1.RessourceZuweisen("PL", "1.1.1")
P1.RessourceZuweisen("PL", "1.1.3")
P1.RessourceZuweisen("PL", "1.2.1")
P1.RessourceZuweisen("PL", "1.2.2", 50)
P1.RessourceZuweisen("PL", "1.3.1", 50)
P1.RessourceZuweisen("PL", "1.3.2")
P1.RessourceZuweisen("PL", "1.3.3")


# Netzplan: Name der PDF
N1 = Netzplan("Netzplan2")
N1.Zeichnen(P1)
N1.PdfExport()
N1.JPGExport()
print(N1.Name+" fertig!") # Nur dass wir wissen, dass es gelaufen ist. 
