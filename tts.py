from transformers import VitsModel, AutoTokenizer
import sounddevice as sd
import torch
from visualizer import Visualizer
import re
from multiprocessing import Process

print(); print()

class Mouth:
    def __init__(self, model_id='kakao-enterprise/vits-vctk', speaker_id=0, device='cpu', visualize=False):
        self.model = VitsModel.from_pretrained(model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.device = device
        self.model.to(device)
        self.speaker_id = speaker_id
        self.visualize = visualize
        if visualize:
            self.visualizer = Visualizer(self.model.config.sampling_rate)
    @torch.no_grad()
    def run_tts(self, text):
        inputs = self.tokenizer(text, return_tensors="pt")
        inputs = inputs.to(self.device)
        output = self.model(**inputs, speaker_id=self.speaker_id).waveform[0].to('cpu')
        return output

    def say(self, text):
        output = self.run_tts(text)
        # get the duration of audio
        sd.play(output, samplerate=self.model.config.sampling_rate)
        if self.visualize:
            self.visualizer.visualize(output, text)
        sd.wait()

    def say_interruption(self, text, listen_interruption_func):
        output = self.run_tts(text)
        # get the duration of audio
        duration = len(output) / self.model.config.sampling_rate
        p = Process(target=sd.play, args=(output, self.model.config.sampling_rate))
        p1 = Process(target=listen_interruption_func, args=(duration,))
        p.start() # start saying the text
        p1.start() # start listening for interruption
        p1.join() # get interruption result
        sd.stop() # stop saying the text (if it's still saying bc then it's interrupted)
        p.join()


    def say_multiple(self, text):
        pattern = r'[.?!]'
        sentences = re.split(pattern, text)
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        print(sentences)
        for sentence in sentences:
            self.say(sentence)

if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    mouth = Mouth(device=device, speaker_id=7)

    text = "If there's one thing that makes me nervous about the future of self-driving cars, it's that they'll replace human drivers.\nI think there's a huge opportunity to make human-driven cars safer and more efficient. There's no reason why we can't combine the benefits of self-driving cars with the ease of use of human-driven cars."
    print(text)
    mouth.say(text)
    sd.wait()




