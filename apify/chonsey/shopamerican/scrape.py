import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["https://www.shopamericanrental.com/locations", "location_name", "1076 Patton Ave", "Ashville", "NC", "28806", "country_code", "store_number", "828-785-1552", "location_type", "latitude", "longitude", "mon-sat 9am-7pm"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    return [["https://www.shopamericanrental.com/locations", "", "1076 Patton Ave", "Ashville", "NC", "28806", "US", "<MISSING>", "(828) 785-1552", "Office", 37.773500, -122.417831, "mon-fri 9am-7pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()