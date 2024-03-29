import os
os.system("pip install pyodbc")
import sqlite3
import time
import shutil
import os.path
import datetime
import pyodbc
import uuid
import random

class Day():
    def __init__(self,currentday):
        self.currentday = currentday
        self.totalcustomers = 0
    def OperateDay(self,Store,Terminal):
        if Terminal.day == "Random":
            self.totalcustomers = round((30 + ((30 * self.currentday)-(15 * self.currentday)))*(Store.rating/5000))
            for x in range(1,self.totalcustomers):
                customertypeweighting = random.randint(0,100)
                customerbudget = 0
                customertype = None
                if customertypeweighting <= 50:
                    customertype = "Essentials"
                    customerbudget = random.randint(10,125)
                elif customertypeweighting > 50 and customertypeweighting <= 75:
                    customertype = "Luxury"
                    customerbudget = random.randint(15,150)
                elif customertypeweighting > 75 and customertypeweighting <= 85:
                    customertype = "Clothes"
                    customerbudget = random.randint(110,350)
                elif customertypeweighting > 85 and customertypeweighting <= 95:
                    customertype = "Electronic"
                    customerbudget = random.randint(150,500)
                elif customertypeweighting > 95:
                    customertype = "Furniture"
                    customerbudget = random.randint(150,425)
                Customer = str(uuid.uuid4())
                Store.cursor.execute('INSERT INTO Customer (CustomerID, CustomerTypeID, Budget) VALUES (?, ?, ?)', (Customer, customertype, customerbudget))
                #--
                AvailableItems = Store.cursor.execute('SELECT ItemID,CostToObtain FROM StockItems WHERE ItemTypeID = (?)', (customertype))
                AvailableItemsList = []
                for row in AvailableItems:
                    list.append(AvailableItemsList,list(row))
                #--
                AmountOfItemsToBuy = 0
                if customerbudget >= 1 and customerbudget < 25:
                    AmountOfItemsToBuy = random.randint(1,11)
                elif customerbudget >= 25 and customerbudget < 40:
                    AmountOfItemsToBuy = random.randint(3,17)
                elif customerbudget >= 40 and customerbudget < 80:
                    AmountOfItemsToBuy = random.randint(5,21)
                elif customerbudget >= 80 and customerbudget < 100:
                    AmountOfItemsToBuy = random.randint(8,28)
                elif customerbudget >= 100 and customerbudget < 150:
                    AmountOfItemsToBuy = random.randint(10,38)
                elif customerbudget >= 150:
                    AmountOfItemsToBuy = random.randint(1,3)
                #--
                AmountBought = 0
                TotalCost = 0
                for z in range(1,AmountOfItemsToBuy):
                    inde = random.randint(0,len(AvailableItemsList)-1)
                    ItemBeingBought = AvailableItemsList[inde][0]
                    ItemCost = float(AvailableItemsList[inde][1]) * (1 + Store.pmargin/100)
                    #--
                    ItemQuery = Store.cursor.execute('SELECT StockID,Amount FROM StoreStock WHERE ItemID = (?)', (ItemBeingBought))
                    QueryResult = []
                    for row in ItemQuery:
                        list.append(QueryResult,list(row))
                    #--
                    if (TotalCost + ItemCost <= customerbudget) and QueryResult[0][1] > 0:
                        TotalCost = TotalCost + ItemCost
                        AmountBought = AmountBought + 1
                        Store.moneyreserve = round(float(Store.moneyreserve) + float(ItemCost))
                        Store.cursor.execute('UPDATE StoreStock SET Amount = (?) WHERE StockID = (?)', (QueryResult[0][1] - 1, QueryResult[0][0]))
                        Store.cursor.execute('INSERT INTO Purchase (StockID, CustomerID, Profit, DayID) VALUES (?, ?, ?, ?)', (QueryResult[0][0], Customer, ItemCost, self.currentday))
                        Store.rating = Store.rating + 1
                        #--
                        if Terminal.purchases == "Realtime":
                            print(ItemBeingBought,"bought for £"+str(ItemCost))
                    else:
                        Store.rating = Store.rating - 3
                    if AmountBought == AmountOfItemsToBuy:
                        Store.rating = Store.rating + 3
                        if Terminal.purchases == "Realtime":
                            print("Customer unable to buy",str(ItemBeingBought)+"!")
                if Terminal.purchases == "Realtime":
                    print("------")
                    print(TotalCost)
                    print(AmountBought)
                    print("------")
                    time.sleep(0.5)



