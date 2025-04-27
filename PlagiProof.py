import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK data (only once)
nltk.download('punkt')

# Function to scrape Bing search results
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

# Function to calculate similarity
def calculate_similarity(input_sentence, snippets):
    corpus = [input_sentence] + snippets
    vectorizer = TfidfVectorizer().fit_transform(corpus)
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity([vectors[0]], vectors[1:])
    highest_similarity = cosine_sim.max()
    return highest_similarity

# Main plagiarism checking function
def check_plagiarism(input_text):
    sentences = nltk.sent_tokenize(input_text)
    plagiarism_report = []

    for sentence in sentences:
        print(f"Checking: {sentence[:50]}...")
        try:
            search_results = search_bing_free(sentence)
            snippets = [res['snippet'] for res in search_results if res['snippet']]
            
            if snippets:
                similarity = calculate_similarity(sentence, snippets)
            else:
                similarity = 0.0
            
            plagiarism_report.append({
                'sentence': sentence,
                'similarity': similarity
            })

            time.sleep(2)  # polite delay to avoid being blocked

        except Exception as e:
            print(f"Error checking sentence: {e}")
            plagiarism_report.append({
                'sentence': sentence,
                'similarity': 0.0
            })

    return plagiarism_report

# --------------------
# Example usage
# --------------------

input_text = """
Artificial intelligence is the simulation of human intelligence processes by machines. It is widely used in fields such as healthcare, finance, and transportation. Climate change is the long-term alteration of temperature and typical weather patterns in a place.
"""

report = check_plagiarism(input_text)

print("\n--- PLAGIARISM REPORT ---")
for item in report:
    print(f"Sentence: {item['sentence']}")
    print(f"Similarity: {item['similarity']*100:.2f}%")
    if item['similarity'] >= 0.7:  # 70%+ similar is considered plagiarized
        print("⚠️ Possible Plagiarism Detected!\n")
    else:
        print("✅ Looks Original.\n")
