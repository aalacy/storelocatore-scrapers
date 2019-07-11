import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["https://www.bakedbymelissa.com/locations", "ColombusCircle", "975 8th Ave", "New York", "NY", "10019", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "mon-fri 8am-10pm"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    return [["https://www.bakedbymelissa.com/locations", "ColumbusCircle", "975 8th Ave", "New York", "NY", "10019", "US", "<MISSING>", "(415) 966-1152", "Office", 37.773500, -122.417831, "mon-fri 9am-5pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()