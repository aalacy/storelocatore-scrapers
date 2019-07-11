import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["https://www.americasthrift.com/locations/", "Alabaster", "218 Second St SW", "Alabaster", "AL", "35007", "country_code", "store_number", "(205) 664-0777", "location_type", "latitude", "longitude", "mon-sat 7:30-9pm"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    return [["https://www.americasthrift.com/locations/", "Alabaster", "218 Second St Sw", "Alabaster", "AL", "35007", "US", "<MISSING>", "(205) 664-0777", "Office", 37.773500, -122.417831, "mon-sat 7:30-9pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()