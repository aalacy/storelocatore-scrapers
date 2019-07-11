import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["https://airbornesports.com/draper/", "sportsfacility", "12674 Pony Express RD", "Draper", "UT", "84020", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "mon-thur 10am-9pm"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    return [["https://airbornesports.com/draper/", "airbornesports", "12674 Pony Express RD", "Draper", "UT", "84020", "US", "<MISSING>", "(415) 966-1152", "Office", 37.773500, -122.417831, "mon-thur 10am-9pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()