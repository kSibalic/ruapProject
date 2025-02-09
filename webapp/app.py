from flask import Flask, render_template, request
import urllib.request
import json
import os
import ssl

def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True)

app = Flask(__name__)

API_URL = 'http://060fd6ad-695f-4ef8-a9b2-24f8243c2f3d.eastus2.azurecontainer.io/score'
API_KEY = 'aMv3SZnrX4pkyuwhigofZ3mRG2dvhS2B'  # Insert your API key here

@app.route('/', methods=['GET', 'POST'])
def index():
    scored_labels = None  # Default value if no prediction is available
    if request.method == 'POST':
        data = {
            "Inputs": {
                "input1": [
                    {
                        "Brand": request.form.get("brand"),
                        "Processor": request.form.get("processor"),
                        "RAM_GB": int(request.form.get("ram")),
                        "Storage": request.form.get("storage"),
                        "GPU": request.form.get("gpu"),
                        "Screen_Size_inch": float(request.form.get("screen_size")),
                        "Resolution": request.form.get("resolution"),
                        "Battery_Life_hours": float(request.form.get("battery_life")),
                        "Weight_kg": float(request.form.get("weight")),
                        "Operating_System": request.form.get("os"),
                        "Price_$": None
                    }
                ]
            }
        }

        body = str.encode(json.dumps(data))
        headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + API_KEY)}
        req_obj = urllib.request.Request(API_URL, body, headers)

        try:
            response = urllib.request.urlopen(req_obj)
            result = response.read().decode()
            result_json = json.loads(result)
            # Extract the predicted label using the actual key name from the JSON response.
            prediction = result_json["Results"]["WebServiceOutput0"][0]["Scored Labels"]
            scored_labels = {"Predicted Target": prediction}
        except urllib.error.HTTPError as error:
            error_message = error.read().decode("utf8", 'ignore')
            scored_labels = {"Error": error_message}

    return render_template("index.html", scored_labels=scored_labels)

if __name__ == '__main__':
    app.run(debug=True)
