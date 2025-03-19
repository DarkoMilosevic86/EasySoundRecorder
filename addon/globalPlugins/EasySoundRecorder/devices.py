# Copyright (C) 2024-2025 Darko Milošević
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.


import sys
import os
module_path = os.path.dirname(__file__)
if module_path not in sys.path:
	sys.path.append(module_path)
import pyaudiowpatch as pyaudio

class Devices:
	def __init__(self):
		super().__init__()
		self.AudioInterface = pyaudio.PyAudio()
		self.wasapi = pyaudio.paWASAPI

	def terminate(self):
		self.AudioInterface.terminate()
		super().terminate()

	def get_loopback_speakers_names(self):
		try:
			wasapi_devices = self.AudioInterface.get_host_api_info_by_type(self.wasapi)
		except:
			raise OSError('No WASAPI devices in your system.')
		speakers = []
		for I in range(wasapi_devices["deviceCount"]):
			device_info = self.AudioInterface.get_device_info_by_host_api_device_index(wasapi_devices["index"], I)
			if device_info["isLoopbackDevice"]:
				device_name = device_info["name"]
				speakers.append(device_name)
		return speakers

	def get_loopback_speakers_indexes(self):
		try:
			wasapi_devices = self.AudioInterface.get_host_api_info_by_type(self.wasapi)
		except:
			raise OSError('No WASAPI devices in your system.')
		speaker_indexes = []
		for I in range(wasapi_devices["deviceCount"]):
			device_info = self.AudioInterface.get_device_info_by_host_api_device_index(wasapi_devices["index"], I)
			if device_info["isLoopbackDevice"]:
				device_index = device_info["index"]
				speaker_indexes.append(device_index)
		return speaker_indexes

	def get_input_devices_names(self):
		input_devices = []
		for I in range(self.AudioInterface.get_device_count()):
			device_info = self.AudioInterface.get_device_info_by_index(I)
			if not device_info["isLoopbackDevice"] and not device_info["maxOutputChannels"] > 0:
				device_name = device_info["name"]
				input_devices.append(device_name)
		return input_devices

	def get_input_devices_indexes(self):
		input_devices_indexes = []
		for I in range(self.AudioInterface.get_device_count()):
			device_info = self.AudioInterface.get_device_info_by_index(I)
			if not device_info["isLoopbackDevice"] and not device_info["maxOutputChannels"] > 0:
				device_index = device_info["index"]
				input_devices_indexes.append(device_index)
		return input_devices_indexes
