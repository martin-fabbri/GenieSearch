import requests
from bs4 import BeautifulSoup

def scrape_url(url: str):
    try:
        # set a get request to webpage
        response = requests.get(url)

        # if the request response was successful
        if (response.status_code == 200):
            # parse the content of the request
            soup = BeautifulSoup(response.text, "html.parser")
            text_content = soup.get_text(separator=" ", strip=True)
            return text_content
        else:
            return f"Failed to retrieve page: {response.status_code}"
    except Exception as e:
        print(e)    

    return ""