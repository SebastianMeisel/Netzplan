#!/usr/bin/env python3
from netzplan import Projekt, Netzplan


P = Projekt(1, "BeispielProjekt")
P.ImportiereArbeitsPacketListeVonCSV("Projekt.csv")
P.ImportiereRessourcenVonCSV("Ressourcen.csv")


Netzplan = Netzplan(P.Bezeichnung)
Netzplan.Zeichnen(P)
Netzplan.PdfExport()
Netzplan.JPGExport()
P.ZeigeKritischenPfad()

