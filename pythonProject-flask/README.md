# Basic Weather forecast app 
This is this Flask based Weather forecast application that makes API calls to get detailed forecast for coming week 
and uses OpenAI to summarize the information.

## Install Dependencies
Install following dependencies 
```shell
$ pip install Flask
$ pip install pytest requests-mock openai
```

## Run 
To  set your OPENAI_API_KEY Environment variable using zsh and run the flask application:
```shell
$ echo "export OPENAI_API_KEY='yourkey'" >> ~/.zshrc
$ source ~/.zshrc
$ flask --app forecast.py run --host=0.0.0.0 --port=5001
```

## Validate
To validate the API response, use the following curl command:
```shell
$ curl http://localhost:5001/forecast/<your_city_latitude>/<your_city_longitude>
```
