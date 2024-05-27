import librosa
import numpy as np

def calculate_audio_features(audio_file):

    y, sr = librosa.load(audio_file)
    
    average_volume = np.mean(librosa.feature.rms(y=y))
    
    return {
        'duration': librosa.get_duration(y=y, sr=sr),
        'sample_rate': sr,
        'channels': 1 if len(y.shape) == 1 else y.shape[0],
        'average_volume': average_volume
    }
