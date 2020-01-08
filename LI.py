import apache_log_parser
import datetime
import pandas as pd
import subprocess
from pprint import pprint

class LI():
  def __init__(self):
    self.log_list = []

  def LogReceiver(self, file_locate, log_format):
    parser = apache_log_parser.make_parser(log_format)
    P = []
    E = []
    with open(file_locate) as f:
      for line in f:
        try:
          parsed_line = parser(line)
          P.append(parsed_line)
        except ValueError:
          E.append(line)
    print("Parsed    : {0}".format(len(P)))
    print("ValueError: {0}".format(len(E)))
    self.log_list[len(self.log_list):len(self.log_list)] = P

  def Stream_LogReceiver(self, file_locate, log_format, time_from, time_to):
    parser = apache_log_parser.make_parser(log_format)
    with open(file_locate) as f:
      line = f.readline()
      counter_t = {}
      counter_h = {}
      ac = 0
      while line:
        parsed_line = parser(line)
#        print(parsed_line)
        #
        timeobj = parsed_line["time_received_datetimeobj"]
        if timeobj < time_from or time_to < timeobj:
          line = f.readline()
          continue

        target_t = str(timeobj.year) + "-" + str(timeobj.month) + "-" + str(timeobj.day) + "-" + str(timeobj.hour)
        try:
          counter_t[target_t] += 1
        except KeyError:
          counter_t[target_t] = 1
        #
        target_h = parsed_line["remote_host"]
        try:
          counter_h[target_h] += 1
        except KeyError:
          counter_h[target_h] = 1
        #
        subprocess.call("clear")
        print("[*]Current number of log:",ac)
        ac += 1
        line = f.readline()
    return sorted(counter_h.items(), key=lambda x:x[1],reverse=True) , sorted(counter_t.items(), key=lambda x:x[0])

  def LogListParser(self, time_from, time_to):
    D = []
    print("[FROM]", time_from)
    print("[TO  ]", time_to)
    for page in self.log_list:
      target = page["time_received_datetimeobj"]
      if time_from <= target <= time_to:
        D.append(page)
    self.log_list = D

  def LogInitializer(self):
    self.log_list = []

  def LogListPrinter(self):
    for page in self.log_list:
      print(page["time_received"],page["remote_host"],page["remote_logname"],page["remote_user"],page["request_first_line"],page["status"],page["request_header_user_agent"])
#      pprint(page)

  def AC_AtHost(self):
    counter = {}
    for page in self.log_list:
      target = page["remote_host"]
      try:
        counter[target] += 1
      except KeyError:
        counter[target] = 1
    return sorted(counter.items(), key=lambda x:x[1],reverse=True)

  def AC_AtTime(self):
    counter = {}
    for page in self.log_list:
      timeobj = page["time_received_datetimeobj"]
      target = str(timeobj.year) + "-" + str(timeobj.month) + "-" + str(timeobj.day) + "-" + str(timeobj.hour)
      try:
        counter[target] += 1
      except KeyError:
        counter[target] = 1
    return sorted(counter.items(), key=lambda x:x[0])

  def OutputCSV(self,filename):
    df = pd.DataFrame(self.log_list)
    df.to_csv(filename)

  def OutputCSV2(self,data,filename):
    df = pd.DataFrame(data)
    df.to_csv(filename)
