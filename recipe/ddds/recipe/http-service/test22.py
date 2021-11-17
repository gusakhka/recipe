import requests

url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/1003464/nutritionWidget.json"

headers = {
    'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
    'x-rapidapi-key': "a669cfa708mshf8c72019da728f7p125f74jsnbcded802d375"
    }

response = requests.request("GET", url, headers=headers)

print(response.text)