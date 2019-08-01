# IQcut scissors tool
## What is IQcut ?
IQcut is a tool that helps you to manipulate raw file, especially IQ file and extract data by giving timing informations as start, end or duration. You can use inspectrum tool to get the timing information.

![Easy Peasy Lemon Squeezy](https://github.com/cdeletre/iqcut/raw/master/pics/easypeasylemonsqueezy.jpg)

## IQ file format
IQcut can auto-detect GQRX IQ file capture parameters like the samplerate based on the filename. When auto-detection is not available you need to provide the I+Q sample size and the sample rate with *-R* and *-S* parameters. Use the program help *-h* to get more informations.

## Giving the time indicators
IQcut takes whatever start, end or duration time you want to give and try to answer with the best offer according to the IQ file total duration.
Giving both *start* **and** *end* **and** *duration* time will result in ignoring the duration time. Sorry you have to deal with it.
When no duration and end time is given IQcut considers the end of the file.

Time indicators are given with *-s*, *-e* and *-d*. By default, IQcut uses second but you can use millisecond. Use the program help *-h* to get more information.

## File size limit
A limit of 100 MB for the resulting file is applied for safety on small systems like raspberry. However, it can be bypassed with *-f* option or more permanently with the *MAX_FILESIZE* constant in the script.

When the limit is detected, IQcut suggests you to use a dd command. In the current version, the dd command is not optimized as the block size may be low depending on the IQ file sample rate.

## Exemple
### With auto-detection
Let's say we have a GQRX file `gqrx_20180313_160552_27120000_240000_fc.raw` and we want to extract 7 ms of data starting at 3 ms. We just have to use the following command:

```bash
$ ./iqcut.py  -a -s 3m -d 7m gqrx_20180313_160552_27120000_240000_fc.raw
Supported GQRX file found
Detected I+Q sample rate: 240000 sps
Detected I+Q sample size: 8 B
IQ file size: 646 kB
IQ file bitrate: 1875 kB/s
IQ file duration: 345 ms
7 ms of data (13 kB) will be copied
Data copied to gqrx_20180313_160552_27120000_240000_fc_CUT_3-10ms.raw
```
### Without auto-detection
The same operation but without auto-detection:

```bash
$ ./iqcut.py -S 8 -R 240000 -s 3m -d 7m gqrx_20180313_160552_27120000_240000_fc.raw
IQ file size: 646 kB
IQ file bitrate: 1875 kB/s
IQ file duration: 345 ms
7 ms of data (13 kB) will be copied
Data copied to gqrx_20180313_160552_27120000_240000_fc_CUT_3-10ms.raw
```