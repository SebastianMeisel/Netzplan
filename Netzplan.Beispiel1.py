#!/usr/bin/env python3
from netzplan import Projekt, Netzplan

###################################################################
# Beispiel

P1 = Projekt(1, "Beispiel") 

# Arbeits-Packete: Bezeichnung, Dauer, ID (optional)
AP = {
    "1.1.1": P1.NeuesArbeitsPacket("Anfangen", 5, '1.1.1'),
    "1.2.1": P1.NeuesArbeitsPacket("Anders weitermachen", 5, '1.2.1'),
    "1.2.2": P1.NeuesArbeitsPacket("Ganz anders weitermachen", 4, '1.2.2'),
    "1.3.1": P1.NeuesArbeitsPacket("Pause", 8, '1.3.1'),
    "1.2.3": P1.NeuesArbeitsPacket("Aufhören", 7, '1.2.3'),
    "1.1.2": P1.NeuesArbeitsPacket("Weitermachen", 7, '1.1.2'),
    "1.1.3": P1.NeuesArbeitsPacket("Feiern", 6, '1.1.3'),
}
# Abhängigkeiten 
AP["1.1.2"].Folgt(AP["1.1.1"])
AP["1.2.1"].Folgt(AP["1.1.1"])
AP["1.2.2"].Folgt(AP["1.2.1"])
AP["1.3.1"].Folgt(AP["1.2.1"])
AP["1.2.3"].Folgt(AP["1.2.2"])
AP["1.1.3"].Folgt([AP["1.1.2"],AP["1.2.3"], AP["1.3.1"]]) # Mehrere Arbeitspackete in einer Liste
                            # (in eckigen Klammern) zusammenfassen
################################################################################
# Ressourcen: Name
R1 = P1.NeueRessource("Frank Müller")
R2 = P1.NeueRessource("Pipi Langstrumpf")

# Hr. Meier: Arbeitspacket, Kapazität (Default 100%)
R1.NeuesArbeitsPacket(AP["1.1.1"])
R1.NeuesArbeitsPacket(AP["1.1.2"],50)
R1.NeuesArbeitsPacket(AP["1.2.1"],50)
R1.NeuesArbeitsPacket(AP["1.2.3"]) 
R1.NeuesArbeitsPacket(AP["1.1.3"])

# Pipi: Arbeitspacket, Kapazität (Default 100%)
R2.NeuesArbeitsPacket(AP["1.1.1"])
R2.NeuesArbeitsPacket(AP["1.2.1"])
R2.NeuesArbeitsPacket(AP["1.2.2"], 50)
R2.NeuesArbeitsPacket(AP["1.3.1"], 50)
R2.NeuesArbeitsPacket(AP["1.1.3"])

# Netzplan: Name der PDF
N1 = Netzplan("Netzplan2")
N1.Zeichnen(P1)
N1.PdfExport()
print(N1.Name+" fertig!") # Nur dass wir wissen, dass es gelaufen ist. 
