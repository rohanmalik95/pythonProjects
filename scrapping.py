import requests
from bs4 import BeautifulSoup

data = requests.get("https://www.imdb.com/search/title/?title_type=feature&genres=thriller")
soup = BeautifulSoup(data.text,"html.parser")
movieList= soup.find_all("h3",class_="lister-item-header")
for i in movieList:
    print(i.a.text)
