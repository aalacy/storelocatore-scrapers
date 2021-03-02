import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def parse_usa(x):
    return parser.parse_address_usa(x)


def parse_intl(x):
    return parser.parse_address_intl(x)


def fetch_data():
    us_url = "https://hosted.where2getit.com/skechers/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E8C3F989C-6D95-11E1-9DE0-BB3690553863%3C%2Fappkey%3E%3Cformdata+id%3D%22getlist%22%3E%3Cobjectname%3EStoreLocator%3C%2Fobjectname%3E%3Corder%3Erank%3C%2Forder%3E%3Climit%3E1000%3C%2Flimit%3E%3Cwhere%3E%3Ccountry%3E%3Ceq%3EUS%3C%2Feq%3E%3C%2Fcountry%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
    can_url = "https://hosted.where2getit.com/skechers/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E8C3F989C-6D95-11E1-9DE0-BB3690553863%3C%2Fappkey%3E%3Cformdata+id%3D%22getlist%22%3E%3Cobjectname%3EStoreLocator%3C%2Fobjectname%3E%3Corder%3Erank%3C%2Forder%3E%3Climit%3E200%3C%2Flimit%3E%3Cwhere%3E%3Ccountry%3E%3Ceq%3ECA%3C%2Feq%3E%3C%2Fcountry%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
    gb_url = "https://hosted.where2getit.com/skechers/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E8C3F989C-6D95-11E1-9DE0-BB3690553863%3C%2Fappkey%3E%3Cformdata+id%3D%22getlist%22%3E%3Cobjectname%3EStoreLocator%3C%2Fobjectname%3E%3Corder%3Erank%3C%2Forder%3E%3Climit%3E200%3C%2Flimit%3E%3Cwhere%3E%3Ccountry%3E%3Ceq%3EUK%3C%2Feq%3E%3C%2Fcountry%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"

    url_arr = [us_url, can_url, gb_url]
    locator_domain = "https://www.skechers.com/"
    xml_cont = session.get(can_url)
    all_store_data = []
    for url in url_arr:
        xml_cont = session.get(url)
        xml_tree = BeautifulSoup(xml_cont.content, features="lxml")

        locs = xml_tree.find_all("poi")
        for loc in locs:
            location_name = loc.find("name").text + " " + loc.find("name2").text
            location_name = location_name.strip()
            street_address = loc.find("address1").text + " " + loc.find("address2").text
            street_address = street_address.strip()
            country_code = loc.find("country").text.strip()
            if country_code == "CA":
                state = loc.find("province").text

            else:
                state = loc.find("state").text
            city = loc.find("city").text
            zip_code = loc.find("postalcode").text

            lat = loc.find("latitude").text
            longit = loc.find("longitude").text

            phone_number = loc.find("phone").text

            if phone_number == "":
                phone_number = "<MISSING>"

            if loc.find("rmon").text == "":
                hours = "<MISSING>"
            else:
                hours = "Monday " + loc.find("rmon").text + " "
                hours += "Tuesday " + loc.find("rtues").text + " "
                hours += "Wednesday " + loc.find("rwed").text + " "
                hours += "Thursday " + loc.find("rthurs").text + " "
                hours += "Friday " + loc.find("rfri").text + " "
                hours += "Saturday " + loc.find("rsat").text + " "
                hours += "Sunday " + loc.find("rsun").text

            location_type = (
                loc.find("name")
                .text.replace("SKECHERS", "")
                .replace("Skechers", "")
                .strip()
            )
            store_number = loc.find("storeid").text.replace("Store ", "").strip()
            if "SFO" in store_number:
                store_number = "<MISSING>"
            if store_number == "":
                store_number = "<MISSING>"

            country_code = loc.find("country").text

            page_url = "<MISSING>"
            if not state:
                if url == gb_url:
                    state = "<MISSING>"
            if any(not i for i in [street_address, city, state, zip_code]):
                raw_addr = []
                for i in [street_address, city, state, zip_code]:
                    if i:
                        raw_addr.append(i)
                raw_addr = " ".join(raw_addr)
                if url == us_url:
                    parsed = parse_usa(raw_addr)
                else:
                    parsed = parse_intl(raw_addr)

                street_address = parsed.street_address_1
                if parsed.street_address_2:
                    street_address = street_address + ", " + parsed.street_address_2
                city = parsed.city if parsed.city else "<MISSING>"
                state = parsed.state if parsed.state else "<MISSING>"
                zip_code = parsed.postcode if parsed.postcode else "<MISSING>"

            store_data = [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone_number,
                location_type,
                lat,
                longit,
                hours,
                page_url,
            ]
            z = 0
            while z < len(store_data):
                if not store_data[z]:
                    store_data[z] = "<MISSING>"
                z += 1

            all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
