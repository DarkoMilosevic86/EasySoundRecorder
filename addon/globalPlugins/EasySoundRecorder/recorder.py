# Copyright (C) 2024 Darko Milošević
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.


import os
import sys
""" Now we need to expand the current globalPlugins\EasySoundRecorder folder.
We are doing so because some necesary libraries as part of the plugin."""
module_path = os.path.dirname(__file__)
if module_path not in sys.path:
	sys.path.append(module_path)
import wave
import numpy as np
from datetime import datetime
import pyaudiowpatch as pyaudio
from pydub import AudioSegment
from pydub.utils import audioop
import threading
import time

class WasapiSoundRecorder:
	def __init__(self, recording_format="wav", recording_folder=os.path.join(os.environ['USERPROFILE'], "Documents", "Easy Sound Recorder")):
		self.recording_folder = recording_folder
		self.recording_format = recording_format
		self.audio_interface = pyaudio.PyAudio()
		self.recording = 0
		self.stream_mic = None
		self.stream_speakers = None
		self.default_speakers = self.get_default_loopback_speakers()
		self.default_mic = self.get_default_loopback_mic()
		self.speakers_samplerate = int(self.default_speakers["defaultSampleRate"])
		self.mic_samplerate = int(self.default_mic["defaultSampleRate"])
		# self.mic_data and self.speaker_data are byte arrays for storing the recording data for boath streams
		self.speaker_data = []
		self.mic_data = []
		self.frames = []

# Function for resampling audio data
	def resample_audio_data(self, data_buffer, channels, in_rate, out_rate):
		state = None
		converted_audio, _ = audioop.ratecv(data_buffer, 2, channels, in_rate, out_rate, state)
		expected_len = int(len(data_buffer) * (out_rate / in_rate))
		if len(converted_audio) < expected_len:
			converted_audio += b"\x00" * (expected_len - len(converted_audio))
		elif len(converted_audio) > expected_len:
			converted_audio = converted_audio[:expected_len]
		return converted_audio

# Function definition for combining speakers and microphone streams together
	def write_audio_data(self):
		for i in range(min(len(self.speaker_data), len(self.mic_data))):
			speaker_chunk = self.speaker_data[i]
			mic_chunk = self.mic_data[i]
			if len(mic_chunk) < len(speaker_chunk):
				mic_chunk += b"\x00" * (len(speaker_chunk) - len(mic_chunk))
			elif len(mic_chunk) > len(speaker_chunk):
				speaker_chunk += b"\x00" * (len(mic_chunk) - len(speaker_chunk))
			speaker_array = np.frombuffer(speaker_chunk, dtype=np.int16)
			mic_array = np.frombuffer(mic_chunk, dtype=np.int16)
			combined_array = speaker_array.astype(np.int32) + mic_array.astype(np.int32)
			combined_array = np.clip(combined_array, -32768, 32767).astype(np.int16)
			self.frames.append(combined_array.tobytes())

	def write_test(self):
		for i in range(min(len(self.speaker_data), len(self.mic_data))):
			speaker_chunk = self.speaker_data[i]
			mic_chunk = self.mic_data[i]
			comb_data = speaker_chunk * mic_chunk
			self.frames.append(comb_data)

# Speakers and microphone callbacks
	def speakers_callback(self, in_data, frame_count, time_info, status):
		# Appending self.speaker_data array while recording
		self.speaker_data.append(in_data)
		return (in_data, pyaudio.paContinue)

	def mic_callback(self, in_data, frame_count, time_info, status):
		# Resampling microphone if sample rate is not equal to sound cards sample rate
		if not self.mic_samplerate == self.speakers_samplerate:
			in_data = self.resample_audio_data(in_data, self.default_mic["maxInputChannels"], self.mic_samplerate, self.speakers_samplerate)
		# Appending self.mic_data array while recording
		self.mic_data.append(in_data)
		return (in_data, pyaudio.paContinue)

# Getting the default speakers as WASAPI loopback device
	def get_default_loopback_speakers(self):
		try:
			wasapi_device = self.audio_interface.get_host_api_info_by_type(pyaudio.paWASAPI)
		except Exception as e:
			raise RuntimeError(f"Error. ({e})")
		device = self.audio_interface.get_device_info_by_index(wasapi_device["defaultOutputDevice"])
		if not device["isLoopbackDevice"]:
			for loopback in self.audio_interface.get_loopback_device_info_generator():
				if device["name"] in loopback["name"]:
					device = loopback
					break
		return device

# Getting the default loopback microphone
	def get_default_loopback_mic(self):
		try:
			wasapi_device = self.audio_interface.get_host_api_info_by_type(pyaudio.paWASAPI)
		except Exception as e:
			raise RuntimeError(f"Error. ({e})")
		device = self.audio_interface.get_device_info_by_index(wasapi_device["defaultInputDevice"])
		if not device["isLoopbackDevice"]:
			for loopback in self.audio_interface.get_loopback_device_info_generator():
				if device["name"] in loopback["name"]:
					device = loopback
					break
		return device

