import re
import csv
from lxml import html

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_items = []

    start_url = "https://hosted.where2getit.com/icebreaker/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E6F5D49F0-91F8-11E0-89D3-C9B5E425BB5D%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Climit%3E250%3C%2Flimit%3E%3Corder%3Erank%2C+_distance%3C%2Forder%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E%3C%2Faddressline%3E%3Clongitude%3E{}%3C%2Flongitude%3E%3Clatitude%3E{}%3C%2Flatitude%3E%3Ccountry%3E%3C%2Fcountry%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E200%3C%2Fsearchradius%3E%3Cradiusuom%3Emile%3C%2Fradiusuom%3E%3Cwhere%3E%3Cactive%3E%3Ceq%3E1%3C%2Feq%3E%3C%2Factive%3E%3Cor%3E%3Cicebreakertouchlab%3E%3Ceq%3EYes%3C%2Feq%3E%3C%2Ficebreakertouchlab%3E%3Cicebreakeroutlet%3E%3Ceq%3EYes%3C%2Feq%3E%3C%2Ficebreakeroutlet%3E%3Cpremiumretailers%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpremiumretailers%3E%3Cgeneralretailers%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fgeneralretailers%3E%3C%2For%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_coords = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.USA,
            SearchableCountries.CANADA,
            SearchableCountries.BRITAIN,
        ],
        max_search_distance_miles=200,
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lng, lat), headers=hdr)
        dom = html.fromstring(bytes(response.text, encoding="utf8"))

        all_locations = dom.xpath("//poi")
        for poi_html in all_locations:
            store_url = "https://www.icebreaker.com/en-us/stores"
            location_name = poi_html.xpath(".//name/text()")
            location_name = location_name[0] if location_name else "<MISSING>"
            street_address = poi_html.xpath(".//address1/text()")
            street_address = street_address[0] if street_address else "<MISSING>"
            city = poi_html.xpath(".//city/text()")
            city = city[0] if city else "<MISSING>"
            state = poi_html.xpath(".//state/text()")
            state = state[0] if state else "<MISSING>"
            zip_code = poi_html.xpath(".//postalcode/text()")
            zip_code = zip_code[0] if zip_code else "<MISSING>"
            country_code = poi_html.xpath(".//country/text()")
            country_code = country_code[0] if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath(".//phone/text()")
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi_html.xpath(".//latitude/text()")
            latitude = latitude[0] if latitude else "<MISSING>"
            longitude = poi_html.xpath(".//longitude/text()")
            longitude = longitude[0] if longitude else "<MISSING>"
            hours_of_operation = "<MISSING>"

            item = [
                domain,
                store_url,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]

            check = f"{location_name} {street_address}"
            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
