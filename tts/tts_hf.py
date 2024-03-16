from transformers import VitsModel, AutoTokenizer
import sounddevice as sd
import torch
from tts.base import BaseMouth

print()
print()


class Mouth_hf(BaseMouth):
    def __init__(self, model_id='kakao-enterprise/vits-vctk', speaker_id=0, device='cpu'):
        self.model = VitsModel.from_pretrained(model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.device = device
        self.model.to(device)
        self.speaker_id = speaker_id
        super().__init__(sample_rate=self.model.config.sampling_rate)

    @torch.no_grad()
    def run_tts(self, text):
        inputs = self.tokenizer(text, return_tensors="pt")
        inputs = inputs.to(self.device)
        output = self.model(**inputs, speaker_id=self.speaker_id).waveform[0].to('cpu')
        return output


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    mouth = Mouth_hf(device=device, speaker_id=7)

    text = ("If there's one thing that makes me nervous about the future of self-driving cars, it's that they'll "
            "replace human drivers.\nI think there's a huge opportunity to make human-driven cars safer and more "
            "efficient. There's no reason why we can't combine the benefits of self-driving cars with the ease of use "
            "of human-driven cars.")
    print(text)
    mouth.say_multiple(text, lambda x: False)
    sd.wait()
