from pydub import AudioSegment
from PIL import Image, ImageDraw


class Waveform(object):
    bar_count = 1024
    db_ceiling = 60

    def __init__(self, sound: AudioSegment):
        self.duration = len(sound)
        print(self.duration / 1000)
        self.peaks = self._calculate_peaks(sound)
        self.image = self._generate_waveform_image()

    def _calculate_peaks(self, audio_file: AudioSegment):
        """ Returns a list of audio level peaks """
        chunk_length = 256
        loudness_of_chunks = [audio_file[i * chunk_length: (i + 1) * chunk_length].rms for i in range(self.bar_count)]
        max_rms = max(loudness_of_chunks) * 1.00

        return [int((loudness / max_rms) * self.db_ceiling) for loudness in loudness_of_chunks]

    @staticmethod
    def _get_bar_image(size: (int, int), fill):
        """ Returns an image of a bar. """
        width, height = size
        bar = Image.new('RGBA', size, fill)

        end = Image.new('RGBA', (width, 2), fill)
        draw = ImageDraw.Draw(end)
        draw.point([(0, 0), (3, 0)], fill='#c1c1c1')
        draw.point([(0, 1), (3, 1), (1, 0), (2, 0)], fill='#555555')

        bar.paste(end, (0, 0))
        bar.paste(end.rotate(180), (0, height - 2))
        return bar

    def _generate_waveform_image(self):
        """ Returns the full waveform image """
        im = Image.new('RGB', (round(self.duration / 128), 128), '#f5f5f5')
        for index, value in enumerate(self.peaks, start=0):
            column = index * 8 + 2
            upper_endpoint = 64 - value
            im.paste(self._get_bar_image((4, value * 2), '#424242'), (column, upper_endpoint))

        return im

    def get_image(self):
        return self.image
