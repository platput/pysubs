# Dependencies
```shell
brew install ffmpeg
sudo apt update && sudo apt install ffmpeg
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
poetry add git+https://github.com/openai/whisper.git
```

# Testing
```shell
python3.10 -m pytest
coverage run -m pytest -v tests/ && coverage report -m
```

# Environement
GOOGLE_APPLICATION_CREDENTIALS="/Users/defiant/Projects/Personal/secrets/pysubs-af9fe-79a960deb29b.json"
