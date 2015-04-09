# SIPCallRecordVerify
Automated SIP call generator for verifying recording platforms

-------
- In a nutshell, this will register as a user that should have Call Recording enabled. Every N seconds it will place a call and playback a pre-defined annoucment. 

- Once the call has been recorded, the recording is fetched then the speech is converted to text using Google Speech APIs.

- The result from Google is verified with Python lib 'Natural Language Toolkit' by tokenizing the string and producing stems. The stems are then compaired to the expected text and scored. If the score is greater or equal to the threshold, the recording is valid.

- The Google Speech API isn't 100% perfect, "Recording" in speech may end up as "Recorded" in the resulting text once converted. The Stem word for both "Recording" and "Recorded" is "Record" so whatever the Speech API returns, as long as the stem is good, that token is valid.

```
Usage: main.py [options]

Options:
  -h, --help    show this help message and exit
  -c CONFIG     eg: server_one.json
  -i INTERVAL   Test interval in seconds (default: 5min)
  -t THRESHOLD  Minimum threshold percent that recording is valid (default:
                80)
  -v VERBOSE    Be verbose with logging
  ```
