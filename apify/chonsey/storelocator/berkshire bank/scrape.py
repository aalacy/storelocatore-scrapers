import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["https://www.berkshirebank.com/About/Let-Us-Help/Locations", "Bank", "66 West St", "Pittsfield", "MA", "01201", "country_code", "store_number", "1.800.773.5601.", "location_type", "latitude", "longitude", "mon-thur 8:30-4:30"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    return [["https://www.berkshirebank.com/About/Let-Us-Help/Locations", "Bank", "66 West St.", "Pittsfield", "MA", "01201", "US", "<MISSING>", "1.800.773.5601", "Office", 37.773500, -122.417831, "mon-fri 9am-5pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()