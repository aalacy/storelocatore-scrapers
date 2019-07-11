import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["https://locations.ctownsupermarkets.com/", "Ctown", "885 Bergen Ave", "Jersey city", "NJ", "07306", "country_code", "store_number", "(201) 795-1740", "location_type", "latitude", "longitude", "7am-830pm"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    return [["https://locations.ctownsupermarkets.com/", "Ctown", "885 Bergen Ave", "Jersey city ", "NJ", "94103", "US", "<MISSING>", "(415) 966-1152", "Office", 37.773500, -122.417831, "mon-fri 7am-8:30pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()