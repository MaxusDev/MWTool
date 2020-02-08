import sys
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import serial
from serial.tools.list_ports import comports
import numpy as np
import re
from mw0582_algo import *

#If we are using python 2.7 or under
if sys.version_info[0] < 3:
    import Tkinter as tk
    import ttk
#If we are using python 3.0 or above
elif sys.version_info[0] >= 3:
    import tkinter as tk
    from tkinter import ttk


class SensingGUI(tk.Frame):
  """docstring for SensingGUI"""

  def define_var(self):

    self.s = None

    self.triggerVar = tk.StringVar(self)
    self.triggerVar.set("Trigger")
    self.opBoxVar = tk.StringVar(self)
    self.opBoxVar.set("-")
    self.labelVar = tk.StringVar(self)
    self.labelVar.set("Not connected.")

    self.avgCheck = tk.IntVar(self)
    self.irCheck = tk.IntVar(self)
    self.dcrCheck = tk.IntVar(self)
    self.envCheck = tk.IntVar(self)

    self.checkButtons = [self.avgCheck,self.irCheck,self.dcrCheck,self.envCheck]

  def app_quit(self):
    self.master.destroy()
    self.master.quit()
    if self.s is not None:
        self.s.flush()
        self.s.close()

  def create_widgets(self, plotObject):
    self.menubar = tk.Menu(self.master)
    self.filemenu = tk.Menu(self.menubar, tearoff=0)
    self.filemenu.add_command(label="Exit", command=self.app_quit)

    # Left Frame
    self.leftFrame = tk.Frame(self.master, padx=10, pady=10)
    self.leftFrame.grid(row=0, column=0, sticky='N,W,S,E', rowspan=20)

    # Plot Frame
    # For data visualization

    self.plotFrame = tk.LabelFrame(self.leftFrame, padx=10, pady=10, borderwidth=2, text='Raw Plot', labelanchor='nw', relief=tk.RIDGE)
    self.plotFrame.grid(row=0, column=0)


    self.canvas = FigureCanvasTkAgg(plotObject.drawArea, master=self.plotFrame)
    self.canvas._tkcanvas.grid(row=0, column=0)
    self.canvas.draw()

    # Right Frame
    self.rightFrame = tk.Frame(self.master, padx=10, pady=10)
    self.rightFrame.grid(row=0, column=1, sticky='N,W,S,E', rowspan=20)

    self.operFrame = tk.Frame(self.rightFrame, padx=10, pady=10)
    self.operFrame.grid(row=0, column=0, columnspan=2, sticky='w,e')

    if sys.platform.startswith('darwin'):
        # portChoices = tuple([p[0].replace('/cu.', '/tty.') for p in comports() if p[0].find('SLAB') >= 0])
        portChoices = tuple([p[0].replace('/cu.', '/tty.') for p in comports()])
    else:
        portChoices = tuple([p[0].replace('/cu.', '/tty.') for p in comports()])

    self.option = tk.OptionMenu(self.operFrame, self.opBoxVar, *portChoices)
    self.option.grid(row=0, column=0,sticky='w')

    def optionChanged(*args):
        print(self.opBoxVar.get())
        self.s = serial.Serial(self.opBoxVar.get(), 512000)
        # serial write AT command to device to enable raw data output
        command = "AT+DEBUG=0002"
        self.s.write(command.encode('utf-8'))
        self.s.flush()
        if self.s is not None:
            self.labelVar.set("Device connected.")
            self.runButton.config(state=tk.NORMAL)
            self.rfLabel.config(state=tk.NORMAL)
            # self.rfScale.config(state=tk.NORMAL)
            self.powerLabel.config(state=tk.NORMAL)
            self.powerScale.config(state=tk.NORMAL)
            self.gainLabel.config(state=tk.NORMAL)
            self.gainScale.config(state=tk.NORMAL)
            self.delayLabel.config(state=tk.NORMAL)
            self.delayScale.config(state=tk.NORMAL)
            self.avgCheckbutton.config(state=tk.NORMAL)
            # self.avgTapEntry.config(state=tk.NORMAL)
            self.irCheckbutton.config(state=tk.NORMAL)
            self.irTapEntry.config(state=tk.NORMAL)
            self.dcrCheckbutton.config(state=tk.NORMAL)
            # self.dcrTapEntry.config(state=tk.NORMAL)
            self.envCheckbutton.config(state=tk.NORMAL)
            # self.envTapEntry.config(state=tk.NORMAL)

    self.opBoxVar.trace("w", optionChanged)

    # Connection status label
    self.connLabel = tk.Label(self.operFrame, textvariable=self.labelVar)
    self.connLabel.grid(row=0, column=1,sticky='w')

    # Button
    self.pause = True
    self.ani = None

    def trigger():
        self.pause ^= True
        if self.pause:
            self.ani.event_source.stop()
            self.triggerVar.set("Trigger")
        else:
            self.ani = animation.FuncAnimation(plotObject.drawArea, plotObject.update, fargs=(self.s, self.checkButtons, plotObject.a0,), interval=1, blit=True)
            self.triggerVar.set("Pause")

    self.runButton = tk.Button(self.operFrame, textvariable=self.triggerVar, width=10, height=3, fg='red', command=trigger)
    # self.calibButton = tk.Button(self.operFrame, text='Re-Calibrate', width=10, height=3)
    self.runButton.grid(row=1, column=0,sticky='w')
    self.runButton.config(state=tk.DISABLED)
    # self.calibButton.grid(row=1, column=1,sticky='w')

    # Setting Frame
    self.settingFrame = tk.LabelFrame(self.rightFrame, padx=10, pady=10, borderwidth=2, text='Setting', labelanchor='nw', relief=tk.RIDGE)
    self.settingFrame.grid(row=1, column=0, sticky='w,e')

    # RF Range setting
    self.rfLabel = tk.Label(self.settingFrame, text='RF Range (in GHz)')
    self.rfLabel.grid(row=0, column=0, sticky='s,e')
    self.rfLabel.config(state=tk.DISABLED)
    self.rfScale = tk.Scale(self.settingFrame,
        from_ = 5.725,
        to = 5.875,
        orient = tk.HORIZONTAL,
        showvalue = 1,
        length = 200,
        resolution = 0.005,
        command = self.rf_scale_click
        )
    self.rfScale.grid(row=0, column=1)
    self.rfScale.config(state=tk.DISABLED)
    # TX Power setting
    self.powerLabel = tk.Label(self.settingFrame, text='TX Power')
    self.powerLabel.grid(row=1, column=0, sticky='s,e')
    self.powerLabel.config(state=tk.DISABLED)
    self.powerScale = tk.Scale(self.settingFrame,
        from_ = 0,
        to = 7,
        orient = tk.HORIZONTAL,
        showvalue = 1,
        length = 200,
        resolution = 1,
        command = self.power_scale_click
        )
    self.powerScale.grid(row=1, column=1)
    self.powerScale.config(state=tk.DISABLED)

    # RX Gain setting
    self.gainLabel = tk.Label(self.settingFrame, text='RX Gain')
    self.gainLabel.grid(row=2, column=0,sticky='s,e')
    self.gainLabel.config(state=tk.DISABLED)

    self.gainScale = tk.Scale(self.settingFrame,
        from_ = 0,
        to = 7,
        orient = tk.HORIZONTAL,
        showvalue = 1,
        length = 200,
        resolution = 1,
        command = self.gain_scale_click
        )
    self.gainScale.grid(row=2, column=1)
    self.gainScale.config(state=tk.DISABLED)

    # Delay setting
    self.delayLabel = tk.Label(self.settingFrame, text='Delay Time (in s)')
    self.delayLabel.grid(row=3, column=0,sticky='s,e')
    self.delayLabel.config(state=tk.DISABLED)
    self.delayScale = tk.Scale(self.settingFrame,
        from_ = 0,
        to = 3599,
        orient = tk.HORIZONTAL,
        showvalue = 1,
        length = 200,
        resolution = 100,
        command = self.delay_scale_click
        )
    self.delayScale.grid(row=3, column=1)
    self.delayScale.config(state=tk.DISABLED)

    # Processing Frame
    self.processFrame = tk.LabelFrame(self.rightFrame, padx=10, pady=10, borderwidth=2, text='Process', labelanchor='nw', relief=tk.RIDGE)
    self.processFrame.grid(row=2, column=0, columnspan=3, sticky='w,e')

    # Process Selection

    self.avgCheckbutton = tk.Checkbutton(self.processFrame,
        text = 'Moving Average',
        variable = self.avgCheck,
        onvalue = 1,
        offvalue = 0,
        command = self.avgcheckbutton_click
        )
    self.avgCheckbutton.grid(row=0, column=0, sticky='w')

    self.irCheckbutton = tk.Checkbutton(self.processFrame,
        text = 'Impulse Removal',
        variable = self.irCheck,
        onvalue = 1,
        offvalue = 0,
        command = self.ircheckbutton_click
        )
    self.irCheckbutton.grid(row=1, column=0, sticky='w')
    # self.irCheckbutton.config(state=tk.DISABLED)
    self.irLabel = tk.Label(self.processFrame, text='Taps:')
    self.irLabel.grid(row=1, column=1)
    self.irTapEntry = tk.Entry(self.processFrame, relief=tk.RIDGE, width=10)
    self.irTapEntry.insert(0, '5')
    self.irTapEntry.grid(row=1, column=2, sticky='e')
    self.irTapEntry.config(state=tk.DISABLED)

    self.dcrCheckbutton = tk.Checkbutton(self.processFrame,
        text = 'DC Removal',
        variable = self.dcrCheck,
        onvalue = 1,
        offvalue = 0,
        command = self.dcrcheckbutton_click
        )
    self.dcrCheckbutton.grid(row=2, column=0, sticky='w')
    # self.dcrCheckbutton.config(state=tk.DISABLED)
    # self.dcrLabel = tk.Label(self.processFrame, text='Taps:')
    # self.dcrLabel.grid(row=2, column=1)
    # self.dcrTapEntry = tk.Entry(self.processFrame, relief=tk.RIDGE, width=10)
    # self.dcrTapEntry.insert(0, '5')
    # self.dcrTapEntry.grid(row=2, column=2, sticky='e')
    # self.dcrTapEntry.config(state=tk.DISABLED)

    self.envCheckbutton = tk.Checkbutton(self.processFrame,
        text = 'Envelop Extraction',
        variable = self.envCheck,
        onvalue = 1,
        offvalue = 0,
        command = self.envcheckbutton_click
        )
    self.envCheckbutton.grid(row=3, column=0, sticky='w')
    # self.envCheckbutton.config(state=tk.DISABLED)
    # self.envLabel = tk.Label(self.processFrame, text='Taps:')
    # self.envLabel.grid(row=3, column=1)
    # self.envTapEntry = tk.Entry(self.processFrame, relief=tk.RIDGE, width=10)
    # self.envTapEntry.insert(0, '5')
    # self.envTapEntry.grid(row=3, column=2, sticky='e')
    # self.envTapEntry.config(state=tk.DISABLED)

  def rf_scale_click(self, v):
      if self.s is not None:
        command = "AT+FREQ={:0>4d}".format(v)
        self.s.write(command.encode('utf-8'))
        line = self.s.read(2)
        if line is 'OK':
            tk.messagebox.showerror("Error", "Parameter set failed.")
        else:
            tk.messagebox.showinfo("Success", "Parameter set successful!")
  def power_scale_click(self, v):
      if self.s is not None:
        command = "AT+PA={:0>4d}".format(v)
        self.s.write(command.encode('utf-8'))
  def gain_scale_click(self,v):
      if self.s is not None:
        command = "AT+REVGAIN={:0>4d}".format(v)
        self.s.write(command.encode('utf-8'))
  def delay_scale_click(self, v):
      if self.s is not None:
        command = "AT+DELAY={:0>4d}".format(v)
        self.s.write(command.encode('utf-8'))
  def avgcheckbutton_click(self):
      self.irCheckbutton.deselect()
      self.dcrCheckbutton.deselect()
      self.envCheckbutton.deselect()
      if(self.avgCheck.get()):
          self.avgCheckbutton.select()
      else:
        self.avgCheckbutton.deselect()

  def ircheckbutton_click(self, plotObject):
      self.dcrCheckbutton.deselect()
      self.envCheckbutton.deselect()
      self.avgCheckbutton.deselect()
      self.irCheckbutton.select()
      if(self.irCheck.get()):
          self.irCheckbutton.select()
      else:
        self.irCheckbutton.deselect()

  def dcrcheckbutton_click(self):
      self.irCheckbutton.deselect()
      self.envCheckbutton.deselect()
      self.avgCheckbutton.deselect()
      if(self.dcrCheck.get()):
          self.dcrCheckbutton.select()
      else:
        self.dcrCheckbutton.deselect()

  def envcheckbutton_click(self):
      self.irCheckbutton.deselect()
      self.dcrCheckbutton.deselect()
      self.avgCheckbutton.deselect()
      if(self.envCheck.get()):
          self.envCheckbutton.select()
      else:
        self.envCheckbutton.deselect()

  def __init__(self, master=None):
    tk.Frame.__init__(self,master)
    self.appPlot = GUIPlot(size=500)
    self.master = master
    self.define_var()
    self.create_widgets(self.appPlot)