class Store():
    def __init__(self):
        shutil.copy2("StockManagement.accdb","inuse")
        self.moneyreserve = 0
        self.rating = 0 #Out of 5000
        self.budget = 0
        self.pmargin = 0 #Percent out of 100
        self.operatingfee = 0
        #--
        self.conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=inuse\StockManagement.accdb;')
        self.cursor = self.conn.cursor()
    def InvalidEntry(self):
        print("Not a valid entry option!")
        time.sleep(1)
    def checkVariable(self,variable,min,max,type):
        if type == "int" and variable.isdigit():
            if int(variable) >= min and int(variable) <= max:
                return True
            else:
                return False
        else:
            return False
    def StoreMain(self,Terminal,currentday):
        playingGame = True
        currentday = currentday
        while playingGame == True:
            if currentday < 1:
                if Terminal.day == "Random":
                    self.moneyreserve = 1000
                    self.rating = 4000
                    self.budget = 750
                    self.pmargin = 20
                    self.operatingfee = 500
                    currentday = currentday + 1
                    self.cursor.execute('INSERT INTO Days (DayID) VALUES ('+str(currentday)+')')
                    #--
                    print("The game is now starting!")
                    time.sleep(1)
            else:
                Interim = True
                while Interim == True:
                    self.conn.commit()
                    os.system("cls")
                    #--
                    print("""
CURRENT DAY: *DAY """+str(currentday)+"""*
------------------------------------
MONEY RESERVE: £"""+str(self.moneyreserve)+"""
STORE RATING: """+str(self.rating/1000)+"""★
SET BUDGET: £"""+str(self.budget)+"""
PROFIT MARGIN: """+str(self.pmargin)+"""%
OPERATING COSTS: £"""+str(self.operatingfee)+""" - Must be paid daily
-----------------------------------
Bankruptcy or a complete loss of the store's reputation ends in a total failure
                    """)
                    #--
                    Option = input("What action would you like to take? (START/RESTOCK/PRINTSTOCK/CHANGE/FINISHGAME): ")
                    if Option.upper() == "START":
                        Interim = False
                        newDay = Day(currentday)
                        newDay.OperateDay(self,Terminal)
                    elif Option.upper() == "FINISHGAME":
                        Interim = False
                        playingGame = False
                    elif Option.upper() == "RESTOCK":
                        if Terminal.stock == "Auto":
                            AllItems = self.cursor.execute('SELECT StockID, Amount, MaxCapacity, CostToObtain FROM StoreStock,StockItems')
                            QueryResult = []
                            BudgetSpent = 0
                            for row in AllItems:
                                list.append(QueryResult,list(row))
                            for Item in QueryResult:
                                if BudgetSpent < self.budget:
                                    if Item[1] < Item[2] * 0.75:
                                        Difference = Item[2] - Item[1]
                                        if (Difference * Item[3] < self.budget + (self.budget * 0.1)) and (self.moneyreserve - (Difference * Item[3]) > 0):
                                            MoneySpent = Difference
                                            self.cursor.execute('UPDATE StoreStock SET Amount = (?) WHERE StockID = (?)', (Item[1] + Difference,Item[0]))
                                            BudgetSpent = BudgetSpent + MoneySpent
                                            self.moneyreserve = round(self.moneyreserve - MoneySpent)
                                        else:
                                            while (self.moneyreserve > Item[3]) and (BudgetSpent < self.budget + (self.budget + (self.budget * 0.1))) and (Item[1] < Item[2] * 0.75):
                                                MoneySpent = Item[3]
                                                self.cursor.execute('UPDATE StoreStock SET Amount = (?) WHERE StockID = (?)', (Item[1] + 1,Item[0]))
                                                BudgetSpent = BudgetSpent + MoneySpent
                                                self.moneyreserve = round(self.moneyreserve - MoneySpent)
                    elif Option.upper() == "PRINTSTOCK":
                        print("hi, ran out of time to program this :C")
                    elif Option.upper() == "CHANGE":
                        ChangingSetting = input("What setting would you like to change? (BUDGET/PROFITMARGIN): ")
                        if (ChangingSetting.upper() == "BUDGET") or (ChangingSetting.upper() == "PROFITMARGIN"):
                            VariableAccepted = False
                            while VariableAccepted == False:
                                ChangingVariable = input("What would you liked the setting to be changed to?: ")
                                if ChangingSetting.upper() == "BUDGET":
                                    if self.checkVariable(ChangingVariable,0,100000000000,"int") == True:
                                        VariableAccepted = True
                                        self.budget = int(ChangingVariable)
                                    else:
                                        self.InvalidEntry()
                                elif ChangingSetting.upper() == "PROFITMARGIN":
                                    if self.checkVariable(ChangingVariable,1,100,"int") == True:
                                        VariableAccepted = True
                                        self.pmargin = int(ChangingVariable)
                                    else:
                                        self.InvalidEntry()
                                else:
                                    self.InvalidEntry()
                #--
                self.moneyreserve = self.moneyreserve - self.operatingfee
                if self.moneyreserve <= 0 or self.rating <= 0:
                    Interim = False
                    playingGame = False
                    print("SIMULATION FAILED")
                    time.sleep(5)
                    break
                elif self.rating > 5000:
                    self.rating = 5000
                #-
                currentday = currentday + 1
                self.cursor.execute('INSERT INTO Days (DayID) VALUES ('+str(currentday)+')')

