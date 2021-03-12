import importlib
import json
import os
import os.path
import platform
import queue
import tkinter as tk
from importlib import reload
from os import path
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Treeview

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import ui
from selenium.webdriver.support.wait import WebDriverWait

import autobidder
import autobuyer
import helpers
import thread_runner
from autobidder import Autobidder
from autobuyer import Autobuyer
from helpers import *
from thread_runner import RunThread
import threading
import time

LARGE_FONT= ("Verdana", 12)
SMALL_FONT = ("Verdana", 8)
NORM_FONT = ("Helvetica", 10)
HEADER_FONT = ("Helvetica", 12, "bold")


class GUI(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self.container = tk.Frame(self)

        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.parentQueue = queue.Queue()

        # self.logins = Logins(self.container, self)
        self.playerfilters = PlayerFilters(self.container, self)
        self.table = Table(self.container, self)
        self.mainbuttons = MainButtons(self.container, self)
        self.displaylogs = DisplayLogs(self.container, self)
        # self.disclaimers = Disclaimers(self.container, self)

        # self.logins.grid(row=1, column=0, sticky="nsew", padx="10", pady="10")

        # TOP RIGHT Main UI
        # self.playerfilters.pack(side=LEFT, anchor = NW) #grid(row=0, column=1, sticky="nsew", padx="10", pady="10")
        self.playerfilters.grid(row=0, column=0, sticky="nsew", padx="5", pady="5")

        # MIDDLE RIGHT Player Input List Table
        # self.table.pack(side=LEFT, anchor = W) #grid(row=1, column=1, sticky="nsew", padx="10", pady="10")
        self.table.grid(row=1, column=0, sticky="nsew", padx="5", pady="5")

        # FULL RIGHT Autobidder / Buyer Stats
        # self.mainbuttons.pack(side=RIGHT, anchor=NE) #grid(row=0, column=0, sticky="nsew", padx="10", pady="10")
        self.mainbuttons.grid(row=0, column=1, rowspan=3, sticky="nsew", padx="5", pady="5")

        # BOTTOM RIGHT Logs
        # self.displaylogs.pack(side=LEFT, anchor=SW) #grid(row=1, column=2, sticky="nsew", padx="10", pady="10")
        self.displaylogs.grid(row=2, column=0, sticky="nsew", padx="5", pady="5")
        # self.disclaimers.grid(row=1, column=1, sticky="se", padx="5", pady="5")

        # Main queue and Autobidder
        


# Top right 
class PlayerFilters(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller
        self.playerlist = []

        app_title = tk.Label(self, text=' FIFA 21 Autobidder + Autobuyer ', font=HEADER_FONT)
        app_title.grid(row=1, column=0, columnspan=2, pady=15)

        futbinlink_label = tk.Label(self, text='Player Futbin URL: ', font=NORM_FONT)
        futbinlink_text = tk.StringVar()
        futbin_entry = tk.Entry(self, textvariable=futbinlink_text)

        futbinlink_label.grid(row=2, column=0)
        futbin_entry.grid(row=2, column=1)

        
        self.add_btn_futbin = tk.Button(self, text='Add Player', width=12, command=self.add_player_futbin)
        self.add_btn_futbin.grid(row=3, column=0, pady=10)

        self.remove_btn = tk.Button(self, text='Remove Player', width=12, command=self.remove_player)
        self.remove_btn.grid(row=3, column=1, pady=10)


        disclaimer2 = tk.StringVar()
        disclaimer_text2 = tk.Label(self, text='Futbin price will be used as truth in initial searches, after which logged market data collected via search will be analyzed and used as true price', font=SMALL_FONT, wraplength=400)
        disclaimer_text2.grid(row=4, column=0, columnspan=2)

        self.futbinlink_text = futbinlink_text

        loginLabel = tk.Label(self, text='Auto Login: ')
        botChoice = tk.Label(self, text='Bot Method: ')
        loginLabel.grid(row = 5, column = 0)
        botChoice.grid(row = 7, column = 0)

        self.autologin_choice = tk.IntVar()
        self.bot_choice = tk.IntVar()
        self.autologin_choice.set(0) 
        self.bot_choice.set(0)

        self.dev_choice = tk.IntVar()

        self.autologinFalse = tk.Radiobutton(self, text="Disabled", padx = 20,  variable=self.autologin_choice,  command=self.chooseLoginType, value=0).grid(row=5, column = 1)
        self.autologinTrue = tk.Radiobutton(self, text="Enabled", padx = 20,  variable=self.autologin_choice,  command=self.chooseLoginType, value=1).grid(row=6, column = 1)
        self.botchoiceAutobidder = tk.Radiobutton(self, text="AutoBidder", padx = 20,  variable=self.bot_choice,  command=self.chooseBotType, value=0).grid(row=7, column = 1)
        self.botchoiceAutobuyer = tk.Radiobutton(self, text="AutoBuyer", padx = 20,  variable=self.bot_choice,  command=self.chooseBotType, value=1).grid(row=8, column = 1)
        self.devModeCheckbox = tk.Checkbutton(self, text='Developer mode',variable=self.dev_choice, onvalue=1, offvalue=0, command=self.chooseDevMode).grid(row = 9, column = 0)

        self.login_btn_text = tk.StringVar()
        self.login_btn_text.set("Auto Login")
        self.login = tk.Button(self, textvariable=self.login_btn_text, width=30, command=self.login)
        self.login.grid(row=10, column=0, columnspan = 2, pady=25)
        self.reloadFunctions = tk.Button(self, text='Reload', command=self.reloadfunctions)
        self.reloadFunctions.grid(row=9, column=1)
        self.reloadFunctions.grid_remove()

    def chooseDevMode(self):
        choice = self.dev_choice.get()
        # self.controller.playerfilters.dev_choice.get()
        if (choice == 1):
            self.reloadFunctions.grid()
        if (choice == 0):
            self.reloadFunctions.grid_remove()

    def chooseLoginType(self):
        choice = str(self.autologin_choice.get())
        self.update_list()

        if (choice == "1"):
            login_exists = path.exists("./data/logins.txt")
            if (login_exists):
                log_event(self.controller.parentQueue, "Autologin enabled")
                msg = "AutoLogin enabled - Logins.txt file (in the Data folder) must be structured like this: \n Line 1: EA login \n Line 2: EA password \n Line 3: Email login (optional - used for auto fetching code, see readme) \n Line 4: Email password (optional - see above) "
                self.popupmsg(msg)
            else:
                pathstr = os.path.abspath(__file__)
                pathstr = str(pathstr)

                slash = pathstr[-8]
                pathstr_new = pathstr[:-11]
                pathstr_new = pathstr_new + "data"


                log_event(self.controller.parentQueue, pathstr)
                log_event(self.controller.parentQueue, pathstr_new)

                save_path = pathstr_new
                file_name = "logins.txt"

                completeName = os.path.join(save_path, file_name)
                # print(completeName)
              
                file1 = open(completeName, "w")
                file1.write("EA login \nEA password\nEmail login (enter some fake random email if not using auto-code fetch)\nLine 4: Email password (same as above, fill with fake password, it might cause an exception otherwise. Main benefit of autologin is code fetching so you probably should just login manually if not using)")
                file1.close()
                msg = "AutoLogin enabled - Logins.txt file (in the Data folder) must be structured like this: \n Line 1: EA login \n Line 2: EA password \n Line 3: Email login (used for auto fetching code, see readme) \n Line 4: Email password (used for code fetching)\nLogging in manually is probably easier"
                self.popupmsg(msg)

    def chooseBotType(self):
        choice = str(self.bot_choice.get())

        # Show and hide autobidder / autobuyer stats based on user input
        if (choice == "1"):
            self.controller.mainbuttons.autobidder.grid_remove()
            self.controller.mainbuttons.autobuyer.grid()
            msg = "Not yet implemented - if you want this let me know on GitHub, already built and easy to add in. Just personally don't use so haven't felt the need"
            self.popupmsg(msg)
        if (choice == "0"):
            self.controller.mainbuttons.autobuyer.grid_remove()
            self.controller.mainbuttons.autobidder.grid()

    def add_player_futbin(self):
        futbin_url = self.futbinlink_text.get()

        self.add_btn_futbin.config(state="disabled")
        self.remove_btn.config(state="disabled")
        self.controller.mainbuttons.test2.config(state="disabled")
        self.thread = ThreadedClient(self.controller.parentQueue, futbin_url, "add player", self.controller.mainbuttons.driver)
        self.thread.start()
        self.periodiccall()
        # thread_runner.RunThread(self.controller.parentQueue, self.controller.mainbuttons.driver, "getFutbinDataFromURL", "", futbin_url).start()
        # # log_event(self.controller.parentQueue, "Added player to player list")
        # msg = "Note the autobidder is only tested on low value cards (such as non-rare golds) with **ONLY 1 version of their card**. \n Players like Giroud for example, are not good because there are 4 different Giroud cards. \n I recommend random non-rare golds selling for just under or just above 1,000 coins. "
        # self.popupmsg(msg)
        # self.update_list()


    def update_list(self):
        for i in self.controller.table.router_tree_view.get_children():
            self.controller.table.router_tree_view.delete(i)

        txt = open("./data/player_list.txt", "r", encoding="utf8")

        self.playerlist = []
        for aline in txt:
            values2 = aline.strip("\n").split(",")
            # print(values2)
            cardname = values2[1]
            rating = values2[2]
            futbinprice = values2[9]
            realprice = values2[11]
            buypct = values2[12]

            values_small_view = []
            values_small_view.append(cardname)
            values_small_view.append(rating)
            values_small_view.append(futbinprice)
            values_small_view.append(realprice)
            values_small_view.append(buypct)

            self.controller.table.router_tree_view.insert('', 'end', values=values_small_view)
        txt.close()

        # Every 10 seconds refresh
        self.after(10000, self.update_list)

    def remove_player(self):
        index = self.controller.table.router_tree_view.selection()[0]
        selected_item = self.controller.table.router_tree_view.item(index)['values']
        player_to_remove_name = selected_item[0]

        # print(player_to_remove_name)

        txt = open("./data/player_list.txt", "r", encoding="utf8")


        entries_to_stay = []
        for line in txt:
            line = line.strip("\n")
            line_arr = line.split(",")

            name = line_arr[1]

            print(name)

            if (name != player_to_remove_name):
                print((line_arr))
                entries_to_stay.append(line)
            else:
                print("to remove: " + str(line_arr))

        txt.close()

        # Truncate file
        file = open("./data/player_list.txt", "r+")
        file.truncate(0)
        file.close()

        # Re-append old data
        hs = open("./data/player_list.txt", "a", encoding="utf8")
        for line in entries_to_stay:
            hs.write(line + "\n")
        hs.close()

        self.update_list()

    # def login(self):
    #     # Disable the start button
    #     self.test2.config(state="disabled")
    #     self.thread = ThreadedClient(self.controller.parentQueue, 0, "login")
    #     self.thread.start()
    #     self.periodiccall()
    #     # self.isFirstStart = False

    def login(self):
        choice = str(self.autologin_choice.get())


        if (choice == "1"):
            login_exists = path.exists("./data/logins.txt")
            
            if login_exists:
                log_event(self.controller.parentQueue, "Auto logging in...")
                txt = open("./data/logins.txt", "r")
                counter = 0
                for aline in txt:
                    counter += 1
                txt.close()

                # Double check logins.txt has 4 lines before attempting sign in to avoid error
                if (counter == 4):
                    self.login.config(state="disabled")
                    self.login_btn_text.set("Logging/logged in")

                    self.thread = ThreadedClient(self.controller.parentQueue, 0, "login", self.controller.mainbuttons.driver)
                    
                    self.thread.start()
                    self.periodiccall()

                else:
                    self.popupmsg("Logins.txt formatted wrong, login manually")

                

                # self.after(100, self.process_queue)

            else:
                self.popupmsg("Logins.txt not found, login manually")
        else:
            msg = "Autologin not enabled, must login manually"
            self.popupmsg(msg)

    def periodiccall(self):
        self.checkqueue()
        if self.thread.is_alive():
            self.after(100, self.periodiccall)
        else:
            # self.login.config(state="active")
            self.login_btn_text.set("Auto login")
            self.controller.playerfilters.add_btn_futbin.config(state="active")
            self.controller.playerfilters.remove_btn.config(state="active")
            self.controller.mainbuttons.test2.config(state="active")


    def checkqueue(self):
        while self.controller.parentQueue.qsize():
            try:
                msg = self.controller.parentQueue.get(0)
                self.controller.mainbuttons.listbox.insert('end', msg)
                self.write_logs_tofile(msg)
                self.controller.mainbuttons.progressbar.step(1)
            except Queue.Empty:
                pass

    def write_logs_tofile(self, event):
        file_object = open('./data/gui_logs.txt', 'a')
        now = datetime.now()
        dt_string = now.strftime("[%H:%M:%S] ")

        full_log = dt_string + event + "\n"
        print(full_log)
        file_object.write(full_log)
        file_object.close()

    def popupmsg(self, msg):
        self.update_list()
        popup = tk.Tk()
        popup.wm_title("Note")
        label = ttk.Label(popup, text=msg, font=NORM_FONT)
        label.pack(side="top", fill="x", pady=10)
        B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
        B1.pack()
        log_event(self.controller.parentQueue, str(msg))
        popup.mainloop()

    def reloadfunctions(self):
        importlib.reload(thread_runner)
        importlib.reload(autobidder)
        importlib.reload(helpers)

# Middle right
class Table(tk.Frame):

    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller

        tk.Frame.__init__(self, parent)

        self.status = tk.Label(self, text="Player List", font=LARGE_FONT)
        self.status.grid(row = 0, column = 0)

        # Player list table
        columns = ["Name", "Rating", "Futbin Price", "Real Price", "Buy %", "Max Bid"]

        self.router_tree_view = Treeview(self, columns=columns, show="headings", height=5)
        # self.router_tree_view.column("id", width=30)

        # Luis Rodríguez,RODRÍGUEZ,78,Tigres,Mexico,Non-Rare,RB,192045,938,700,21,0,0.85

        for col in columns:
            colwidth = 70
            if col == "Card name":
                colwidth = 135
            self.router_tree_view.column(col, width=colwidth)
            self.router_tree_view.heading(col, text=col)

        #router_tree_view.bind('<<TreeviewSelect>>', select_router)
        self.router_tree_view.grid(row=1,column=0)

        # LOAD IN TABLE
        txt = open("./data/player_list.txt", "r", encoding="utf8")

        self.playerlist = self.controller.playerfilters.playerlist

        #self.playerlist = []
        for aline in txt:
            values2 = aline.strip("\n").split(",")
            # print(values2)
            self.playerlist.append(values2)
            cardname = values2[1]
            rating = values2[2]
            futbinprice = values2[9]
            realprice = values2[11]
            buypct = values2[12]

            values_small_view = []
            values_small_view.append(cardname)
            values_small_view.append(rating)
            values_small_view.append(futbinprice)
            values_small_view.append(realprice)
            values_small_view.append(buypct)

            # print(values_small_view)
            self.router_tree_view.insert('', 'end', values=values_small_view)
        txt.close()

# Full Left
class MainButtons(tk.Frame):

    def __init__(self, parent, controller):

        self.parent = parent
        self.controller = controller

        # self.queue

        # ~ ~ ~ ~ INITIATE BOT ~ ~ ~ ~ ~
        log_event(self.controller.parentQueue, " - - - - Bot started - - - - ")
        self.driver = self.create_driver()
        self.action = ActionChains(self.driver)
        self.driver.get("https://www.ea.com/fifa/ultimate-team/web-app/")

        tk.Frame.__init__(self, parent)
        self.playerlist = self.controller.playerfilters.playerlist

        # Create frame for autobidder and autobuyer within mainbots frame
        self.autobidder = tk.LabelFrame(self, text="Autobidder")
        self.autobuyer = tk.LabelFrame(self, text="Autobuyer")

        self.autobidder.grid(row=0, column=0)
        self.autobuyer.grid(row=0, column=1)

        # Load Autobidder stats
        autobidderstats_json = open('./data/gui_stats.json')
        json1_str = autobidderstats_json.read()
        autobidder_data = json.loads(json1_str)[0]
        
        self.autobidder_labels = []
        count = 0
        for key, value in autobidder_data.items():
            key = str(key) + ":"
            value = str(value)
            valuevar = tk.StringVar()
            valuevar.set('')
            tk.Label(self.autobidder, text=key).grid(row=count, column=0, sticky = W)
            tk.Label(self.autobidder, textvariable=valuevar).grid(row=count, column=1)
            self.autobidder_labels.append(valuevar)
            count+=1

        # Load Autobuyer stats
        autobuyerstats_json = open('./data/autobuyer_stats.json')
        json2_str = autobuyerstats_json.read()
        autobuyer_data = json.loads(json2_str)[0]
        
        self.autobuyer_labels = []
        count = 0
        for key, value in autobuyer_data.items():
            key = str(key) + ":"
            value = str(value)
            valuevar = tk.StringVar()
            valuevar.set('yup')
            tk.Label(self.autobuyer, text=key).grid(row=count, column=0, sticky = W)
            tk.Label(self.autobuyer, textvariable=valuevar).grid(row=count, column=1)
            self.autobuyer_labels.append(valuevar)
            count+=1

        num_autobidder_labels = len(autobidder_data)
        num_autobuyer_labels = len(autobuyer_data)

        self.startautobidder_label = tk.StringVar()
        self.startautobidder_label.set("Start Autobidder")
        self.test2 = tk.Button(self.autobidder, textvariable=self.startautobidder_label, width=15, command=self.startAutobidder)
        self.test2.grid(row=num_autobidder_labels+1, column=0, columnspan = 2)
        self.test3 = tk.Button(self.autobuyer, text='Start Autobuyer', width=15, command=self.startAutobuyer).grid(row=num_autobuyer_labels+1, column=0, columnspan = 2)

        # Bid conservation mode
        self.autobidder_safe_label = tk.Label(self.autobidder, text='Minimize wasted bids: ', font=SMALL_FONT)
        self.autobidder_safe_label.grid(row=num_autobidder_labels+2, column=0)
        self.autobidder_safe_option = tk.IntVar()
        self.autobidder_safe_checkbox = tk.Checkbutton(self.autobidder, text='',variable=self.autobidder_safe_option, onvalue=1, offvalue=0, command=self.chooseSafeMode).grid(row = num_autobidder_labels+2, column = 1)

        # Sleep time between rounds
        self.sleeptime_label = tk.Label(self.autobidder, text='Sleep between rounds (mins): ', font=SMALL_FONT)
        self.sleeptime_text = tk.IntVar(value = 3)
        self.sleeptime_entry = tk.Entry(self.autobidder, textvariable=self.sleeptime_text, width=3)
        self.sleeptime_label.grid(row=num_autobidder_labels+3, column=0)
        self.sleeptime_entry.grid(row=num_autobidder_labels+3, column=1)

        # Bot speed
        self.autobidder_speed_label = tk.Label(self.autobidder, text='Bot Speed: ', font=SMALL_FONT)
        self.autobidder_speed_label.grid(row=num_autobidder_labels+4, column=0, rowspan=3)
        self.autobidder_speed_option = tk.IntVar()
        self.autobidder_speed_entry1 = tk.Radiobutton(self.autobidder, text='1x',variable=self.autobidder_speed_option, value=1, command=self.chooseBotSpeed).grid(row = num_autobidder_labels+4, column = 1)
        self.autobidder_speed_entry2 = tk.Radiobutton(self.autobidder, text='1.25x',variable=self.autobidder_speed_option, value=2, command=self.chooseBotSpeed).grid(row = num_autobidder_labels+5, column = 1)
        self.autobidder_speed_entry3 = tk.Radiobutton(self.autobidder, text='1.5x',variable=self.autobidder_speed_option, value=3, command=self.chooseBotSpeed).grid(row = num_autobidder_labels+6, column = 1)

        self.autobidder_speed_option.set(1)
        self.autobidder_safe_option.set(0)
    
        # Save options
        self.saveoptions = tk.Button(self.autobidder, text='Save Configuration', width=15, command=self.saveConfig).grid(row=num_autobidder_labels+7, column=0, columnspan = 2)
        self.autobuyer.grid_remove()

        self.update_stat_labels()
        self.saveConfig()

        self.listbox = tk.Listbox(self.autobidder, width=20, height=5)
        self.listbox.grid(row=num_autobidder_labels+8, column=0, columnspan = 7)
        self.progressbar = ttk.Progressbar(self.autobidder, orient='horizontal',
                                           length=300, mode='determinate')
        self.progressbar.grid(row=num_autobidder_labels+9, column=0, columnspan = 7)
        self.isFirstStart = True
        
        # Initialize bot object + globala queue here - parent autobidder so user vars are not lost on failure
        # self.parentAutobidder = Autobidder(self.driver, self.controller.parentQueue)

    def startAutobidder(self):
        # Disable the start button
        self.test2.config(state="disabled")
        self.startautobidder_label.set("Autobidder Running")
        self.controller.playerfilters.add_btn_futbin.config(state="disabled")
        self.controller.playerfilters.remove_btn.config(state="disabled")
        self.thread = ThreadedClient(self.controller.parentQueue, self.isFirstStart, "autobidder", self.driver)
        self.thread.start()
        self.periodiccall()
        self.isFirstStart = False
        # self.parentAutobidder = Autobidder(self.driver, self.controller.parentQueue)
        # thread_runner.RunThread(self.controller.parentQueue, self.driver, "autobidder", self.parentAutobidder, self.isFirstStart).start()

        # self.isFirstStart = False

        # self.after(100, self.process_queue)        
        # If dev mode is enabled, thread runner will not use parentAutobidder - it will make a new (which can be updated using reload functions button)
        # devModeState = self.controller.playerfilters.dev_choice.get()
        # if (devModeState == 1):
        #     thread_runner.RunThread(self.controller.parentQueue, self.driver, "autobidder_devmode", self.parentAutobidder, "").start()
        #     self.after(1000, self.process_queue)
        # else:
    
    def periodiccall(self):
        self.checkqueue()
        if self.thread.is_alive():
            self.after(100, self.periodiccall)
        else:
            self.startautobidder_label.set("Start Autobidder")
            self.test2.config(state="active")
            self.controller.playerfilters.add_btn_futbin.config(state="active")
            self.controller.playerfilters.remove_btn.config(state="active")

    def checkqueue(self):
        while self.controller.parentQueue.qsize():
            try:
                msg = self.controller.parentQueue.get(0)
                self.listbox.insert('end', msg)
                self.write_logs_tofile(msg)
                self.progressbar.step(1)
            except Queue.Empty:
                pass

    def write_logs_tofile(self, event):
        file_object = open('./data/gui_logs.txt', 'a')
        now = datetime.now()
        dt_string = now.strftime("[%H:%M:%S] ")

        full_log = dt_string + event + "\n"
        print(full_log)
        file_object.write(full_log)
        file_object.close()

    def saveConfig(self):
        print("Config - - -")
        botspeed = self.autobidder_speed_option.get()

        if (botspeed == 1):
            botspeed = 1
        if (botspeed == 2):
            botspeed = 1.25
        if (botspeed == 3):
            botspeed = 1.5

        sleeptime = int(self.sleeptime_entry.get())

        sleeptime_seconds = sleeptime*60
        safemode = int(self.autobidder_safe_option.get())

        log_event(self.controller.parentQueue, "Bot Speed set: " + str(botspeed))
        log_event(self.controller.parentQueue, "Sleep time set: " + str(sleeptime))
        log_event(self.controller.parentQueue, "Safe mode set: " + str(safemode))

        with open('./data/config.json', 'r') as f:
            json_data = json.load(f)
            # json_data2 = json_data[0] 
            json_data[0]["conserve_bids"] = safemode
            json_data[0]["sleep_time"] = sleeptime_seconds
            json_data[0]["speed"] = botspeed

        with open('./data/config.json', 'w') as f:
            f.write(json.dumps(json_data))
        
    def chooseBotSpeed(self):
        botspeed = self.autobidder_speed_option.get()
        if (botspeed == 1):
            botspeed = 1
        if (botspeed == 2):
            botspeed = 1.25
        if (botspeed == 3):
            botspeed = 1.5

        with open('./data/config.json', 'r') as f:
            json_data = json.load(f)
            json_data[0]["speed"] = botspeed

        with open('./data/config.json', 'w') as f:
            f.write(json.dumps(json_data))

    def chooseSafeMode(self):
        choice = self.autobidder_safe_option.get()

        msg = "Use this to avoid needless bid wars. \n If bid wars are consistently ending near your price ceiling, definitely enable this \n (you're probably fighting another autobidder and should choose a new player) \n This also avoids a soft ban, if you make over a certain number of bids in a day"
        # self.controller.playerfilters.dev_choice.get()
        if (choice == 1):
            self.controller.playerfilters.popupmsg(msg)
        if (choice == 0):
            print("yeaeo")

        with open('./data/config.json', 'r') as f:
            json_data = json.load(f)
            # json_data2 = json_data[0] 
            json_data[0]["conserve_bids"] = choice

        with open('./data/config.json', 'w') as f:
            f.write(json.dumps(json_data))

    def chooseSleepTime(self):
        choice = self.sleeptime_text.get()
        # print("Sleep time choice: " + str(choice))
        
    # Creates webdriver instance to be passed to all methods
    def create_driver(self):
        system = platform.system()

        if system == 'Darwin':
            path = 'chrome_mac/chromedriver'
        elif system == 'Linux':
            path = 'chrome_linux/chromedriver'
        elif system == 'Windows':
            path = os.getcwd() + '\chrome_windows\chromedriver.exe'

        option = webdriver.ChromeOptions()

        # For older ChromeDriver under version 79.0.3945.16
        option.add_argument("--ignore-certificate-error")
        option.add_argument("--ignore-ssl-errors")
        option.add_experimental_option("excludeSwitches", ["enable-automation"])
        option.add_experimental_option('useAutomationExtension', False)

        # For ChromeDriver version 79.0.3945.16 or over
        option.add_argument('--disable-blink-features=AutomationControlled')

        driver = webdriver.Chrome(executable_path=path, options=option)
        driver.maximize_window()

        return driver

    # Continuously updates log table, inefficient but it works
    def update_stat_labels(self):
        try:
            # Load Autobidder stats
            autobidderstats_json = open('./data/gui_stats.json')
            json1_str = autobidderstats_json.read()
            autobidder_data = json.loads(json1_str)[0]
            
            autobiddervals = []
            for key, value in autobidder_data.items():
                autobiddervals.append(value)

            # Load Autobuyer stats
            autobuyerstats_json = open('./data/autobuyer_stats.json')
            json2_str = autobuyerstats_json.read()
            autobuyer_data = json.loads(json2_str)[0]
            
            autobuyervals = []
            for key, value in autobuyer_data.items():
                autobuyervals.append(value)

            count = 0
            for label in self.autobidder_labels:
                val = label.get()
                label.set(autobiddervals[count])
                count+=1
            
            count = 0
            for label in self.autobuyer_labels:
                val = label.get()
                label.set(autobuyervals[count])
                count+=1

            self.after(300, self.update_stat_labels)
        except:
            print("Error in updating GUI labels")

    # These functions are called on button press
    def testfunc(self):
        thread_runner.RunThread(self.controller.parentQueue, self.driver, "test", self.controller.playerfilters.playerlist, "").start()
        self.after(100, self.process_queue)

    def startWatchlistManager(self):
        self.queue = queue.Queue()
        # thread_runner.RunThread(self.queue, self.driver, "watchlist", self.parentAutobidder, "").start()
        # self.after(100, self.process_queue)

    def startAutobuyer(self):
        # thread_runner.RunThread(self.queue, self.driver, "autobuyer", self.controller.playerfilters.playerlist, "").start()
        self.after(1000, self.process_queue)

    def reloadfunctions(self):
        importlib.reload(thread_runner)
        importlib.reload(autobidder)
        importlib.reload(helpers)
        # self.after(100, self.process_queue)

    def process_queue(self):
        try:
            #  # Load Autobidder stats

            msg = self.controller.parentQueue.get(0)
            self.controller.table.status["text"] = str(msg)
            log_event(self.controller.parentQueue, msg)
        except queue.Empty:
            self.after(100, self.process_queue)

# Bottom right
class DisplayLogs(tk.Frame):

    def __init__(self, parent, controller):

        self.parent = parent
        self.controller = controller

        tk.Frame.__init__(self, parent)

        self.status2 = tk.Label(self, text="Logs", font=LARGE_FONT)
        self.status2.grid(row = 0, column = 0)

        # Player list table
        columns = ['log']
        self.loggings = Treeview(self, columns=columns, show="headings")
        self.loggings.column("log", width=415)

        for col in columns[1:]:
            self.loggings.column(col, width=1)
            self.loggings.heading(col, text=col)

        #loggings.bind('<<TreeviewSelect>>', select_router)
        self.loggings.grid(row=1,column=0)

        # LOAD IN TABLE
        txt = open("./data/gui_logs.txt", "r", encoding="latin-1")

        #self.playerlist = []
        for aline in txt:
            values2 = aline.strip("\n").split(",")
            self.loggings.insert('', 'end', values=values2)

        self.update_logs()

    # Continuously updates log table
    def update_logs(self):
        for i in self.loggings.get_children():
            self.loggings.delete(i)

        txt = open("./data/gui_logs.txt", "r", encoding="latin-1")

        self.playerlist = []
        for aline in txt:
            values2 = aline.strip("\n").split(",")
            self.loggings.insert('', 'end', values=values2)
        txt.close()
        self.loggings.yview_moveto(1)
        self.after(100, self.update_logs)


class ThreadedClient(threading.Thread):

    def __init__(self, queue, firstStart, action, driver):
        threading.Thread.__init__(self)
        self.queue = queue
        self.firstStart = firstStart
        self.action = action
        self.driver = driver

        self.futbinurl = firstStart

    def run(self):
        if (self.action == "autobidder"):
            autobidderObject = Autobidder(self.driver, self.queue)
            if (self.firstStart):
                autobidderObject.initializeBot()
            else:
                autobidderObject.start()
            # for x in range(1, 5):
            #     time.sleep(2)
            #     msg = "Function %s finished..." % x
            #     self.queue.put(msg)
        if (self.action == "login"):
            self.queue.put("Logging in")
            time.sleep(5)
            
            txt = open("./data/logins.txt", "r")
            counter = 0
            credentials = []
            for aline in txt:
                counter += 1
                line = aline.strip("\n")
                credentials.append(str(line))
            txt.close()

            USER = {
                "email": credentials[0],
                "password": credentials[1],
            }

            EMAIL_CREDENTIALS = {
                "email": credentials[2],
                "password": credentials[3],
            }

            login(self.queue, self.driver, USER, EMAIL_CREDENTIALS)
        if (self.action == "add player"):
            getFutbinDataAndPopulateTable(self.driver, self.queue, self.futbinurl)


# TODO insert create logins.txt method here, that makes first line say not entered - update msgbox method
clearOldUserData_nonclass()
app = GUI()
app.title("TMB's FIFA 21 Autobidder")
app.mainloop()
