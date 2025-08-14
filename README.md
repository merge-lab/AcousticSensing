# Acoustic Sensing
Python files and the KiCAD schematic for piezo amplifier are kept here.

Check the IDs for the USB Audio interface inputs/outputs on your machine, you will need to modify IDs accordingly to assign correct devices.
Run the following in the Python terminal to determine the IDs.
```
import sounddevice as sd
sd.query_devices()
```
Example output:
```
   0 Microsoft Sound Mapper - Input, MME (2 in, 0 out)
>  1 Microphone (Creative Live! Audi, MME (4 in, 0 out)
   2 Microphone Array (Intel® Smart , MME (6 in, 0 out)
   3 Microsoft Sound Mapper - Output, MME (0 in, 2 out)
<  4 Speakers (Creative Live! Audio , MME (0 in, 2 out)
   5 Speakers (Realtek(R) Audio), MME (0 in, 2 out)
   6 Primary Sound Capture Driver, Windows DirectSound (2 in, 0 out)
   7 Microphone (Creative Live! Audio A3), Windows DirectSound (4 in, 0 out)
   8 Microphone Array (Intel® Smart Sound Technology for Digital Microphones), Windows DirectSound (6 in, 0 out)
   9 Primary Sound Driver, Windows DirectSound (0 in, 2 out)
```
## Python Code
Runs on Python 3.13

Dependencies:
- matplotlib
- numpy
- sounddevice
- PyQt6
- scipy
- collections
