# -*- coding: utf-8 -*-
import json
from flask import Flask, request
from jinja2 import Environment
from urllib.request import Request, urlopen
from os import getenv
import structlog
from logger import configure_stdout_logging
import requests



def setup_logger():
    logger = structlog.get_logger(__name__)
    try:
        log_level = getenv("LOG_LEVEL", default="INFO")
        configure_stdout_logging(log_level)
        return logger
    except BaseException:
        logger.exception("exception during logger setup")
        raise


logger = setup_logger()
app = Flask(__name__)
environment = Environment()


def jsonfilter(value):
    return json.dumps(value)


environment.filters["json"] = jsonfilter


def error_response(message):
    response_template = environment.from_string("""
    {
      "status": "error",
      "message": {{message|json}},
      "data": {
        "version": "1.0"
      }
    }
    """)
    payload = response_template.render(message=message)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    logger.info("Sending error response to TDM", response=response)
    return response


def query_response(value, grammar_entry):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": {{value|json}},
            "confidence": 1.0,
            "grammar_entry": {{grammar_entry|json}}
          }
        ]
      }
    }
    """)
    payload = response_template.render(value=value, grammar_entry=grammar_entry)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    logger.info("Sending query response to TDM", response=response)
    return response


def multiple_query_response(results):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "result": [
        {% for result in results %}
          {
            "value": {{result.value|json}},
            "confidence": 1.0,
            "grammar_entry": {{result.grammar_entry|json}}
          }{{"," if not loop.last}}
        {% endfor %}
        ]
      }
    }
     """)
    payload = response_template.render(results=results)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    logger.info("Sending multiple query response to TDM", response=response)
    return response


def validator_response(is_valid):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "is_valid": {{is_valid|json}}
      }
    }
    """)
    payload = response_template.render(is_valid=is_valid)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    logger.info("Sending validator response to TDM", response=response)
    return response


@app.route("/dummy_query_response", methods=['POST'])
def dummy_query_response():
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": "dummy",
            "confidence": 1.0,
            "grammar_entry": null
          }
        ]
      }
    }
     """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    logger.info("Sending dummy query response to TDM", response=response)
    return response


@app.route("/action_success_response", methods=['POST'])
def action_success_response():
    response_template = environment.from_string("""
   {
     "status": "success",
     "data": {
       "version": "1.1"
     }
   }
   """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    logger.info("Sending successful action response to TDM", response=response)
    return response

#query, cuisine, diet, meal_type, intolerances
def get_data(query, cuisine, diet, meal_type, intolerances):
    if cuisine == "no":
        cuisine = None
    if diet == "no":
        diet = None
    if meal_type == "no":
        meal_type = None
    if intolerances == "no":
        intolerances = None


    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/search"

    querystring = {"query": "query", "cuisine": "cuisine", "diet": "diet",
                   "intolerances": "intolerances", "type": "meal_type", }

    headers = {
        'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
        'x-rapidapi-key': "6c9ee808bamshe34b62dbfdbf169p1600c8jsn69ba74f35b5a"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    meal = json.loads(response.content)
    print(str(meal),"---------")

    return meal

    #print(response.text)

    @app.route("/recipe", methods=['POST'])
    def recipe():
        payload = request.get_json()
        city = payload["context"]["facts"]["city_to_search"]["grammar_entry"]
        country = payload["context"]["facts"]["country_to_search"]["grammar_entry"]
        city, country = str(city), str(country)

        if 'units' in payload["context"]["facts"]:
            unit = payload["context"]["facts"]["units"]["grammar_entry"]
            unit_str = str(unit)  # "metric"or"standard"or"imperial"
        else:
            unit_str = 'metric'  # default

        ans_data = get_data(city, country, unit=unit_str)
        temp_ans_data = ans_data['main']['temp']
        temp_ans_datastr = str(temp_ans_data)
        meal = str(get_data())
        return query_response(value=meal, grammar_entry=None)


