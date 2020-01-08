import argparse
import subprocess
import sys
import datetime
from pprint import pprint
from LI import LI
import os

FILE = "/var/log/httpd/access_log"

format = '%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"'
oflag = False
output_f = ""
##
li = LI()
def print_banner():
  subprocess.call("clear")
  print("=================================================================")
  print("|                                                               |")
  print("|                  LOGINSPECTOR FOR APPACHE                     |")
  print("|                                                               |")
  print("=================================================================")

def print_message():
  print()
  print("[**]Current Log",len(li.log_list))
  print("-----------------------------------------------------------------")
  print("\033[31m Quit           : Q\033[0m")
  print(" \033[31mA\033[0mddFile        : A")
  print(" \033[31mS\033[0mhowLog        : S")
  print(" \033[31mF\033[0mlashLog       : F")
  print(" \033[31mC\033[0mountAccess    : C")
  print(" \033[31mP\033[0marseLog       : P")
  print(" \033[31mO\033[0mutputOption   : O         --Set output file e/d and name      ")
  print()
  print(" \033[07mStreamMode     : M         --Change mode to stream for big data\033[0m")
  print("-----------------------------------------------------------------")
  print("(LI)>",end="")
print_banner()
print("[*]Connect your log file")
print("(LI)>",FILE)
try:
  li.LogReceiver(FILE,format)
  print("[*]...OK")
except Exception as e:
  print("[!]Input File Error:",str(e))

while True:
  print_message()
  cmd = input()
  #
  if cmd == "Q" or cmd == "q": break
  #
  elif cmd == "A" or cmd == "a":
    print("(LI)[!]Input your log file location:",end="")
    file_locate = input()
    print("[*]Connect your log file")
    print("->",file_locate)
    try:
      li.LogReceiver(file_locate,format)
      print("[*]...OK")
    except Exception as e:
      print("[!]Input File Error:",str(e))
  #
  elif cmd == "C" or cmd == "c":
    print("[*]CountAccess for each RemoteHost: R")
    print("[*]CountAccess for each Time      : T")
    cmd = input()
    if cmd == "R" or cmd == "r":
      dict = li.AC_AtHost()
      for page in dict:
        pprint(page)
      if oflag:
        try:
          li.OutputCSV2(dict,output_f)
          print("[*]Success create file:",output_f)
        except:
          print("[!]Output Error:",str(e))

    elif cmd == "T" or cmd == "t":
      dict = li.AC_AtTime()
      for page in dict:
        pprint(page)
      if oflag:
        try:
          li.OutputCSV2(dict,output_f)
          print("[*]Success create file:",output_f)
        except:
          print("[!]Output Error:",str(e))
    else:
      print("[!]No command:",cmd)
  #
  elif cmd == "P" or cmd == "p":
    print("[*]Input type:      [YYYY MM DD HH MM SS]")
    print("(LI)[!]Input start time :",end="")
    time = list(map(int,input().split()))
    date_from = datetime.datetime(year=time[0],month=time[1],day=time[2],hour=time[3],minute=time[4],second=time[5])
    print("(LI)[!]Input end   time :",end="")
    time = list(map(int,input().split()))
    date_to = datetime.datetime(year=time[0],month=time[1],day=time[2],hour=time[3],minute=time[4],second=time[5])
    li.LogListParser(date_from, date_to)
  #
  elif cmd == "F" or cmd == "f":
    print("[!]Flash All Log?")
    print("(LI)[Y/N]>",end="")
    cmd = input()
    if cmd == "Y" or cmd == "y":
      li.LogInitializer()
      print("[*]Flashed. Add your Log File[A] or Quit[Q]")
    else:
      print("[*]Flash is rejected")
  #
  elif cmd == "S" or cmd == "s":
    print("[*]Show Log")
    li.LogListPrinter()
    if oflag:
      try:
        li.OutputCSV(output_f)
        print("[*]Success create file:",output_f)
      except:
        print("[!]Output Error:",str(e))
  #
  elif cmd == "O" or cmd == "o":
    print("[!]Enable File output?")
    print("(LI)[Y/N]->",end="")
    cmd2 = input()
    if cmd2 == "Y" or cmd2 == "y":
      print("[!]Input output file name")
      print("(LI)>",end="")
      output_f = input()
      oflag = True
    else:
      print("[*]Disable Output file")
      oflag = False
  #
  elif cmd == "M" or cmd == "m":
    date_from = datetime.datetime(year=1,month=1,day=1,hour=0,minute=0,second=0)
    date_to   = datetime.datetime(year=9999,month=1,day=1,hour=0,minute=0,second=0)
    #
    print("[*]Stream Processor for big data")
    print("[!]Input your log file")
    print("(LI)>",end="")
    stream_f = input()
    print("[*]Connect your log file")
    print("->",stream_f)
    print()
    #
    print("[!]Parse Log?")
    print("(LI)[Y/N]->",end="")
    cmd_t = input()
    if cmd_t == "Y" or cmd_t == "y":
      print("[*]Input type:      [YYYY MM DD HH MM SS]")
      print("(LI)[!]Input start time :",end="")
      time = list(map(int,input().split()))
      date_from = datetime.datetime(year=time[0],month=time[1],day=time[2],hour=time[3],minute=time[4],second=time[5])
      print("(LI)[!]Input end   time :",end="")
      time = list(map(int,input().split()))
      date_to = datetime.datetime(year=time[0],month=time[1],day=time[2],hour=time[3],minute=time[4],second=time[5])

    #
    try:
      if(os.path.exists(stream_f)):
        print("[*]...OK")
      dict_r, dict_t = li.Stream_LogReceiver(stream_f, format,date_from,date_to)
      #
      try:
        li.OutputCSV2(dict_r,"access_count_athost.csv")
        print("[*]Success create file:","access_count_athost.csv")
        li.OutputCSV2(dict_t,"access_count_attime.csv")
        print("[*]Success create file:","access_count_attime.csv")
      except Exception as ee:
        print("[!]Output File Error:",str(ee))
    except Exception as e:
      print("[!]Input File Error:",str(e))

  else:
    print("[!]No command:",cmd)
