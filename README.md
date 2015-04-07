# SIPCallRecordVerify
Automated SIP call generator for verifying recording platforms


In a nutshell, this will register as a user that should have Call Recording enabled. Every N seconds it will place a call and playback a pre-defined annoucment. 

Once the call has been recorded, the recording is fetched then the speech is converted to text using Google Speech APIs.

The result from Google is verified with Python lib 'Natural Language Toolkit' by tokenizing the string and producing steams. The steams are then compaired to the expected text and scored. If the score is greater or equal to the threshold, the recording is valid.

As the Google Speech API isn't 100% perfect, "Recording' in speech may end up as "Recorded" in the resulting text. As the Stem word for both of these is "Record" - the text is done on "Record" thus, the recording would be valid.
