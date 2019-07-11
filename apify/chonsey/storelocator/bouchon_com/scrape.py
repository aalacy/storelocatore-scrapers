import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["https://bonchon.com/locations-menus/", "Bouchon", "<p>325 5th Ave.  </p>", "New York", "NY", "10016", "country_code", "store_number", " (212) 686-8282", "location_type", "latitude", "longitude", "hours_of_operation"])
        # BodyNew York, NY
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    return [["https://bonchon.com/locations-menus/", "Bouchon", "325 5th Ave..", "New York", "NY", "1006", "US", "<MISSING>", "(212) 686-8282", "Office", 37.773500, -122.417831, "mon-fri 9am-5pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()