import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["https://bodyalivefitness.com/kenwood/", "kenwood", "8100 Montgomery Rd", "cincinnati", "Ohio", "45326", "country_code", "store_number", "(513)630-9352", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    return [["https://bodyalivefitness.com/kenwood/", "Kenwood", "8100 Montgomery Rd.", "Cincinnati", "Ohio", "45326", "US", "<MISSING>", "(513) 630-9352", "Office", 37.773500, -122.417831, "mon-fri 9am-5pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()