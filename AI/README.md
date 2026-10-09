## Run Commands
- `uv run ai` - voice recognition program
- `uv run sound_interpreter.py` - sound recognition program

## Sound Recognition Model Setup
The sound recognizer uses the PANNs Cnn14 audio tagging model. It requires two files that are **not** in the repo.
- `class_labels_indices.csv` (15 KB) in `~/panns_data/`
    - The path is hard coded in `panns-inference`, so the library cannot be imported without it.
- `Cnn14_mAP=0.431.pth` (327 MB) in `AI/models/`
    - Contains model weights

### Model Installation
`cd` to the `AHCI-Project/AI` folder, then:

**macOS/Linux**
```bash
mkdir -p ~/panns_data models
curl -L -o ~/panns_data/class_labels_indices.csv https://raw.githubusercontent.com/qiuqiangkong/audioset_tagging_cnn/master/metadata/class_labels_indices.csv
curl -L -o models/Cnn14_mAP=0.431.pth "https://zenodo.org/records/3987831/files/Cnn14_mAP%3D0.431.pth?download=1"
```

**Windows**
```powershell
mkdir $HOME\panns_data -Force; mkdir models -Force
curl.exe -L -o $HOME\panns_data\class_labels_indices.csv https://raw.githubusercontent.com/qiuqiangkong/audioset_tagging_cnn/master/metadata/class_labels_indices.csv
curl.exe -L -o "models\Cnn14_mAP=0.431.pth" "https://zenodo.org/records/3987831/files/Cnn14_mAP%3D0.431.pth?download=1"
```
