# DOMPERIDOG - BD2-TP

**Important: Some of the requirements to run the API are not available on windows, so we recommend using linux or a venv.**

API for taking notes and writing documents. Includes user support eith authentication, document visibility, multiple editors, favourite documents, etc.

## Set Up

To use the API, you need a MongoDB instance running. The docker offical image can be used by executing the following command inside the
```./app``` directory

```shell
docker-compose up
```

Once the db is running, ensure that you have Python 3.7 or above installed as the API is built using FastApi. The necessary requirements can be installed with:

```shell
pip install -r requirements.txt
```

Finally  once the requirments are installed, outside of the ```./app``` directory, start the API with:

```shell
cd ..
uvicorn app.main:app
```



The API will serve on port 8000, you can use localhost:8000/docs to interact with it.


 
