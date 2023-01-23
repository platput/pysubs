# PySubs API - OpenAI powered subtitle generator API
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/platoputhur/pysubs/blob/main/LICENSE)
[![CodeCov](https://codecov.io/gh/platoputhur/pysubs/branch/main/graph/badge.svg)](https://codecov.io/gh/platoputhur/pysubs)
[![GitHub Release](https://img.shields.io/github/v/release/platoputhur/pysubs.svg)](https://github.com/platoputhur/pysubs/releases)

PySubs API  is a subtitle generator API powered by OpenAI's Whisper framework.

And we are currently in beta stage. This tool currently supports YouTube video links which means if you input a video url from YouTube, it will generate subtitles and let you download the subtitle in SRT format.

I will be fixing the bugs and keep on adding more features to it until it becomes a good enough tool to go into production stage.
If you have any thoughts on the tool like feedback, feature requests etc. feel free to create an issue here.

## Dependencies
### Firebase Dependencies
- Setup firebase project with Firestore
- Set the `GOOGLE_APPLICATION_CREDENTIALS` env variable with the Google service account key filepath so that PySubs can authenticate with Firebase.
- Use the CloudFunctions from [pysubs-cloud-functions directory](https://github.com/platoputhur/pysubs/tree/main/pysubs-cloud-functions) to sync the users between Firebase Users and Firestore `users` Collection
  - Users collection users need to have at least one credit for the users to be able to generate subtitles.
  - Currently seconds to credit ratio is based on the [constant](https://github.com/platoputhur/pysubs/blob/main/pysubs/utils/pysubs_manager.py#L24) `SECONDS_PER_ONE_CREDIT`
### Run using docker
- If running from GCP Cloudrun, add the role of Firebase Firestore Admin
- Or set the `GOOGLE_APPLICATION_CREDENTIALS` env variable with the Google service account key filepath so that PySubs can authenticate with Firebase
```shell
docker build -t pysubs .
docker create --name pysubs pysubs
docker start
```

## Run using poetry
```shell
sudo apt udpate
sudo apt install ffmpeg curl
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
python3 -m poetry install
uvicorn pysubs.main:app --host="0.0.0.0" --port=8080 --log-level="info"
```

## Testing
```shell
python3.10 -m pytest
coverage run -m pytest -v tests/ && coverage report -m
```

## Environment
```dotenv
GOOGLE_APPLICATION_CREDENTIALS="pysubs.json"
```

## Features
- [x] Add YouTube video support
- [x] Add firestore as the datastore to store the history of subtitle generations
- [x] Add firebase bearer token authentication
- [x] Add support for detecting language
- [x] API endpoint for checking subtitle generation status
- [x] Basic URL verification as a security measure, to be improved later 
- [x] Add api endpoint to get history
- [x] Add credits feature
- [x] Add firebase cloud functions to automate user sync to firestore
- [x] Reduce credit by one for each subtitle generation
- [x] Add limits to video duration based on available credits
- [x] Show error message when video url is invalid and user clicks the generate button
- [x] Add support for uploading videos
- [ ] Feature to show the details of the subtitle which is being generated
- [ ] Feature to disallow user to generate subtitles if one is being generated
- [ ] Check if the video id already exists before starting to generate the subtitle
- [ ] Add api endpoints support for subtitle translate option to different languages
- [ ] Add support for direct links of videos
- [ ] Change `SECONDS_PER_ONE_CREDIT` from [pysubs_manager.py](https://github.com/platoputhur/pysubs/blob/main/pysubs/utils/pysubs_manager.py#L24) to use an ENV variable 
- [ ] Increase test coverage