# Start recording definition
	def start_recording(self):
		try:
			self.recording = 1
			""" Re initializing devices each time when start recording.
			This will prevent crashes if the default speakers has changed.
			For example, if someone turns off a bluetooth speakers. """
			self.re_initialize_devices()
			# Opening speakers and microphone streams for recording
			self.stream_card = self.audio_interface.open(
				format=pyaudio.paInt16,
				channels=self.default_speakers["maxInputChannels"],
				rate=self.speakers_samplerate,
				input=True,
				input_device_index=self.default_speakers["index"],
				frames_per_buffer=4096,
				stream_callback=self.speakers_callback
			)
			time.sleep(0.01)
			self.stream_mic = self.audio_interface.open(
				format=pyaudio.paInt16,
				channels=self.default_mic["maxInputChannels"],
				rate=self.mic_samplerate,
				input=True,
				input_device_index=self.default_mic["index"],
				frames_per_buffer=4096,
				stream_callback=self.mic_callback
			)
			# Initializing self.frames with empty value
			self.frames = []
		except Exception as e:
			self.recording = False
			raise RuntimeError(f"Failed to start recording: {e}")

# Definition for pause recording
	def pause_recording(self):
		try:
			self.recording = 2
			self.stream_card.stop_stream()
			self.stream_mic.stop_stream()
		except Exception as e:
			raise RuntimeError(f"Error while pausing recording {e}")

# Definition for resuming recording
	def resume_recording(self):
		try:
			self.recording = 1
			self.stream_card.start_stream()
			time.sleep(0.01)
			self.stream_mic.start_stream()
		except Exception as e:
			raise RuntimeError(f"Error while resuming recording {e}")

# Definition for stop recording
	def stop_recording(self):
		try:
			self.recording = 0
			#Closes boath streams and terminates the self.audio_interface
			if self.stream_mic is not None:
				self.stream_mic.stop_stream()
				self.stream_mic.close()
			if self.stream_card is not None:
				self.stream_card.stop_stream()
				self.stream_card.close()
			self.audio_interface.terminate()
			""" Writes the audio data and saves to the specifyed file in the separate thread.
			This will prevent freezing NVDA while saving the audio file. """
			threading.Thread(target=self.write_and_save_data).start()
		except Exception as e:
			raise RuntimeError(f"Failed to stop recording: {e}")

# Writing and saving data definition
	def write_and_save_data(self):
		try:
			self.write_test()
			if self.frames:
				# Defines the path of the audio file
				timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
				if not os.path.exists(self.recording_folder):
					# Creates the recording folder if not exists
					os.makedirs(self.recording_folder)
				output_file = os.path.join(self.recording_folder, f"recording_{timestamp}.{self.recording_format}")
				if self.recording_format == "wav":
					with wave.open(output_file, "wb") as wf:
						wf.setnchannels(self.default_speakers["maxInputChannels"])
						wf.setsampwidth(self.audio_interface.get_sample_size(pyaudio.paInt16))
						wf.setframerate(self.speakers_samplerate)
						wf.writeframes(b"".join(self.frames))
				elif self.recording_format == "mp3":
					# Uses the AudioSegment from pydub to convert the audio file to the .mp3 format
					AudioSegment.converter = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
					audio_data = AudioSegment(
						data=b"".join(self.frames),
						sample_width=self.audio_interface.get_sample_size(pyaudio.paInt16),
						frame_rate=self.speakers_samplerate,
						channels=self.default_speakers["maxInputChannels"]
					)
					audio_data.export(output_file, format="mp3")
				else:
					raise ValueError("Unsupported format. Only 'wav' is currently supported.")
		except Exception as e:
			raise RuntimeError(f"Error while saving recording ({e})")

# Restoring the all necesary members to it's original values, and re initializes devices
	def reset(self):
		self.frames = None
		self.frames = []
		self.speaker_data = None
		self.speaker_data = []
		self.mic_data = None
		self.mic_data = []
		self.re_initialize_devices()

# Device re initialization definition
	def re_initialize_devices(self):
		self.default_mic = None
		self.default_speakers = None
		self.mic_samplerate = None
		self.speakers_samplerate = None
		if self.audio_interface:
			self.audio_interface.terminate()
		self.audio_interface = pyaudio.PyAudio()
		self.default_speakers = self.get_default_loopback_speakers()
		self.default_mic = self.get_default_loopback_mic()
		self.speakers_samplerate = int(self.default_speakers["defaultSampleRate"])
		self.mic_samplerate = int(self.default_mic["defaultSampleRate"])

	def terminate(self):
		self.audio_interface.terminate()
		super().terminate()
