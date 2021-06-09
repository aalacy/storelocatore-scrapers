import csv
import ssl
import time

from datetime import datetime
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address, International_Parser
from sgselenium import SgSelenium

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []

    locator_domain = "https://www.patagonia.com/"
    api_url = "https://patagonia.locally.com/stores/conversion_data?has_data=true&company_id=30&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=40.78831928091212&map_center_lng=-74.06000000000097&map_distance_diag=5000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["markers"]:
        page_url = "https://www.patagonia.com/store-locator"
        location_name = j.get("name") or "<MISSING>"
        location_type = "Authorized Patagonia Dealer"
        street_address = j.get("address") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        try:
            hours_of_operation = f"Mon {datetime.strptime(str(j.get('mon_time_open')),'%H%M').strftime('%I:%M %p')} - {datetime.strptime(str(j.get('mon_time_close')),'%H%M').strftime('%I:%M %p')} Tue {datetime.strptime(str(j.get('tue_time_open')),'%H%M').strftime('%I:%M %p')} - {datetime.strptime(str(j.get('tue_time_close')),'%H%M').strftime('%I:%M %p')} Wed {datetime.strptime(str(j.get('wed_time_open')),'%H%M').strftime('%I:%M %p')} - {datetime.strptime(str(j.get('wed_time_close')),'%H%M').strftime('%I:%M %p')} Thu {datetime.strptime(str(j.get('thu_time_open')),'%H%M').strftime('%I:%M %p')} - {datetime.strptime(str(j.get('thu_time_close')),'%H%M').strftime('%I:%M %p')} Fri {datetime.strptime(str(j.get('fri_time_open')),'%H%M').strftime('%I:%M %p')} - {datetime.strptime(str(j.get('fri_time_close')),'%H%M').strftime('%I:%M %p')} Sat {datetime.strptime(str(j.get('sat_time_open')),'%H%M').strftime('%I:%M %p')} - {datetime.strptime(str(j.get('sat_time_close')),'%H%M').strftime('%I:%M %p')} Sun {datetime.strptime(str(j.get('sun_time_open')),'%H%M').strftime('%I:%M %p')} - {datetime.strptime(str(j.get('sun_time_close')),'%H%M').strftime('%I:%M %p')}"
        except:
            hours_of_operation = "<MISSING>"

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    store_url = "https://www.patagonia.com/store-locator/"
    session = SgRequests()
    r = session.get(store_url, headers=headers)
    tree = html.fromstring(r.text)
    select = tree.xpath('//select[@class="input-select country"]/option/@value')
    for i in select:
        apis_url = (
            f"https://www.patagonia.com/store-locator/?dwfrm_wheretogetit_country={i}"
        )
        session = SgRequests()
        r = session.get(apis_url, headers=headers)
        country_code = i
        if country_code == "JP":
            continue
        tree = html.fromstring(r.text)
        divs = tree.xpath('//div[@class="store-info"]')
        for d in divs:

            page_url = "https://www.patagonia.com" + "".join(
                d.xpath('.//div[@class="store-name"]/a/@href')
            )
            location_name = (
                "".join(d.xpath('.//div[@class="store-name"]//text()'))
                .replace("\n", "")
                .strip()
            )

            ad = (
                "".join(d.xpath('.//div[@class="store-addr"]/text()'))
                + " "
                + "".join(d.xpath('.//div[@class="store-location"]/text()'))
            )

            adr = parse_address(International_Parser(), ad)
            street_address = (
                f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                    "None", ""
                ).strip()
                or "<MISSING>"
            )

            city = adr.city or "<MISSING>"
            state = adr.state or "<MISSING>"
            postal = adr.postcode or "<MISSING>"

            store_number = "<MISSING>"
            stn = page_url.split("store_")[1].split(".html")[0].strip()
            if stn.isdigit():
                store_number = stn
            phone = (
                "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
                .replace("p:", "")
                .strip()
                or "<MISSING>"
            )
            location_type = "Patagonia Retail Stores"
            if (
                page_url.find(
                    "https://www.patagonia.com/on/demandware.store/Sites-patagonia-us-Site/en_US/Page-Show?cid=store_206469445"
                )
                != -1
            ):
                page_url = apis_url
            if (
                page_url.find(
                    "https://www.patagonia.com/on/demandware.store/Sites-patagonia-us-Site/en_US/Page-Show?cid=store_Patagonia-Tu-Cheng-Outlet"
                )
                != -1
            ):
                page_url = apis_url

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//strong[contains(text(), "Opening Hours")]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if hours_of_operation == "<MISSING>":
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//strong[contains(text(), "Store Hours")]/following-sibling::text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
            hours_of_operation = hours_of_operation.replace(": Monday", "Monday")
            if hours_of_operation == "<MISSING>" and country_code == "US":
                driver = SgSelenium().firefox()
                driver.get(page_url)
                time.sleep(5)
                page_source = driver.page_source
                a = html.fromstring(page_source)
                hours_of_operation = (
                    " ".join(
                        a.xpath(
                            "//div[@class='store-details-hours--full store-hours-details-js']/p/text()"
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )

            latitude = (
                "".join(tree.xpath('//div[@class="store-locator-map"]/@data-latitude'))
                or "<MISSING>"
            )
            longitude = (
                "".join(tree.xpath('//div[@class="store-locator-map"]/@data-longitude'))
                or "<MISSING>"
            )

            row = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                postal,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
