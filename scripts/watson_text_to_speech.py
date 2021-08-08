# You need to install pyaudio to run this example
# pip install pyaudio

# In this example, the websocket connection is opened with a text
# passed in the request. When the service responds with the synthesized
# audio, the pyaudio would play it in a blocking mode

from ibm_watson import TextToSpeechV1
from ibm_watson.websocket import SynthesizeCallback
import pyaudio
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import logging
import os

logging.disable(logging.CRITICAL)

authenticator = IAMAuthenticator(os.getenv('API_TEXT_TO_SPEECH'))
service = TextToSpeechV1(authenticator=authenticator)
#service.set_service_url('https://api.us-south.text-to-speech.watson.cloud.ibm.com/instances/9572ac68-de44-453e-9e52-906fa128b542')

class Play(object):
    """
    Wrapper to play the audio in a blocking mode
    """
    def __init__(self):
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 22050
        self.chunk = 1024
        self.pyaudio = None
        self.stream = None

    def start_streaming(self):
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self._open_stream()
        self._start_stream()

    def _open_stream(self):
        stream = self.pyaudio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk,
            start=False
        )
        return stream

    def _start_stream(self):
        self.stream.start_stream()

    def write_stream(self, audio_stream):
        self.stream.write(audio_stream)

    def complete_playing(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

class MySynthesizeCallback(SynthesizeCallback):
    def __init__(self):
        SynthesizeCallback.__init__(self)
        self.play = Play()

    def on_connected(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Opening stream to play')
        self.play.start_streaming()

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_timing_information(self, timing_information):
        print(timing_information)

    def on_audio_stream(self, audio_stream):
        self.play.write_stream(audio_stream)

    def on_close(self):
        print('Completed synthesizing')
        self.play.complete_playing()

test_callback = MySynthesizeCallback()

print('DIGITE "sair" para voltar ao menu')
text = ''
while text != 'sair':
    text = input('>> ')
    os.system('cls' if os.name == 'nt' else 'clear')
    service.synthesize_using_websocket(text,
                                   test_callback,
                                   accept='audio/wav',
                                   voice="pt-BR_IsabelaVoice"
                                  )