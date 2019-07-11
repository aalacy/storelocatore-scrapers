import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["https://www.billskhakis.com/store-locator/", "Binghams", "827 E Broadway, ", "Colombia", "MO", "65201", "country_code", "store_number", "673-442-6397", "location_type", "latitude", "longitude", "9am-9pm"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    return [["https://www.billskhakis.com/store-locator/", "827 E Broadway,", "", "Colombia", "MO", "65201", "US", "<MISSING>", "(415) 966-1152", "Office", 37.773500, -122.417831, "mon-fri 9am-5pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()