class Terminal:
    def __init__(self,stock,purchases,day):
        self.stock = stock
        self.purchases = purchases
        self.day = day
        self.NewStore = None
    def InvalidEntry(self):
        print("Not a valid entry option!")
        time.sleep(1)
    def StartProgram(self):
        StartedGame = False
        #--
        print("""
           Welcome!

            This is a stock management training tool being 
            developed for major supermarket brands across the UK. 
            This tool uses a command-line interface in order to interact
            with the tool. The basic layout of your interactions will follow
            the layout of:
            '[Question] ([Available command prompts])'
            Only available command prompts given to you for that specific
            question will work.
            
            Press ENTER to begin.
        """)
        input()
        #--
        while StartedGame == False:
            os.system("cls")
            Option = input("What action would you like to take? (START/END/PRINT/CHANGE): ")
            if Option.upper() == "START":
                StartedGame = True
                self.NewStore = Store()
                self.NewStore.StoreMain(self,0)
                StartedGame = False
            elif Option.upper() == "END":
                if os.path.exists("inuse\\StockManagement.accdb"):
                    self.NewStore.cursor.close()
                    self.NewStore.conn.close()
                    #--
                    now = str(datetime.datetime.now())[:19]
                    now = now.replace(":","_")
                    shutil.copy2("inuse\\StockManagement.accdb","gamearchive\\StockManagement"+now+".accdb")
                    #--
                    os.remove("inuse\\StockManagement.accdb")
                    print("Game archive has been saved [directory]/gamearchive")
                exit()
            elif Option.upper() == "PRINT":
                print("ran out of time to program this :C")
            elif Option.upper() == "CHANGE":
                ChangingSetting = input("What setting would you like to change? (STOCK/PURCHASES/DAYOPTIONS): ")
                if ChangingSetting.upper() == "STOCK":
                    ChangingVariable = input("What would you liked the setting to be changed to? (AUTO/MANUAL): ")
                    if ChangingVariable.upper() == "AUTO" or ChangingVariable.upper() == "MANUAL":
                        self.stock = ChangingVariable.capitalize()
                        print(ChangingSetting.capitalize(),"setting now changed to",str(self.stock))
                        time.sleep(1)
                    else:
                        self.InvalidEntry()
                elif ChangingSetting.upper() == "PURCHASES":
                    ChangingVariable = input("What would you liked the setting to be changed to? (REALTIME/SUMMARY): ")
                    if ChangingVariable.upper() == "REALTIME" or ChangingVariable.upper() == "SUMMARY":
                        self.purchases = ChangingVariable.capitalize()
                        print(ChangingSetting.capitalize(),"setting now changed to",str(self.purchases))
                        time.sleep(1)
                    else:
                        self.InvalidEntry()
                elif ChangingSetting.upper() == "DAYOPTIONS":
                    ChangingVariable = input("What would you liked the setting to be changed to? (RANDOM/FILE): ")
                    if ChangingVariable.upper() == "RANDOM" or ChangingVariable.upper() == "FILE":
                        self.day = ChangingVariable.capitalize()
                        print(ChangingSetting.capitalize(),"setting now changed to",str(self.day))
                        time.sleep(1)
                    else:
                        self.InvalidEntry()  
                else:
                    self.InvalidEntry()
            else:
                self.InvalidEntry()

Game = Terminal("Auto","Summary","Random")
Game.StartProgram()
