# Show Me Your Brainwave And I Will Tell You What You Are Doing

In this repo I collect all my projects which is based on brainwaves (EEG data) and other data coming from an EEG headband like gyroscope and acceleration data.

## Required hardware
In order to use this project you will need an Interaxon Muse brain sensing EEG band.

I am using a Muse S, but most probably it will work with any Muse headband as they provide the RAW EEG data the same way.

You can buy the [Muse band in Interaxon's webshop](https://choosemuse.com/muse-s/). At the time of this commit, the price is €379.99 which I think quite generous as in exchange you get access to your brain.

In comparison to the earlier versions, the Muse S has a flexible band so it makes it quite comfortable to wear even during sleeping.

In terms of EEG Muse provides 4 channels FT7, FT8, TP9 and TP10 on 256Hz with 12bits/sample.

It also has gyroscope, accelerometer, PPG and thermistor sensor which opens new horizons for applications.

You can [find more details in the Muse S technical specification](https://images-na.ssl-images-amazon.com/images/I/71A9NwYDx9S.pdf).
I have implemented this project in a way that you can easily add support for other EEG devices too. It might need some tweak, please do not hesitate to open a new issue, and we will support your EEG brain sensor in no time, if it has a public API.

## Required software
Unfortunately, Interaxon does not offer a publicly available API so I use the Mind Monitor app to stream the data on local network via the Open Source Control (OSC) protocol to my local machine. The app is [available for iOs, Android and Amazon](https://mind-monitor.com/#download) for $15. Again I think that is a nobrainer for getting access to our brain.

As very often dollar-euro exchange is done in 1-1 ration on th internet, we can calculate **you can get access to your brain for €395.

Of course there are much more expensive alternatives, but 4 channel is more than adequate for putting our feet on the fascinating field of Brain Computer Interfaces (BCI).

Muse has a non-public SDK for which I have applied, but I did not get any feedback yet. As I am building a web application in python I will only use he SDK if I ca make it work in this environment.

In the long run I am planning to implement a direct implementation of the Muse bluetooth communication, so we won't need one additional program to access the live RAW EEG data.

## Required Python packages
- python-osc
- matplotlib
- scipy
- Kivy

## Setup

1. Turn on your Muse
2. Start Mind Monitor
3. Open Mind Monitor's Settings and set the OSC Stream Target IP to your machine's IP (You can use ipconfig on Windows and ifconfig on Linux and Mac to get it)
4. The program will connect to port 5000, but you can configure the OSC Stream Port also in case it is not right for you.
5. Tap the streaming icon
6. Open the project in your favourite IDE (at the moment mine is IntelliJ IDEA)
7. Start the app which you want to execute.

## Creating Android app
You can find everything on [Kivy's Android packaging page](https://kivy.org/doc/stable/guide/packaging-android.html)
Here are the steps
1. Get Buildozer:
```
git clone https://github.com/kivy/buildozer.git
cd buildozer
```
 If you are a Linux, MacOS user, then you are ready to go. If you are on Windows like me, then WSL (Windows Subsystem for Linux) should be installed. [Click here to learn how to install it on WSL](https://docs.microsoft.com/en-us/windows/wsl/install)!
 You will also need Python installed under your wsl: 
```
sudo apt update
sudo apt upgrade
sudo apt install python3 python3-pip ipython3
```
 
After you installed Python you can setup Buildozer. First, go to Buildozer directory then execute: 
``` 
sudo python3 setup.py install
```    
2. 
3. 

4. [Click here for instructions!](https://medium.com/@rhdzmota/python-development-on-the-windows-subsystem-for-linux-wsl-17a0fa1839d)
5. Generate and upload APK to your connected Android device

## Currently Available Apps
I do believe only our imagination is the limit to use the possibilities which we have in brainwaves. 4 channels is not a lot, but having strict limits boost creativity, so I do believe if we brainstorm together we can come up with amazing ideas.

Do not hesitate to **[contact me](https://www.linkedin.com/in/miki-szeles-freelancer-agileish-creativeishtechnicalish-writer/) if you would like to do a collaborative brainstorming about the possibilities provided by brainwaves.**
### Blinkish To Textish
This app converts eyeblinks detecting using brainwaves to text using the Morse code. The development is still in progress.

I have developed the app mostly lying in the bed, but last time I was sitting in front of a table and realized there is a high frequency, high amplitude artefact on the signal, so a low pass filter has to be implemented in order to make it more stable.
### Eye Movementish To Textish
This app will use your eye movement direction to chose between groups of characters, then you can select a group by blinking. In the second round you can select the exact character in the same way.

I do believe it is possible to make it even more effective by using words instead of characters, but I had no time yet to think about that. In case you have any idea, .
