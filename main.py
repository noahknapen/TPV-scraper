import argparse
import requests
from bs4 import BeautifulSoup
import re
import datetime

# TODO: Do not hardcode the number of fields
# TODO: Make applicable for tennis courts (add flag that looks for 'padel' or 'tennis')

def generate_url(type, day, month, year):
    # TODO: Add checks for proper arguments

    if type == "t_indoor":
        return f"https://www.tennisenpadelvlaanderen.be/clubdashboard/reserveer-een-terrein?clubId=1956&planningDay={day}-{month}-{year}&terrainGroupId=3464&ownClub=true&clubCourts[0]=I&clubCourts[1]=O#hash_results"
    elif type == "t_outdoor":
        return f"https://www.tennisenpadelvlaanderen.be/clubdashboard/reserveer-een-terrein?clubId=1956&planningDay={day}-{month}-{year}&terrainGroupId=3465&ownClub=true&clubCourts[0]=I&clubCourts[1]=O#hash_results"
    elif type == "padel":
        return f"https://www.tennisenpadelvlaanderen.be/clubdashboard/reserveer-een-terrein?clubId=1956&planningDay={day}-{month}-{year}&terrainGroupId=9565&ownClub=true&clubCourts%5B0%5D=I&clubCourts%5B1%5D=O#hash_results"
    else:
        raise Exception("Invalid court type was supplied")

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

def remove_irrelevant_characters(type, parsed_html):
    # Keywords: <hh:mm>, padel <1|2>, <vrij|bezet>
    # Remove all other characters

    if type == "t_indoor" or type == "t_outdoor":
        filtered_html = re.findall(r"[0-9]{2}:[0-9]{2}|terrein [0-9]{1,}|vrij|bezet|verhuurd", parsed_html)
    else:
        filtered_html = re.findall(r"[0-9]{2}:[0-9]{2}|padel [0-9]{1,}|vrij|bezet|verhuurd", parsed_html)
    
    if re.findall(r"terrein [0-9]{1,}|padel [0-9]{1,}", str(filtered_html)) == []:
        return ""
    else:
        return filtered_html

def get_occupied_hours(filtered_html):
    # TODO: add out-of-range checks

    hour = None
    fields = []
    occupied_hours = {}

    for index in range(0, len(filtered_html)):
        if re.fullmatch(r'[0-9]{2}:[0-9]{2}', filtered_html[index]):
            hour = filtered_html[index]
        if re.fullmatch(r"terrein [0-9]{1,}|padel [0-9]{1,}", filtered_html[index]):
            fields.append(filtered_html[index])
        if filtered_html[index] == 'bezet' or filtered_html[index] == 'verhuurd':
            field = filtered_html[index-1]

            if field in occupied_hours:
                occupied_hours[field].append(hour)
            else:
                occupied_hours[field] = [hour]
    
    for field in fields:
        if field not in occupied_hours:
            occupied_hours[field] = []
        
    return occupied_hours

def get_fully_occupied_days_and_hours(occupied_days):

    fully_occupied = {}

    for day in occupied_days.keys():
        fully_occupied[day] = []
        for field in occupied_days[day].keys():
            if fully_occupied[day] == []:
                fully_occupied[day] = occupied_days[day][field]
            else:
                fully_occupied[day] = [hour for hour in fully_occupied[day] if hour in occupied_days[day][field]]

    return fully_occupied

def get_nb_occurrences_fully_occupied(fully_occupied):

    occurrences = 0

    for hours in fully_occupied.values():
        occurrences += len(hours)
    
    return occurrences

def main():
    parser = argparse.ArgumentParser(description="Parse the HTML code of the supplied URL")
    parser.add_argument("-d", "--day", required=True, help="The start day to fetch the data from (dd-mm-yyyy)")
    parser.add_argument('--b', action='store_true', help='If supplied, return the number of occurrences the fields are all fully booked')
    parser.add_argument('-t', '--type', required=True, help='The court type to fetch results for. Possibilities are: "padel", "t_indoor", "t_outdoor"')
    args = parser.parse_args()

    day = args.day.split(sep="-")
    analyze_date = datetime.date(int(day[2]), int(day[1]), int(day[0]))
    today = datetime.date.today()
    occupied_days = {}

    while analyze_date <= today:
        print(f"Analyzing {analyze_date}")
        url = generate_url(args.type, analyze_date.strftime("%d"), analyze_date.strftime("%m"), analyze_date.strftime("%Y"))

        parsed_html = get_page(url)
        filtered_html = remove_irrelevant_characters(args.type, parsed_html)

        if filtered_html == "":
            analyze_date += datetime.timedelta(days=1)
            continue

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
