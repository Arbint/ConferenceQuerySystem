# To Local Test:

* Create a virtual env:
```sh
python -m venv .venv
```
* Activate the virtual env:
```MAC```
```
source ./venv/bin/activate
```

* Install Streamlit, Pillow, and qrCode
```
pip install streamlit \
pip install pillow \
pip install qrcode
```

* Generate QR Code:

open ./src/qrCodeGen.py

Set the correct server ip, for local test, should be your computers local ip, in the ```def GetServerURL():```

```py
def GetServerURL():
    return "http://your.server.ip:8501"
```


run the qrCodeGen.py.

the QR code should be under output/qrcodes

* Launch to server:
    - go to src:
```
cd ./src
```

- launch app.py with streamlit

```
    streamlit run app.py
```

* Scan the qrcode to go to the corresponding booth