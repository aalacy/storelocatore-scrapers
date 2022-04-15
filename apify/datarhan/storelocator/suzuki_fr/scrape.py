# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.suzuki.fr/ajax-store-result?q=&c={};{}&nextStep=3&monde=3&typeTunnel=contact"
    domain = "suzuki.fr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.FRANCE], expected_search_radius_miles=10
    )
    for lat, lng in all_coords:
        data = session.get(start_url.format(lat, lng), headers=hdr).json()
        for poi in data["stores"]:
            page_url = f'https://www.suzuki.fr/store/show/{poi["slug"]}'
            location_type = ", ".join([e["post_name"] for e in poi["services"]])
            hoo = []
            hoo_data = [e for e in poi["schedules"] if e["name"] == "Espace commercial"]
            if hoo_data:
                hoo_data = hoo_data[0]["dates"]
                for day, hours in hoo_data.items():
                    time = []
                    for e in hours:
                        if e["open"]:
                            opens = e["open"]["date"].split()[-1].split(":00.")[0]
                            closes = e["close"]["date"].split()[-1].split(":00.")[0]
                            time.append(f"{opens} - {closes}")
                    time = " / ".join(time)
                    if not time:
                        time = "closed"
                    hoo.append(f"{day}: {time}")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=poi["address"],
                city=poi["city"],
                state="",
                zip_postal=poi["zipcode"],
                country_code="FR",
                store_number=poi["code"],
                phone=poi["phone"],
                location_type=location_type,
                latitude=poi["lat"],
                longitude=poi["lng"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
