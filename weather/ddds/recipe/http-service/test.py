import requests

url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/search"

querystring = {"query":"burger","diet":"vegetarian","excludeIngredients":"coconut","number":"10","offset":"0","type":"main course"}

headers = {
    'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
    'x-rapidapi-key': "a669cfa708mshf8c72019da728f7p125f74jsnbcded802d375"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)