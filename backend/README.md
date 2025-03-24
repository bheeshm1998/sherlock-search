command to run the backend app
```
uvicorn app.main:app --reload 
```


in windows to start the python virtual environment
```
venv/Scripts/activate

```

on linux and mac use
```
source myenv/bin/activate
```

start command for render
```aiignore
uvicorn app.main:app --host 0.0.0.0 --port 7888
```

pip install command for render
```aiignore
pip install -r requirements.txt
```