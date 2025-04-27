import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

# Function to check plagiarism
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

            time.sleep(2)  # polite delay

        except Exception as e:
            print(f"Error checking sentence: {e}")
            plagiarism_report.append({
                'sentence': sentence,
                'similarity': 0.0
            })

    return plagiarism_report

# Function to read a PDF file
def read_pdf(file_path):
    pdf_text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()
    return pdf_text

# Function to generate PDF report
def generate_pdf_report(report, output_filename):
    c = canvas.Canvas(output_filename, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica", 12)
    y_position = height - 40
    c.drawString(40, y_position, "Plagiarism Check Report")
    y_position -= 20
    
    for item in report:
        c.drawString(40, y_position, f"Sentence: {item['sentence'][:100]}...")  # Display first 100 characters
        y_position -= 15
        c.drawString(40, y_position, f"Similarity: {item['similarity']*100:.2f}%")
        y_position -= 15
        
        if item['similarity'] >= 0.7:
            c.drawString(40, y_position, "⚠️ Possible Plagiarism Detected!")
        else:
            c.drawString(40, y_position, "✅ Looks Original.")
        y_position -= 20

        if y_position < 50:  # New page if space is running out
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 40

    c.save()

# --------------------
# MAIN MENU
# --------------------
if __name__ == "__main__":
    print("\n💬 Welcome to the Plagiarism Checker!\n")
    print("Select input method:")
    print("1️⃣  Type/Paste Text")
    print("2️⃣  Upload .txt file")
    print("3️⃣  Upload .pdf file\n")

    choice = input("Enter your choice (1/2/3): ")

    full_text = ""

    if choice == "1":
        print("\nEnter the text you want to check (press Enter twice when done):\n")
        user_input = []
        while True:
            line = input()
            if line == "":
                break
            user_input.append(line)
        full_text = "\n".join(user_input)

    elif choice == "2":
        filename = input("\nEnter the path to your .txt file: ")
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                full_text = file.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            exit()

    elif choice == "3":
        filename = input("\nEnter the path to your .pdf file: ")
        try:
            full_text = read_pdf(filename)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            exit()

    else:
        print("❌ Invalid choice. Exiting.")
        exit()

    # Now run plagiarism check
    report = check_plagiarism(full_text)

    # Generate and save PDF report
    pdf_filename = input("\nEnter the desired filename for the PDF report (e.g., report.pdf): ")
    generate_pdf_report(report, pdf_filename)

    print(f"\nPDF report saved as {pdf_filename}.")
