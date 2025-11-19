import argparse
import requests
from bs4 import BeautifulSoup

def get_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"ERror fetching the page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text().lower()

    return text

def main():
    parser = argparse.ArgumentParser(description="Parse the HTML code of the supplied URL")
    parser.add_argument("-u", "--url", required=True, help="The URL to retrieve")
    args = parser.parse_args()

    url = args.url

    print(get_page(url))

if __name__ == "__main__":
    main()
