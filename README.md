# MWTool for mw series radar

This repo is a debug tool for developers to visualize the raw data of Maxustech mw series radar. MW series radar is a highly integrated signle chip motion sensor.

## Usage

### Python (Only tested on v3.7.4)

> Dependencies:
>
> - Matplotlib
> - Numpy
> - Tkinter

``` python
python mw0582_gui.py
```

![Xnip2019-12-05_19-17-28.png](https://i.loli.net/2019/12/05/NFYnSeI4XfypODc.png)

#### Note:

- Impulse removal algorithm is yet to finish
- RF setting is not available at in this version

### Node

> Dependencies:
>
> - serialport

- Install Node v8.9.1 and above
- Run `npm install` to install the project dependencies specified in `package.json`
- Run `node mwSerial.js <portName>` to capture the raw data output

### Other serial tools

Recommended serial tools include:

- **Baudrate at 512000**
- For mac, `coolterm`is recommended. To change the baudrate simply goto **"Option-Serial Port-Baudrate(Custom)"**
  ![Change the baudrate](https://i.loli.net/2020/01/06/tOy9frKPDdCE4Al.png)
- For windows, `taraterm` will be a nice choice

#### Debug commands

1. Radiated Power`AT+PA=x`

   with x ranges from 0000~0007 (default is 0001)

2. RX Gain `AT+REVGAIN=x`

   with x ranges from 0000~0007 (default is 0007)

3. Time delay after detection `AT+DELAY=xxxx`

   with xxxx ranges from 0001~3599 (default is 0002, unit is second)

4. Mode selection `AT+DEBUG=x`

   Normal mode when x = 0000 (default); Raw data mode when x = 0002

5. Detect Threshold `AT+THRES=xx`

   with xx ranges from 0001~0099 (default is 0012)

