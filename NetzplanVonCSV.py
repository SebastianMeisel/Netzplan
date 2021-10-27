#!/usr/bin/env python3
from netzplan import Projekt, Netzplan
import csv
import re

with open('Projekt.csv', newline='') as csvfile:
    CSV = csv.DictReader(csvfile, delimiter=';', quotechar='"')
    for i, Zeile in enumerate(CSV):
        if i < 1 :
            P = Projekt(1, Zeile["Projekt"])
        P.NeuesArbeitsPacket(Zeile["Beschreibung"], int(Zeile["Dauer"]), Zeile["ID"])
        Folgt = Zeile["Folgt"].split(",")
        if len(Folgt) == 1 and not Folgt[0] == '': 
            P.ArbeitsPackete[Zeile["ID"]].Folgt(Zeile["Folgt"])
        elif Folgt[0] != '':
            P.ArbeitsPackete[Zeile["ID"]].Folgt(Folgt)
with open('Ressourcen.csv', newline='') as csvfile:
    CSV = csv.DictReader(csvfile, delimiter=';', quotechar='"')
    for i, Zeile in enumerate(CSV):
        for AP in Zeile["Arbeitspackete"].split(','):
            ID_K = AP.split(":", 1) # in ID und Kapazität aufspalten
            AP_ID = ID_K[0]
            K = 100 if len(ID_K) == 1 else int(ID_K[1])
            print(AP_ID,Zeile["ID"], K, sep=":")
            P.NeueRessource(Zeile["ID"],Zeile["Vorname"]+" "+Zeile["Nachname"])
            P.RessourceZuweisen(Zeile["ID"],AP_ID,K)

Netzplan = Netzplan(Zeile["Projekt"])
Netzplan.Zeichnen(P)
Netzplan.PdfExport()
Netzplan.JPGExport()
P.ZeigeKritischenPfad()

