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

def get_intolerance(intolerance):
    x= intolerance.replace('and', ',')
    print ("function works!!!----", str(x))
    return str(x)

#query, cuisine, diet, meal_type, intolerances
def get_data(sort, type, diet, intolerance):
    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/search"
    querystring = {"query": sort, "diet":diet,"excludeIngredients":"coconut", "type":type, "intolerances":intolerance}
    headers = {
        'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
        'x-rapidapi-key': "86e53e2d5amshc832bc79b91d0efp1736e2jsned623e38d1c5"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    meal= json.loads(response.content)
    print (meal["results"])
    if meal["results"]:
        meal_rec= "I recommend "+ meal["results"][0]["title"]+". it is ready in: " + str(meal["results"][0]["readyInMinutes"]) + " minutes"+ "You can find the recipe here: " + meal["results"][0]["sourceUrl"]
        return meal_rec
    else:
        return "no meal found"

@app.route("/recipe", methods=['POST'])

def recipe():
        payload = request.get_json()
        meal_sort = str(payload["context"]["facts"]["query_search"]["value"])
        meal_type = str(payload["context"]["facts"]["meal_type_search"]["grammar_entry"])
        diet_type = str(payload["context"]["facts"]["diet_search"]["grammar_entry"])
        intolerance = str(payload["context"]["facts"]["intolerances_search"]["grammar_entry"])
        intolerance_type=get_intolerance(intolerance)
        print (str(payload))
        recommendation = get_data(meal_sort,meal_type, diet_type, intolerance_type)
        return query_response(value=str(recommendation), grammar_entry=None)


# @app.route("/ask_about_meal_types", methods=['POST'])
# def ask_about_meal_types():
#     payload = request.get_json()
#     city = payload["context"]["facts"]["ask_about_meal_types"]["grammar_entry"]
#     data = get_data(type)
#     temp = str(payload["context"]["facts"]["meal_type_search"]["grammar_entry"])
#     tempstr = str(temp)
#     return query_response(value=tempstr, grammar_entry=None)
