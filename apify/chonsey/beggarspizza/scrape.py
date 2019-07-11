import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["https://www.raleys.com/store-locator/", "Raley West Capitol West", "1601 W.Capitol ave., West", "Sacremento", "CA", "95691", "country_code", "store_number", "(916)372-3000", "location_type", "latitude", "longitude", "mon-fri 6am-11pm"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    return [["https://www.raleys.com/store-locator/", "Raley West Capitol West", "1601 W.Capitol ave., West", "Sacremento", "CA", "95691", "US", "<MISSING>", "(916) 372-3000", "Office", 37.773500, -122.417831, "mon-fri 6am-11pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()