# TPV-scraper
This is a scraper for the Tennis en Padel Vlaanderen website. Its goal is to be a configurable scraper which can be used to, for example, look for availabilities, pull up historic data and perform analysis on said data.

# Usage
By default, the scraper takes a start date and returns a list of dates from the start date until today with all the padel courts and the hours on which they are booked. It only works for *T.C. Het Zeen*.

The scraper can be configured to return these results for tennis courts instead of padel courts. It can also be configured to return the hours on which all courts, either for tennis or padel, are booked in the same timeslot.

## Arguments
`-d`: The start day to fetch the data from (dd-mm-yyyy)

`--b`: If supplied, return the number of occurrences the fields are all fully booked

`--t`: If supplied, fetch the results for tennis instead of padel

