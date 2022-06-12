from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.thrivepetcare.com/_next/data/4sAX9Sn5t9bIiA6c1JqIW/all-locations.json"
    domain = "thrivepetcare.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for state in data["pageProps"]["groupedLocations"]:
        for city in state["locationByStateAndCity"]:
            for poi in city["locations"]:
                hdr = {
                    "authorization": "Bearer i_SbzNYIH9E46sD9b4vIreJwelXDt96f8HAhhZWIpmA"
                }
                poi = session.get(
                    f'https://cdn.contentful.com/spaces/8hq8guzcncfs/environments/master/entries?content_type=location&limit=1&fields.storeNumber={poi["marketingId"]}',
                    headers=hdr,
                ).json()
                slug = poi["items"][0]["fields"]["slug"]
                poi_url = f'https://www.thrivepetcare.com/_next/data/4sAX9Sn5t9bIiA6c1JqIW//locations/{state["state"].lower().replace(" ", "-")}/{city["city"].lower().replace(" ", "-")}/{slug}.json'  # slug=illinois&slug=arlington-heights&slug=northwest-highway'
                poi_data = session.get(poi_url, headers=hdr).json()
                page_url = f'https://www.thrivepetcare.com/locations/{state["state"].lower().replace(" ", "-")}/{city["city"].lower().replace(" ", "-")}/{slug}'
                street_address = poi_data["pageProps"]["siteApiData"]["addressLine1"]
                street_address_2 = poi_data["pageProps"]["siteApiData"]["addressLine2"]
                if street_address_2:
                    street_address += " " + street_address_2
                hoo = []
                hoo_data = [
                    e["workdays"]
                    for e in poi_data["pageProps"]["siteApiData"]["departments"]
                    if e["workdays"]
                ]
                hoo_data = hoo_data[0] if hoo_data else []
                for e in hoo_data:
                    hoo.append(
                        f'{e["dayOfWeek"]}: {e["openTime"][:-3]} - {e["closeTime"][:-3]}'
                    )
                hoo = " ".join(hoo)
                latitude = poi_data["pageProps"]["siteApiData"]["latitude"]
                longitude = poi_data["pageProps"]["siteApiData"]["longitude"]
                latitude = latitude if latitude and len(str(latitude)) > 2 else ""
                longitude = longitude if longitude and len(str(longitude)) > 2 else ""

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi_data["pageProps"]["page"]["name"],
                    street_address=street_address,
                    city=poi_data["pageProps"]["siteApiData"]["city"],
                    state=poi_data["pageProps"]["siteApiData"]["state"],
                    zip_postal=poi_data["pageProps"]["siteApiData"]["postcode"],
                    country_code="",
                    store_number=poi_data["pageProps"]["page"]["storeNumber"],
                    phone=poi_data["pageProps"]["siteApiData"]["mainPhone"],
                    location_type="",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hoo,
                )

                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.PAGE_URL})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
