import csv
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests


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
    session = SgRequests()

    items = []

    DOMAIN = "roomandboard.com"
    start_url = "https://www.roomandboard.com/stores/"

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "cookie": 'SESSION=fef2c7df-a696-4c7d-ad33-9b9492d76752; s_dfa=roomandboardprod%2Croomroomandboardglobalprod; AMCVS_90240C0F53E8D8B30A490D45%40AdobeOrg=1; AMCV_90240C0F53E8D8B30A490D45%40AdobeOrg=-330454231%7CMCMID%7C51481925924369249871701993374624858748%7CMCAAMLH-1613571409%7C6%7CMCAAMB-1613571409%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1612973809s%7CNONE%7CvVersion%7C3.1.2; mt.v=2.1760119965.1612966609481; s_cc=true; _ga=GA1.2.865277710.1612966610; _gid=GA1.2.1816227031.1612966610; _gcl_au=1.1.1764126543.1612966610; __rutmb=66078253; __ruid=66078253-1v-do-4t-1p-rahtlrj7ye0yro6zg3wl-1612966610425; __rcmp=0!bj1fZ2MsZj1nYyxzPTEsYz0yOTIyLHRyPTEwMCxybj03NTMsdHM9MjAyMTAyMTAuMTQxNixkPXBjO249c2IxLGY9c2Iscz0xLGM9MjE5Nix0PTIwMTkwNDEwLjE4MDQ7bj1zcDEsZj1zcCxzPTEsYz0yMTk5LHQ9MjAxOTA0MTUuMTg0NA~~; __rslct=sb%2Csp; tracker_device=d059853b-97a2-421f-b3f9-c25668ef9a6d; fpcid=3672841528767164252_FP; _pin_unauth=dWlkPVltWmtNbU00TW1VdE5UazBNaTAwWlRneUxUaGtNVGN0TmpRMU9XTmpPRGhpT1dKbQ; eu-gdpr-opt-in=1; s_nr=1612966626171-New; s_sq=%5B%5BB%5D%5D; __rutma=66078253-1v-do-4t-1p-rahtlrj7ye0yro6zg3wl-1612966610425.1612966610425.1612966610425.1.2.2; __rpck=0!eyJwcm8iOiJkaXJlY3QiLCJidCI6eyIwIjp0cnVlLCIxIjowLCIyIjpudWxsLCIzIjoxfSwiQyI6e30sIk4iOnt9fQ~~; _uetsid=9e1871006baa11eb8c86efbcbe3dd833; _uetvid=9e1c05206baa11eb8965377bec9417f9; _derived_epik=dj0yJnU9dnZYbjYzeTBsOE50VHZSQ2hVYUd0cFRNamlEd3BoYVMmbj1CTkx0YnBoLW1HNks2MmJWLW95Yy13Jm09MSZ0PUFBQUFBR0FqNnVNJnJtPTEmcnQ9QUFBQUFHQWo2dU0; featureToggles="DISABLE_AVAILABILITY=OFF&DELAYED_DELIVERY_MESSAGING=OFF&DELIVERY_DATES_WITHOUT_TIME=ON&PRODUCT_PAGE_HIDE_STOCKED=ON&RETURN_REASON_CODES=ON&PAYMENT_TOKENS_IN_ENGAGE=ON&NEW_EMAIL_PREFERENCES=ON&ADD_TO_DELIVERY_GROUP_PHASE1_PUBLIC=ON&MY_OPPORTUNITY_BULK_LOOKUP=ON&COVID_MESSAGING=OFF&DELAYED_UPS_MESSAGING=OFF&ORDER_HISTORY_SUMMARY_KEYS=ON&REMOVE_2PM_UPS=ON&CHECKOUT_REMOVE_DEFERRED_DELIVERY=ON&UPS_EXPEDITED_CHARGE_UPDATES=ON&WISHLIST_MODAL=ON&CUSTOM_CABINETS_INSERT_ATTRIBUTES=ON&COVID_SHIP_UPS_SEPARATE=OFF&COVID_EXTENDED_DELIVERY_WINDOWS=OFF&PARTIAL_PAYMENT=ON&ADD_TO_DELIVERY_GROUP_PHASE1_ENGAGE=ON"; __rpckx=0!eyJ0NyI6eyIyIjoxNjEyOTY2NjI2Mjg0fSwidDd2Ijp7IjIiOjE2MTI5NjY2ODYzNDB9LCJpdGltZSI6IjIwMjEwMjEwLjE0MTYifQ~~',
        "referer": "https://www.roomandboard.com/privacy-approval/?path=/stores/",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="Card-link Heading Heading--4"]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[@id="store-schema-data"]/text()')[0]
        poi = json.loads(poi.replace("0],", '0"],'))

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi.get("telephone")
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]
        location_type = location_type if location_type else "<MISSING>"
        geo = (
            loc_dom.xpath('//a[contains(@href, "/@")]/@href')[-1]
            .split("/@")[-1]
            .split(",")[:2]
        )
        latitude = geo[0]
        longitude = geo[1]
        hoo = loc_dom.xpath('//div[h2[text()="Hours"]]/following-sibling::div//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        if "," in city:
            state = city.split(", ")[-1]
            city = city.split(",")[0]

        item = [
            DOMAIN,
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
