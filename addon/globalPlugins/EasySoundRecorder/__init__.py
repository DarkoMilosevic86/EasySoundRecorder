# -*- coding: UTF-8 -*-

# Copyright (C) 2024-2025 Darko Milošević
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

import sys
from globalPluginHandler import GlobalPlugin
import gui.guiHelper
import ui
from scriptHandler import script
from .devices import Devices
import addonHandler
from .recorder import WasapiSoundRecorder
import os
import config
import configobj
from configobj import validate
import gui
import wx
from logHandler import log
from io import StringIO, BytesIO

addonHandler.initTranslation()

recorder = None
_config = None
conf_file = "EasySoundRecorder.ini"
rec_folder = os.path.join(os.environ['USERPROFILE'], 'Documents', 'Easy Sound Recorder')
configspec = StringIO("""
					[Settings]
					recording_format = integer(default = 0)
					  recording_folder = string(default = {rec_folder})
					  input_device = integer(default=0)
					  output_device = integer(default=0)
					  beep = boolean(default=True)
					  """.format(rec_folder=rec_folder))

def get_config():
	global _config
	if not _config:
		config_path = os.path.join(config.getUserDefaultConfigPath(), conf_file)
		_config = configobj.ConfigObj(config_path, configspec=configspec)
		val = validate.Validator()
		_config.validate(val)
	return _config


class SettingsDialog(gui.SettingsDialog):
	# Translators: Settings dialog title
	title=_("Easy Sound Recorder settings")

	def on_browse_recording_folder_button(self, event):
		# Translators: Browse for folder dialog caption
		with wx.DirDialog(
			self, 
			_("Select folder for recordings"), 
			defaultPath=self.recording_folder.GetValue(), 
			style=wx.DD_DEFAULT_STYLE
		) as dialog:
			if dialog.ShowModal() == wx.ID_OK:
				self.recording_folder.SetValue(dialog.GetPath())

	def makeSettings(self, sizer):
		self.devices = Devices()
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)
		self.conf = get_config()
		# Translators: Select speakers label
		self.output_device = settingsSizerHelper.addLabeledControl(_("Select output device for recording"), wx.Choice, choices=self.devices.get_loopback_speakers_names())
		self.output_device.SetSelection(0)
		# Translators: Label for selecting input device
		self.input_devices = settingsSizerHelper.addLabeledControl(_("Select input device for recording"), wx.Choice, choices=self.devices.get_input_devices_names())
		self.input_devices.SetSelection(0)
		choices = ["wav", "mp3"]
		# Translators: Recording formats
		self.recording_formats = settingsSizerHelper.addLabeledControl(_("Please specify the recording format (wav or mp3)"), wx.Choice, choices=choices)
		self.recording_formats.SetSelection(0)
		# Translators: Recording folder label
		self.recording_folder = settingsSizerHelper.addLabeledControl(_("Please specify a folder where recordings will be saved"), wx.TextCtrl)
		self.recording_folder.SetValue(self.conf["Settings"]["recording_folder"])
		# Translators: Browse recording folder button
		self.browse_recording_folder_button = wx.Button(self, label=_("Browse..."))
		self.browse_recording_folder_button.Bind(wx.EVT_BUTTON, self.on_browse_recording_folder_button)
		settingsSizerHelper.addItem(self.browse_recording_folder_button)
		# Translators: Beep when recording has saved checkbox value
		self.beep = wx.CheckBox(self, label=_("Beep when recording has saved"))
		self.beep.SetValue(self.conf["Settings"]["beep"])
		settingsSizerHelper.addItem(self.beep)

	def postInit(self):
		self.output_device.SetFocus()

	def onOk(self, event):
		self.conf["Settings"]["recording_format"] = self.recording_formats.GetSelection()
		self.conf["Settings"]["recording_folder"] = self.recording_folder.GetValue()
		self.conf["Settings"]["output_device"] = self.devices.get_loopback_speakers_indexes()[self.output_device.GetSelection()]
		self.conf["Settings"]["input_device"] = self.devices.get_input_devices_indexes()[self.input_devices.GetSelection()]
		self.conf["Settings"]["beep"] = self.beep.GetValue()
		try:
			self.conf.write()
		except IOError:
			log.error("Error writing Easy Sound Recorder configuration", exc_info=True)
			# Translators: Error saving configuration message
			gui.messageBox(e.strerror, _("Error while saving Easy Sound Recorder configuration."), style=wx.OK | wx.ICON_ERROR)
		super(SettingsDialog, self).onOk(event)

class GlobalPlugin(GlobalPlugin):
	def _initialize_recorder(self):
		global recorder
		if recorder:
			recorder = None
		recorder = WasapiSoundRecorder(
			recording_format=self.conf["Settings"]["recording_format"],
			recording_folder=self.conf["Settings"]["recording_folder"],
			output_device=self.conf["Settings"]["output_device"],
			input_device=self.conf["Settings"]["input_device"],
			beep=self.conf["Settings"]["beep"])

	def __init__(self):
		super().__init__()
		self.WasapiSoundRecorderSettingsItem = gui.mainFrame.sysTrayIcon.preferencesMenu.Append(wx.ID_ANY, _("Easy Sound Recorder settings..."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, lambda evt: gui.mainFrame._popupSettingsDialog(SettingsDialog), self.WasapiSoundRecorderSettingsItem)
		self.conf = get_config()
		global recorder
		recorder = WasapiSoundRecorder(self.conf["Settings"]["recording_format"], self.conf["Settings"]["recording_folder"], self.conf["Settings"]["output_device"], self.conf["Settings"]["input_device"], self.conf["Settings"]["beep"])

	@script(
		description=_("Starts, pauses and resumes recording"),
		gesture="kb:Shift+NVDA+R"
	)
	def script_startRecording(self, gesture):
		if recorder.recording == 1:
			recorder.pause_recording()
			ui.message(_("Recording paused"))
		elif recorder.recording == 2:
			ui.message(_("Recording resumed"))
			recorder.resume_recording()
		else:
			self._initialize_recorder()
			ui.message(_("Recording started"))
			recorder.start_recording()

	@script(
		description=_("Stops recording and saves the audio file using specifyed format."),
		gesture="kb:Shift+NVDA+T"
	)
	def script_stopRecording(self, gesture):
		if recorder.recording == 1 or recorder.recording == 2:
			recorder.stop_recording()
			ui.message(_("Recording stopped"))
		else:
			ui.message(_("No recording is in progress."))

	def reset(self):
		self._initialize_recorder()

	def terminate(self):
		try:
			gui.mainFrame.sysTrayIcon.preferencesMenu.RemoveItem(self.WasapiSoundRecorderSettingsItem)
		except:
			pass
		self.recorder = None
		self.conf = None
		super().terminate()
