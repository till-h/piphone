Development Notes
=================

# Dependencies

        sudo apt install libffi libffi-dev openssl libssl-dev
        pip install Flask tox twilio

and if you like it

        sudo apt install python-virtualenv

The pip installation may take a while on an RPi.

# Audio in Chromium
Setting .asoundrc to force audio devices.
https://pimylifeup.com/raspberry-pi-google-assistant/

Also see sibling files about sound setup.

# A minimal Browser-to-phone-calls application
This consists of the following.

1. Flask backend -- serves capability token (to browser) ~~and TwiML (to Twilio)~~
2. HTML -- landing page for the browser
3. Javascript -- client-side program flow and Twilio Device to allow browser-based voice calls

## Using the minimal app
1. ~~Start ngrok~~

        ~~ngrok http 5000~~

2. ~~Enter the ngrok URL as the Twilio application endpoint for voice. Ensure that the Twilio voice App for this application has the correct ngrok endpoint. It should be `http://aabb1122.ngrok.io/voice`; the Flask app serves the voice TwiML at this address.~~
1. The TwiML response is now saved on the Twilio Cloud.

1. Enable the virtualenv if you set one up, `piphone/bin/activate`

3. Start the Flask http server application

        python app.py run

4. Surf to `localhost:5000` in Chromium (we'll try to use it later in headless mode).
5. The user enters a phone number to be called into the field or uses the default value and presses call.
6. Somewhere, a phone rings.

## Program flow

The following outlines the program flow that makes the above use case possible.

1. The browser requests `localhost:5000/`. This renders `index.html`, passing along the default number to be called and the caller ID.
2. When the page has loaded, the Javascript in `app.js` requests a capability token from the Flask backend at `localhost:5000/token`.
   1. Flask returns a Token to the browser that allows the Twilio Device in the browser to make outgoing calls.
   
      > **Twilio Capability Tokes** contain the SID of the Twilio user account and an authorisation token. These allow Twilo to connect the call from a so-called **Twilio Device** (that manages the browser side of the call) to a user account. This is required for authentication, billing etc. Also, the Token assigns the Device its capabilities, such as "You can make outgoing calls" or "You can receive incoming calls".

   2. A Twilio Device is set up (in Javascript) with the capabilities defined inside the Token.
   3. When the Device is ready, the call button is activated.
   4. In our case, the outgoing-calls capability that was returned from `/token` contains the SID of a TwiML Application.

      > **TwiML** is a micro language that defines the behaviour during a Twilio call. A **TwiML Application**, when contacted by a Twilo Device, maps the request to a TwiML URL from which the Device learns what to do when it has been instructed to make a call.

4. When the user presses the call button, the Twilio Device makes a request to the URL that the TwiML application points to, in our case `http://aabb1122.ngrok.io/voice`. This request contains as parameters the number to be called and the caller ID.
5. `http://aabb1122.ngrok.io/voice` directs to `localhost:5000/voice`, using ngrok.
6. `localhost:5000/voice` contains TwiML that instructs the device to:
   1. Read out the number being called
   2. Dial the number, thus initiating the connection from the Device inside the browser to a phone number.

Happy chatting!

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

