import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_bing_free(query):
    query = urllib.parse.quote_plus(query)
    url = f"https://www.bing.com/search?q={query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for item in soup.find_all('li', {'class': 'b_algo'}):
        title = item.find('h2').text
        link = item.find('a')['href']
        snippet_tag = item.find('p')
        snippet = snippet_tag.text if snippet_tag else ""
        results.append({"title": title, "link": link, "snippet": snippet})
    
    return results
