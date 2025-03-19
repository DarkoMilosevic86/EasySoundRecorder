# Copyright (C) 2024-2025 Darko Milošević
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.


import os
import sys
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
import tones
import time


def cut (data, start=None, end=None):
	ct = data[start:end]
	return np.delete(data, slice(start, end)), ct

def mix (data1, data2):
	chunk1 = np.frombuffer(data1, dtype=np.int16)
	chunk2 = np.frombuffer(data2, dtype=np.int16)
	min_len = min(len(chunk1), len(chunk2))
	chunk1, _ = cut(chunk1, min_len, None)
	chunk2, _ = cut(chunk2, min_len, None)
	mixed_data = (chunk1+chunk2)//2
	return mixed_data.tobytes()


class WasapiSoundRecorder:
	def __init__(self, recording_format, recording_folder, output_device, input_device, beep):
		self.recording_folder = recording_folder
		self.recording_format = recording_format
		self.output_device = output_device
		self.input_device = input_device
		self.beep = beep
		self.audio_interface = pyaudio.PyAudio()
		self.recording = 0
		self.stream_mic = None
		self.stream_card = None
		if self.output_device == 0:
			self.default_speakers = self.get_default_loopback_speakers()
		else:
			self.default_speakers = self.audio_interface.get_device_info_by_index(self.output_device)
		if self.input_device == 0:
			self.default_mic = self.get_default_loopback_mic()
		else:
			self.default_mic = self.audio_interface.get_device_info_by_index(self.input_device)
		self.speakers_samplerate = int(self.default_speakers["defaultSampleRate"])
		self.mic_samplerate = int(self.default_mic["defaultSampleRate"])
		self.speakers_channels= self.default_speakers["maxInputChannels"]
		self.mic_channels = self.default_mic["maxInputChannels"]
		self.speakers_chunk = 8192
		self.mic_chunk = 8192
		self.frames = []

	def resample_audio_data(self, data_buffer, channels, in_rate, out_rate):
		state = None
		converted_audio, _ = audioop.ratecv(data_buffer, 2, channels, in_rate, out_rate, None)
		return converted_audio

	def mono_to_stereo(self, data):
		stereo = audioop.tostereo(data, 2, 1, 1)
		return stereo

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
			return self.audio_interface.get_default_input_device_info()
		except:
			raise RuntimeError("Cannot find default microphone.")

	def start_recording(self):
		try:
			self.recording = 1
			self.stream_card = self.audio_interface.open(
				format=pyaudio.paInt16,
				channels=self.speakers_channels,
				rate=self.speakers_samplerate,
				input=True,
				input_device_index=self.default_speakers["index"],
				frames_per_buffer=self.speakers_chunk
			)
			self.stream_mic = self.audio_interface.open(
				format=pyaudio.paInt16,
				channels=self.mic_channels,
				rate=self.mic_samplerate,
				input=True,
				input_device_index=self.default_mic["index"],
				frames_per_buffer=self.mic_chunk
			)
			self.frames = []
			threading.Thread(target=self.collect_data).start()
		except Exception as e:
			self.recording = 0
			raise RuntimeError(f"Failed to start recording: {e}")

	def collect_data(self):
		while self.recording == 1:
			speaker_data = self.stream_card.read(8192, exception_on_overflow=False)
			mic_data = self.stream_mic.read(8192, exception_on_overflow=False)
			if not self.mic_samplerate == self.speakers_samplerate:
				mic_data = self.resample_audio_data(mic_data, 1, self.mic_samplerate, self.speakers_samplerate)
			if self.mic_channels == 1:
				mic_data = self.mono_to_stereo(mic_data)
			self.frames.append(mix(speaker_data, mic_data))

	def pause_recording(self):
		try:
			self.recording = 2
			time.sleep(0.1)
			self.stream_card.stop_stream()
			self.stream_card.close()
			time.sleep(0.1)
			self.stream_card = None
			self.stream_mic.stop_stream()
			self.stream_mic.close()
			time.sleep(0.1)
			self.stream_mic = None
		except Exception as e:
			raise RuntimeError(f"Error while pausing recording {e}")

	def resume_recording(self):
		try:
			self.stream_card = self.audio_interface.open(
				format=pyaudio.paInt16,
				channels=self.speakers_channels,
				rate=self.speakers_samplerate,
				input=True,
				input_device_index=self.default_speakers["index"],
				frames_per_buffer=self.speakers_chunk
			)
			time.sleep(0.1)
			self.stream_mic = self.audio_interface.open(
				format=pyaudio.paInt16,
				channels=self.mic_channels,
				rate=self.mic_samplerate,
				input=True,
				input_device_index=self.default_mic["index"],
				frames_per_buffer=self.mic_chunk
			)
			time.sleep(0.1)
			self.recording = 1
			time.sleep(0.1)
			threading.Thread(target=self.collect_data).start()
		except Exception as e:
			raise RuntimeError(f"Error while resuming recording {e}")

	def stop_recording(self):
		try:
			self.recording = 0
			if self.stream_mic is not None:
				self.stream_mic.stop_stream()
				self.stream_mic.close()
			time.sleep(0.1)
			if self.stream_card is not None:
				self.stream_card.stop_stream()
				self.stream_card.close()
			time.sleep(0.1)
			self.audio_interface.terminate()
			time.sleep(0.1)
			threading.Thread(target=self.write_and_save_data).start()
		except Exception as e:
			raise RuntimeError(f"Failed to stop recording: {e}")

# Writing and saving data definition
	def write_and_save_data(self):
		try:
			if self.frames:
				timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
				if not os.path.exists(self.recording_folder):
					# Creates the recording folder if not exists
					os.makedirs(self.recording_folder)
				recording_formats = ["wav", "mp3"]
				output_file = os.path.join(self.recording_folder, f"recording_{timestamp}.{recording_formats[self.recording_format]}")
				if self.recording_format == 0:
					with wave.open(output_file, "wb") as wf:
						wf.setnchannels(self.default_speakers["maxInputChannels"])
						wf.setsampwidth(self.audio_interface.get_sample_size(pyaudio.paInt16))
						wf.setframerate(self.speakers_samplerate)
						wf.writeframes(b"".join(self.frames))
				elif self.recording_format == 1:
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
				time.sleep(0.1)
				if self.beep:
					tones.beep(400, 500)
					tones.beep(800, 400)
		except Exception as e:
			raise RuntimeError(f"Error while saving recording ({e})")

	def reset(self):
		self.frames = None
		self.frames = []
		self.re_initialize_devices()

# Device re initialization definition
	def re_initialize_devices(self):
		if self.audio_interface:
			self.audio_interface.terminate()
		self.audio_interface = pyaudio.PyAudio()

	def terminate(self):
		self.audio_interface.terminate()
		super().terminate()
