Development Notes
=================

# A minimal Browser-to-phone-calls application
This consists of the following.

1. Flask backend -- serves capability token and TwiML
2. HTML -- landing page for the browser
3. Javascript -- client-side program flow and Twilio Device to allow browser-based voice calls

Bringing up a Twilio application goes as follows:

1. Start ngrok
    ngrok http 5000
2. Start the Flask http server application
    python app.py run
3. Surf to `localhost:5000` in Chromium (we'll try to use it later in headless mode)
  1. The page should be rendered
4. Troubleshooting tips
  1. Ensure that the Twilio voice App for this application has the correct ngrok endpoint. It should be `http://aabb1122.ngrok.io/voice`; the Flask app serves the voice TwiML at this address.

Then, making a call from a browser to a phone number goes as follows.


# Official Twilio Docs
https://www.twilio.com/docs/

## Javascript CLient Device
This device is required to do call control and data flow within the browser.
https://www.twilio.com/docs/voice/client/javascript/device

# Tutorials
The present minimal application is based on https://github.com/TwilioDevEd/clicktocall-flask. Some other sources are listed below.

## Twilio Browser-Phone and Browser-Browser call tutorial in Flask
I didn't end up using this as it comes with too many bells and whistles for a start.
In the Twilio Docs: https://www.twilio.com/docs/voice/tutorials/browser-calls-python-flask
On Github: https://github.com/TwilioDevEd/browser-calls-flask

## Minimal Flask application
https://github.com/zaccolley/twilio-call-phone-from-browser/blob/master/server.js

## Minimal Node.js+Angular application
https://www.twilio.com/docs/voice/tutorials/browser-dialer-node-angular
https://github.com/TwilioDevEd/browser-dialer-angular

# Minimal click-to-call app

* Need Twilio account, Account SID, Token, Application SID
* Flask application
 * HTML template
 * Javascript
  * Build Twilio Device with callbacks for various interactions

# Twilio Applications

These contain URLs for voice and/or SMS. They tell Twilio what to do (through the TwiML accessible at the respective URL) when there is an **incoming** call. Accessible through user console. The TwiML can be static or generated programmatically.

https://www.twilio.com/docs/usage/api/applications

