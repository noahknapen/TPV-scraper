import argparse
import requests
from bs4 import BeautifulSoup
import re
import datetime

# TODO: Do not hardcode the number of fields
# TODO: Make applicable for tennis courts (add flag that looks for 'padel' or 'tennis')

def generate_url(day, month, year):
    # TODO: Add checks for proper arguments
    return f"https://www.tennisenpadelvlaanderen.be/clubdashboard/reserveer-een-terrein?clubId=1956&planningDay={day}-{month}-{year}&terrainGroupId=9565&ownClub=true&clubCourts%5B0%5D=I&clubCourts%5B1%5D=O#hash_results"

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
    occupied_hours = {'field1': [], 'field2': []}

    for index in range(0, len(filtered_html)):
        if re.fullmatch(r'[0-9]{2}:[0-9]{2}', filtered_html[index]):
            hour = filtered_html[index]
        if filtered_html[index] == 'bezet':
            field = filtered_html[index-1]
            if field == 'padel 1':
                occupied_hours["field1"].append(hour)
            elif field == 'padel 2':
                occupied_hours["field2"].append(hour)
            else:
                raise Exception("Where is the field specification?")
        
    return occupied_hours

def get_fully_occupied_days_and_hours(occupied_days):

    fully_occupied = {}

    for day in occupied_days.keys():
        field1_hours = occupied_days[day]['field1']
        field2_hours = occupied_days[day]['field2']

        fully_occupied[day] = [hour for hour in field1_hours if hour in field2_hours]
    
    return fully_occupied

def get_nb_occurrences_fully_occupied(fully_occupied):

    occurrences = 0

    for hours in fully_occupied.values():
        occurrences += len(hours)
    
    return occurrences

def main():
    parser = argparse.ArgumentParser(description="Parse the HTML code of the supplied URL")
    parser.add_argument("-d", "--day", required=True, help="The start day to fetch the data from (dd-mm-yyyy)")
    parser.add_argument('--b', action='store_true')
    args = parser.parse_args()

    day = args.day.split(sep="-")
    analyze_date = datetime.date(int(day[2]), int(day[1]), int(day[0]))
    today = datetime.date.today()
    occupied_days = {}

    while analyze_date <= today:
        print(f"Analyzing {analyze_date}")
        url = generate_url(analyze_date.strftime("%d"), analyze_date.strftime("%m"), analyze_date.strftime("%Y"))

        parsed_html = get_page(url)
        filtered_html = remove_irrelevant_characters(parsed_html)
        occupied_hours = get_occupied_hours(filtered_html)
        occupied_days[analyze_date.strftime("%d-%m-%Y")] = occupied_hours
        analyze_date += datetime.timedelta(days=1)

    if args.b:
        fully_occupied_days_and_hours = get_fully_occupied_days_and_hours(occupied_days)
        print(fully_occupied_days_and_hours)
        fully_occupied_occurrences = get_nb_occurrences_fully_occupied(fully_occupied_days_and_hours)
        print(fully_occupied_occurrences)
    else:
        print(occupied_days)

    return

if __name__ == "__main__":
    main()
