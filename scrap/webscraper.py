from bs4 import BeautifulSoup
import requests

url = 'https://help.twitter.com/es'

response = requests.get(url, timeout=5)

content = BeautifulSoup(response.content, "html.parser")

# print(content)

for tweet in content.findAll('div', attrs={"class": "hp01__content"}):
    #print(tweet.text)
    for text in tweet.findAll('li', attrs={"class","hp01__topic-list-item"}):
        print(text)