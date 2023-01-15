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

# Environment
```dotenv
GOOGLE_APPLICATION_CREDENTIALS="pysubs.json"
```

# Features
- [x] Add YouTube video support
- [x] Add firestore as the datastore to store the history of subtitle generations
- [x] Add firebase bearer token authentication
- [x] Add support for detecting language
- [x] API endpoint for checking subtitle generation status
- [x] Basic URL verification as a security measure, to be improved later 
- [x] Add api endpoint to get history
- [ ] Check if the video id already exists before starting to generate the subtitle
- [ ] Add api endpoints support for subtitle translate option to different languages
- [ ] Add support for direct links of videos
- [ ] Add support for uploading videos
- [ ] Increase test coverage