class GUIPlot:
    # constructor
    def __init__(self, size):
        self.drawArea = plt.figure()
        self.ax = plt.axes(ylim=(0, 2000))
        self.ax.axvline(linewidth=4, color='r', x=250)
        self.arr = np.zeros(size)
        self.a0, = self.ax.plot(range(500), self.arr)
        self.avg = 0;
        self.dcavg = 0;
        self.env_avg = 0;
        self.base = 0;

    # update plot
    def update(self, frameNum, ser, checkButtons, a0):
        try:
            line = ser.read(300)
            try:
                data = [int(x, 16) for x in re.findall(' (?!f)\w{4}', line.decode('utf-8'))]
                # print(data)
                # self.arr = np.append(self.arr[len(data):], data)
                new_data = data[-1]

                if(checkButtons[0].get()):
                    self.avg = movingAverage(self.arr[250], 0.2, self.avg)
                    self.arr = np.concatenate((self.arr[1:250], self.avg, self.arr[251:], new_data), axis=None)
                elif(checkButtons[1].get()):
                    pass
                elif(checkButtons[2].get()):
                    self.base, self.dcavg = dcRemoval(self.arr[250], 0.7, self.dcavg)
                    self.arr = np.concatenate((self.arr[1:250], self.base, self.arr[251:], new_data), axis=None)
                elif(checkButtons[3].get()):
                    self.dcavg, self.env_avg = envelopExtract(self.arr[250], 0.2, 0.7, self.dcavg, self.env_avg)
                    self.arr = np.concatenate((self.arr[1:250], self.env_avg, self.arr[251:], new_data), axis=None)
                else:
                    self.arr = np.concatenate((self.arr[1:], new_data), axis=None)

                self.a0.set_ydata(self.arr)

            except Exception:
                pass
        except KeyboardInterrupt:
            print('exiting..')
        return self.a0,

if __name__ == '__main__':
  root = tk.Tk()
  root.title('Maxustech Sensing GUI')
  app = SensingGUI(master=root)

  def on_close():
    try:
      app.app_quit()
    except Exception:
      print("Exiting...")
      app.app_quit()

  root.protocol("WM_DELETE_WINDOW", on_close)
  app.mainloop()
