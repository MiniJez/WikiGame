from bs4 import BeautifulSoup
import urllib.request
from PyQt5 import QtCore, QtGui, QtWidgets
from Qt_start_page import QtStartPage
from Qt_main_page import QtMainPage
from Qt_end_page import QtEndPage
import sys
from functools import partial

WIKIPEDIA_BASE_LINK = "https://fr.wikipedia.org"
WIKIPEDIA_RANDOM_LINK = "/wiki/Sp%C3%A9cial:Page_au_hasard"

class wikiPage:
    def __init__(self, link=WIKIPEDIA_RANDOM_LINK):
        self.title = None
        self.pageUrl = None
        self.wikiPage = None
        self.directLinks = []
        self.getWikiPages(link)
        self.getAllPageLinks()

    def getWikiPages(self, link=WIKIPEDIA_RANDOM_LINK):
        page = urllib.request.urlopen(WIKIPEDIA_BASE_LINK + link)
        self.pageUrl = page.url
        self.wikiPage = BeautifulSoup(page.read(), features="html.parser")
        self.title = self.wikiPage.select("#firstHeading")[0].contents[0]
        try:
            last = ""
            for string in self.title.strings:
                last = repr(string)
            self.title = last
        except:
            pass

    def getAllPageLinks(self):
        for div in self.wikiPage.find_all(True, {'class':['infobox_v3', 'infobox_v2', 'mw-editsection', 'navbox', 'navbox-container', 'external', 'bandeau-article', 'mw-selflink']}):
            div.decompose()
        for div in self.wikiPage.find_all(True, {"id": ["toc", 'bandeau-portail']}):
            div.decompose()
        for span in self.wikiPage.find_all("span"):
            span.decompose()

        links = self.wikiPage.select("#mw-content-text")[0].find_all("a")

        for a in links:
            try:
                if(len(a) > 0 and hasattr(a, 'href') and len(a.contents[0]) > 0 and a.getText() != "" and a.contents[0] == '[Quoi ?]' or not '/wiki/' in a['href'] or 'Fichier:' in a['href'] or 'Aide:' in a['href'] or 'Projet:' in a['href'] or 'Module:' in a['href'] or 'Mod%C3%A8le:%C3%89bauche' in a['href'] or "Wikip%C3%A9dia:Articles_de_qualit%C3%A9" in a['href']):
                    a.decompose()
                else:
                    try:
                        last = ""
                        for string in a.strings:
                            last = repr(string)
                        self.directLinks.append([last[1:-1], a['href']])
                    except:
                        self.directLinks.append([a.contents[0], a['href']])
            except KeyError:
                print(a)


class Game:
    def __init__(self):
        self.endGame = False
        self.tour = 0
        self.allWikiPages = []
        self.wikiPageStart = None
        self.wikiPageEnd = None

    def gameLoop(self):
        self.printLinks(len(self.allWikiPages[-1].directLinks) if len(self.allWikiPages[-1].directLinks) < 10 else 10)

    def updatePath(self, choix):
        self.tour += 1
        ui2.label_5.setText("Chargement ...")
        self.clearWidgetLayout()
        self.allWikiPages.append(wikiPage(self.allWikiPages[-1].directLinks[choix - 1][1]))
        self.printLinks(len(self.allWikiPages[-1].directLinks) if len(self.allWikiPages[-1].directLinks) < 10 else 10)
        ui2.label_3.setText("Tour numéro : " + str(self.tour))
        ui2.label_4.setText("Acutellement : " + self.allWikiPages[-1].title)
        ui2.label_5.setText("")

        if self.allWikiPages[-1].pageUrl == self.wikiPageEnd.pageUrl:
            self.endGamePrint()

    def returnBehind(self):
        ui2.label_5.setText("Chargement ...")
        self.clearWidgetLayout()
        self.allWikiPages.pop(-1)
        self.printLinks(len(self.allWikiPages[-1].directLinks) if len(self.allWikiPages[-1].directLinks) < 10 else 10)
        ui2.label_4.setText("Actuellement : " + self.allWikiPages[-1].title)
        ui2.label_5.setText("")

    def printAllLinks(self):
        self.clearWidgetLayout()
        self.printLinks(len(self.allWikiPages[-1].directLinks))

    def clearWidgetLayout(self):
        for i in reversed(range(ui2.vbox.count())):
            ui2.vbox.itemAt(i).widget().setParent(None)

    def printLinks(self, linksRange):
        if len(self.allWikiPages) > 1:
            item = QtWidgets.QPushButton("REVENIR EN ARRIERE")
            item.clicked.connect(self.returnBehind)
            item.setStyleSheet("background-color: white")
            ui2.vbox.addWidget(item)

        for i in range(linksRange):
            item = QtWidgets.QPushButton(self.allWikiPages[-1].directLinks[i][0])
            item.setStyleSheet("background-color: white")
            item.clicked.connect(partial(self.updatePath, i))
            ui2.vbox.addWidget(item)

        if linksRange == 10:
            item = QtWidgets.QPushButton("AFFICHER TOUS LES LIENS")
            item.clicked.connect(self.printAllLinks)
            item.setStyleSheet("background-color: white")
            ui2.vbox.addWidget(item)

    def initGame(self):
        mainWindow.show()
        self.wikiPageStart =  wikiPage()
        self.wikiPageEnd = wikiPage()
        self.allWikiPages.append(self.wikiPageStart)
        ui2.label_3.setText(ui2.label_3.text() + str(self.tour))
        ui2.label.setText(ui2.label.text() + self.wikiPageStart.title)
        ui2.label_2.setText(ui2.label_2.text() + self.wikiPageEnd.title)
        ui2.label_4.setText(ui2.label_4.text() + self.allWikiPages[-1].title)
        ui2.label_5.setText("")
        self.printLinks(len(self.allWikiPages[-1].directLinks) if len(self.allWikiPages[-1].directLinks) < 10 else 10)

    def endGamePrint(self):
        mainWindow.hide()
        endWindow.show()
        string = "C'est gagner ! \nNombres de coups : " + str(self.tour) + "\n\nChemin suivi :\n"
        for page in self.allWikiPages:
            string += page.title + "\n"
        ui3.label_2.setText(string)


app = QtWidgets.QApplication(sys.argv)
firstWindow = QtWidgets.QMainWindow()
mainWindow = QtWidgets.QMainWindow()
endWindow = QtWidgets.QMainWindow()
ui1 = QtStartPage()
ui1.setupUi(firstWindow)
ui2 = QtMainPage()
ui2.setupUi(mainWindow)
ui3 = QtEndPage()
ui3.setupUi(endWindow)

game = Game()
ui1.pushButton.clicked.connect(game.initGame)
firstWindow.show()

app.exec_()