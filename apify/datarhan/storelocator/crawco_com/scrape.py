from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://locator.crawco.com/api/countries/?callback=JSON_CALLBACK"
    domain = "crawco.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_countries = session.get(start_url, headers=hdr).json()
    for country in all_countries:
        country = country["code"]
        url = f"https://locator.crawco.com/api/branches/?country={country}&callback=JSON_CALLBACK"
        all_locations = session.get(url).json()

        for poi in all_locations:
            store_url = f'https://www.crawco.com/about/our-locations/{poi["number"]}{poi["addressNum"]}'
            location_name = poi["name"]
            street_address = poi["address"].get("line1")
            if not street_address:
                street_address = poi["address"].get("line2")
            if poi["address"].get("line1") and poi["address"].get("line2"):
                street_address += " " + poi["address"]["line2"]
            if street_address and poi["address"].get("line3"):
                street_address += " " + poi["address"]["line3"]
            if not street_address:
                street_address = poi["mailing"].get("line1")
                if poi["mailing"].get("line2"):
                    street_address += " " + poi["mailing"]["line2"]
            if not street_address:
                street_address = "<MISSING>"
            if street_address == ".":
                poi_data = session.get(
                    f'https://locator.crawco.com/api/branches/{poi["number"]}{poi["addressNum"]}?callback=JSON_CALLBACK'
                ).json()
                street_address = poi_data["address"]["line1"]
                if poi_data["address"].get("line2"):
                    street_address += " " + poi_data["address"]["line2"]
            city = poi["address"].get("city")
            if city:
                city = city.replace(", D.C.", "").replace("DHA, ", "")
            state = poi["address"].get("state")
            zip_code = poi["address"].get("postal")
            country_code = poi["address"]["country"]
            store_number = poi["number"]
            phone = poi["contact"].get("phone")
            latitude = poi["mapping"].get("lat")
            longitude = poi["mapping"].get("lng")

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="",
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
