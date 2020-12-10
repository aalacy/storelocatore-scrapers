import csv
from sgrequests import SgRequests


def write_output(data):
    with open('data.csv', mode='w', encoding='utf8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []
    url = 'https://racewaystores.com/'
    api_url = 'https://www.racewaystores.com/api/locations.php'

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        locator_domain = url
        street_address = j.get('address') or '<MISSING>'
        city = j.get('city') or '<MISSING>'
        state = j.get('state') or '<MISSING>'
        postal = j.get('zip') or '<MISSING>'
        if not postal.isdigit() or len(postal) != 5:
            postal = '<MISSING>'
        country_code = 'US'
        store_number = j.get('number') or '<MISSING>'
        page_url = f'https://www.racewaystores.com/location-details?s={j.get("slug")}'
        location_name = f"RaceWay #{store_number} {j.get('name')}"
        phone = j.get('phone') or '<MISSING>'
        latitude = j.get('latitude') or '<MISSING>'
        longitude = j.get('longitude') or '<MISSING>'
        location_type = '<MISSING>'
        hours = j.get('hours')
        if hours:
            hours_of_operation = f"{hours[0].get('days')}: {hours[0].get('hours')}"
        else:
            hours_of_operation = '<MISSING>'

        row = [locator_domain, page_url, location_name, street_address, city, state, postal,
               country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
