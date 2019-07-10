import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["https://www.birkenstock.com/us/storelocator", "BirkenStockStore", "120 Spring St", "New York", "NY", "10012", "country_code", "store_number", "(646)-890-6940", "location_type", "latitude", "longitude", "mon-fri 10am-8pm"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    return [["https://www.birkenstock.com/us/storelocator", "BirkenStockStore", "120 Sprint St", "New York ", "NY", "10012", "US", "<MISSING>", "(646) 890-6940", "Office", 37.773500, -122.417831, "mon-fri 10am-8pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()