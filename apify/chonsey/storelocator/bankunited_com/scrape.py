import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["https://www.bankunited.com/branch-locator", "location_name", "252 Broadway Brooklyn", "New York", "New York", "11211", "country_code", "store_number", "1-877-779-2265", "location_type", "latitude", "longitude", "9am-2pm"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    return [["safegraph.com", "SafeGraph", "1543 Mission St.", "San Francisco", "CA", "94103", "US", "<MISSING>", "(415) 966-1152", "Office", 37.773500, -122.417831, "mon-fri 9am-5pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()