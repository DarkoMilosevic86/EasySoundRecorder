# Easy Sound Recorder
Easy Sound Recorder allows recording audio from both the sound card and microphone simultaneously using WASAPI.
This add-on utilizes the currently active sound card or Bluetooth headset, as well as the active microphone, and enables recording in either WAV or MP3 format.

# Installation
You can install Easy Sound Recorder in two ways:

* Using the add-on store,
* Downloading the latest version of the add-on from the page  
  [https://github.com/DarkoMilosevic86/EasySoundRecorder/releases](https://github.com/DarkoMilosevic86/EasySoundRecorder/releases)

# Usage
Using Easy Sound Recorder is very simple with just two commands:

* **Shift+NVDA+R** – Starts recording, pauses, and resumes recording,
* **Shift+NVDA+T** – Stops recording and saves the recording as a `.wav` or `.mp3` file, depending on the settings.

# Important notes

* After you turn off your bluetooth speakers, if recording do not starts, it is necesary to restart your NVDA to re initialize the default output device.
* If you hear microphone clipping in recordings, please set your microphone format to be the same format as your sound card in the Sound section in the Control Panel.

After installing Easy Sound Recorder, the default folder for saving recordings is:  
`C:\Users\username\Documents\EasySoundRecorder`

For example, if your username is **John**, recordings will be saved in the following location by default:  
`C:\Users\john\Documents\EasySoundRecorder`

By default, the format for saved recordings upon installation is WAV.  
You can change the recording format and the save folder in the Easy Sound Recorder settings as follows:

1. Press **NVDA+N** to open the NVDA menu,
2. Press the **Down Arrow** until you hear **Options**,
3. Press the **Right Arrow**,
4. Press the **Down Arrow** until you hear **Easy Sound Recorder Settings...**,
5. Press **Enter**, and the Easy Sound Recorder settings dialog will appear.

In this dialog, you can configure the recording format:

* WAV
* MP3  

Additionally, you can set the folder where recordings will be saved.  
You can either manually enter the folder name or press the **Browse...** button to select the desired folder.

Also, you can configure your input and output device for recording, meanning your speakers and microphone.
When you use the Easy Sound Recorder for the first time, it will use your default speakers and microphone.
Additionally, you can configure beep when recording has been saved using Beep checkbox in the settings dialog, and you will here beep sound when you finish recording.

## Important Note
If the folder where recordings should be saved does not exist, it will be created upon the first recording.

# For Developers
If you want to contribute to the development of Easy Sound Recorder, you can do so as follows:

* Clone the GitHub repository using the following command:  
  ```bash
  git clone https://github.com/DarkoMilosevic86/EasySoundRecorder.git
* Fork this repository and make the necessary changes, whether it’s adding localization or modifying the code,
* Create a pull request to merge your changes into the main repository.

# Reporting Issues
If you encounter any issues while using Easy Sound Recorder, open a discussion on the following page:

[https://github.com/DarkoMilosevic86/EasySoundRecorder/issues](https://github.com/DarkoMilosevic86/EasySoundRecorder/issues)
