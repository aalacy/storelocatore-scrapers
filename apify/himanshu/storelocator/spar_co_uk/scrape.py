import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests

MISSING = "<MISSING>"

STREET_NUM = re.compile("""^\d{1,7}[A-Z]?$""")
CONNECTED_HOUSE_NUMS = re.compile("""^\d+ ?- ?\d+$""")
UNIT_NUM = re.compile("""^Unit \d+$""")

def or_default(get_value: lambda: str, default = MISSING) -> str:
    try:
        v_stripped = get_value().strip()
        return v_stripped if v_stripped else default
    except:
        return default

def condense(string: str) -> str:
    return re.sub(" +", " ", re.sub("\r*\n", " ", string)).strip()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    requests = SgRequests()

    base_url = "https://www.spar.co.uk"

    r = requests.get("https://www.spar.co.uk/sitemap-page",headers={})
    soup = BeautifulSoup(r.text, "lxml")

    encountered_identities = set()

    for inex,link in enumerate(soup.find_all("a")):
        if "/store-locator/" in link['href']:
            page_url = base_url + link['href']

            # special case
            if "https://www.spar.co.uk/store-locator/hal24301" in page_url:
                continue
            
            r1= requests.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")

            # Sometimes, the JSON doesn't have all the answers... or the correct answers, fot that matter.
            contact_us_raw = list(map(condense,
                                  list(filter(lambda s: s.strip() and s.strip() != ",",
                                              ",".join(list(soup1.find("div", {"class": "store-details__contact"}).stripped_strings)).split(",")))))

            # Putting street numbers back with the street, if they were comma-separated.
            contact_us = []
            street_address_seen = False
            for item in contact_us_raw:
                # some street addresses have these in them, which isn't necessary.
                if item == "SPAR" or item == "Euro Garages":
                    continue

                if STREET_NUM.match(item) \
                        or CONNECTED_HOUSE_NUMS.match(item) \
                        or UNIT_NUM.match(item):
                    street_address_seen = True
                    contact_us.append(item)

                elif not street_address_seen:
                    contact_us.append(item)

                else:
                    contact_us[-1] = f"{contact_us[-1]} {item}"
                    street_address_seen = False
            # ------

            try:
                address_idx = contact_us.index("Address")
                street_address = contact_us[address_idx + 1]
                city = contact_us[address_idx + 2]

                if len(contact_us) > address_idx + 4:
                    state = contact_us[address_idx + 3]
                    zipcode = contact_us[address_idx + 4]
                else:
                    state = None
                    zipcode = contact_us[address_idx + 3]
            except (ValueError, IndexError) as e:
                # either no values, or ambiguous data
                (street_address, city, state, zipcode) = (None, None, None, None)

            try:
                phone_idx = contact_us.index("Phone")
                phone = contact_us[phone_idx + 1]
            except ValueError:
                phone = None


            addr = json.loads(soup1.find(lambda tag : (tag.name == "script") and "latitude" in tag.text).text)

            street_address = street_address if street_address else or_default(lambda: addr['address']['streetAddress'])
            zipcode =        zipcode if zipcode else or_default(lambda: addr['address']['postalCode'])
            store_number =   or_default(lambda: page_url[page_url.rfind("/") + 1:])

            city =           city if city else or_default(lambda: addr['address']['addressLocality'])
            state =          state if state else or_default(lambda: addr['address']['addressRegion'])
            phone =          phone if phone else or_default(lambda: addr['telephone'])

            lat =            or_default(lambda: addr['geo']['latitude'])
            lng =            or_default(lambda: addr['geo']['longitude'])
            location_name =  or_default(lambda: addr['name'], "SPAR")
            location_type =  or_default(lambda: addr['@type'])

            operating_hours = ", ".join(
                [" ".join(
                    [" ".join(d['dayOfWeek']), d['opens'], d['closes']]) for d in addr['openingHoursSpecification']
                ]
            )

            # missing crucial address details
            if not street_address and not zipcode:
                continue

            # if it's closed 7 days a week, treat it as permanently closed
            if operating_hours.count("CLOSED") == 7:
                continue

            # deduping
            if store_number in encountered_identities:
                continue
            else:
                encountered_identities.add(store_number)

            if street_address.isdigit() or CONNECTED_HOUSE_NUMS.match(street_address) or street_address == "SPAR":
                print(list(soup1.find("div", {"class": "store-details__contact"}).stripped_strings))
                print(contact_us_raw)
                print(contact_us)
                print(addr['address']['streetAddress'])
                print("----")

            store = [base_url,
                     location_name,
                     street_address,
                     city,
                     state,
                     zipcode,
                     "UK",
                     store_number,
                     phone,
                     location_type,
                     lat,
                     lng,
                     operating_hours,
                     page_url]

            yield [field.strip() if field else MISSING for field in store]

def scrape():
    data = fetch_data()
    write_output(data)

if __name__ == "__main__":
    scrape()
