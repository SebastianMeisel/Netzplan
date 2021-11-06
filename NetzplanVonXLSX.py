#!/usr/bin/env python3
from netzplan import Projekt, Netzplan


P = Projekt(1, "BeispielProjekt")
P.ImportiereVonExcel("Projekt.xlsx")

Netzplan = Netzplan(P.Bezeichnung)
Netzplan.Zeichnen(P)
Netzplan.PdfExport()
Netzplan.JPGExport()
P.ZeigeKritischenPfad()

