from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl


def parse_detail(data, base_url, locator_domain, country):
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        locations = soup.select("ul.st-shortcuts--list li ul li a")
        for location in locations:
            page_url = location["href"]
            if "store-detail" not in page_url:
                continue
            soup1 = bs(session.get(page_url).text, "lxml")
            store_number = page_url.split("sid=")[1]
            address = soup1.select_one(
                "div.store-details a.store-address address.address"
            )
            if not address:
                continue
            address = soup1.select_one(
                "div.store-details a.store-address address.address"
            ).text
            addr = parse_address_intl(address)
            _phone = soup1.select_one("div.store-details a.phone")
            phone = "<MISSING>"
            if _phone:
                phone = _phone["href"].replace("tel:", "").strip()
            hours = []
            for _ in soup1.select("#store-hours div.store-hour-box"):
                hours.append(
                    f'{_.h5.text.strip()}: {_.select_one("span").text.strip()}'
                )
            latitude = soup1.select_one(".map-canvas")["data-latitude"]
            longitude = soup1.select_one(".map-canvas")["data-longitude"]

            data.append(
                SgRecord(
                    page_url=page_url,
                    store_number=store_number,
                    location_name=location.text,
                    street_address=addr.street_address_1,
                    city=addr.city,
                    state=addr.state,
                    latitude=latitude,
                    longitude=longitude,
                    zip_postal=addr.postcode,
                    phone=phone,
                    country_code=country,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )
            )


def fetch_data():
    # canada
    data = []
    locator_domain = "https://ca.diesel.com/"
    base_url = "https://ca.diesel.com/en/stores"
    parse_detail(data, base_url, locator_domain, "CA")

    # uk
    locator_domain = "https://uk.diesel.com/"
    base_url = "https://uk.diesel.com/en/stores"
    parse_detail(data, base_url, locator_domain, "UK")

    # us
    locator_domain = "https://shop.diesel.com/"
    base_url = "https://shop.diesel.com/en/stores"
    parse_detail(data, base_url, locator_domain, "US")

    return data


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
