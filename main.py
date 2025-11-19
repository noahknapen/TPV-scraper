import argparse
import requests
from bs4 import BeautifulSoup
import re

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

def remove_irrelevant_characters(parsed_html):
    # Keywords: <hh:mm>, padel <1|2>, <vrij|bezet>
    # Remove all other characters

    filtered_html = re.findall(r"[0-9]{2}:[0-9]{2}|padel [12]|vrij|bezet", parsed_html)
    return filtered_html

def main():
    parser = argparse.ArgumentParser(description="Parse the HTML code of the supplied URL")
    parser.add_argument("-u", "--url", required=True, help="The URL to retrieve")
    args = parser.parse_args()

    url = args.url

    parsed_html = get_page(url)
    filtered_html = remove_irrelevant_characters(parsed_html)
    print(filtered_html)


if __name__ == "__main__":
    main()
