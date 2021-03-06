import os
import json
import requests
import tempfile
from pydub import AudioSegment
from excp.exception import ConnectionLostException
from excp.exception import NotUnderstoodException


class Google_STT:

    """
    This class uses Google's Speech to Text engine to convert passed flac(audio) to text
    """

    def __init__(self, audio, rate=44100):
        self.audio = audio
        self.rec_rate = audio.rate() if audio.rate() else rate
        self.text = None

    def get_text(self):
        """
        This method returns a string form of the converted data
        """
        (_, stt_flac_filename) = tempfile.mkstemp('.flac')
        sound = AudioSegment.from_wav(self.audio.filename())
        sound.export(stt_flac_filename, format="flac")
        g_url = "http://www.google.com/speech-api/v1/recognize?lang=en"
        headers = {'Content-Type': 'audio/x-flac; rate= %d;' % self.rec_rate}
        recording_flac_data = open(stt_flac_filename, 'rb').read()
        try:
            r = requests.post(g_url, data=recording_flac_data, headers=headers)
        except requests.exceptions.ConnectionError:
            raise ConnectionLostException()
        response = r.text
        os.remove(stt_flac_filename)
        self.audio.housekeeping()
        if not 'hypotheses' in response:
            raise NotUnderstoodException()
        phrase = json.loads(response)['hypotheses'][0]['utterance']
        return str(phrase)
