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
    url = 'https://hangerclinic.com/find-a-clinic/'
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
              "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
              "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
              "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
              "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'}

    for s in states:
        session = SgRequests()
        r = session.get(f'https://hangerclinic.com/wp-content/themes/hanger/search-locations.php?search={s}',
                        headers=headers)
        js = r.json()['locations']

        for j in js:
            locator_domain = url
            store_number = j.get('post_id') or '<MISSING>'
            page_url = j.get('link') or '<MISSING>'
            street_address = f"{j.get('address_line_1')} {j.get('address_line_2') or ''}".strip() or '<MISSING>'
            city = j.get('city') or '<MISSING>'
            state = j.get('state_abbreviation') or '<MISSING>'
            postal = j.get('zip_code') or '<MISSING>'
            country_code = j.get('country') or '<MISSING>'
            location_name = f"{city}, {j.get('state')} - {j.get('name')}"
            phone = j.get('phone_number') or '<MISSING>'
            latitude = j.get('map_pin', {}).get('lat') or '<MISSING>'
            longitude = j.get('map_pin', {}).get('lng') or '<MISSING>'
            location_type = '<MISSING>'
            hours_of_operation = j.get('hours', '').replace('\r\n', ';') or '<MISSING>'

            row = [locator_domain, page_url, location_name, street_address, city, state, postal,
                   country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
            out.append(row)
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
