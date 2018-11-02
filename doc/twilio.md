Twilio on RPi
=============

# Browser calls to phones

https://www.twilio.com/docs/voice/tutorials/browser-calls-python-flask

# Using Flask

https://github.com/TwilioDevEd/browser-calls-flask

# Installation prerequisites

apt install libssl-dev libffi-dev


Follow the instructions, site comes up, but the local server throws tracebacks. The JWT Client code seems broken, it is missing a generate function. Adding this following the last bit of https://github.com/TwilioDevEd/browser-calls-flask/issues/6#issuecomment-294327266 leads to further Tracebacks.

Check this further.

The call initiates, but immediately hangs up. Checked that this is the same behaviour on the API explorer and using a laptop.

Maybe an option

https://github.com/zaccolley/twilio-call-phone-from-browser/blob/master/server.js