import argparse
import requests
from bs4 import BeautifulSoup
import re

def get_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text().lower()

    return text

def remove_irrelevant_characters(parsed_html):
    # Keywords: <hh:mm>, padel <1|2>, <vrij|bezet>
    # Remove all other characters

    filtered_html = re.findall(r"[0-9]{2}:[0-9]{2}|padel [12]|vrij|bezet", parsed_html)
    return filtered_html

def get_occupied_hours(filtered_html):
    # TODO: add out-of-range checks

    hour = None
    field1_occupied = False
    field2_occupied = False
    occupied_hours = {'field1': [], 'field2': []}

    for index in range(0, len(filtered_html)):
        if re.fullmatch(r'[0-9]{2}:[0-9]{2}', filtered_html[index]):
            hour = filtered_html[index]

            if field1_occupied:
                if re.fullmatch(r'[0-9]{2}:[0-9]{2}',filtered_html[index+1]):
                    occupied_hours["field1"].append(hour)

            if field2_occupied:
                if re.fullmatch(r'[0-9]{2}:[0-9]{2}',filtered_html[index+1]):
                    occupied_hours["field2"].append(hour)

        if filtered_html[index] == 'bezet':
            field = filtered_html[index-1]
            if field == 'padel 1':
                occupied_hours["field1"].append(hour)
                field1_occupied = True
            elif field == 'padel 2':
                occupied_hours["field2"].append(hour)
                field2_occupied = True
            else:
                raise Exception("Where is the field specification?")
        
        if filtered_html[index] == 'vrij':
            field = filtered_html[index-1]
            if field == 'padel 1':
                field1_occupied = False
            elif field == 'padel 2':
                field2_occupied = False
            else:
                raise Exception("Where is the field specification?")
    
    return occupied_hours

def main():
    parser = argparse.ArgumentParser(description="Parse the HTML code of the supplied URL")
    parser.add_argument("-u", "--url", required=True, help="The URL to retrieve")
    args = parser.parse_args()

    url = args.url

    parsed_html = get_page(url)
    filtered_html = remove_irrelevant_characters(parsed_html)
    occupied_hours = get_occupied_hours(filtered_html)
    print(occupied_hours)

if __name__ == "__main__":
    main()
