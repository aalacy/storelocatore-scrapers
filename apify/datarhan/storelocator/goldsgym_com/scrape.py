import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "goldsgym.com"

    start_url = "https://www.goldsgym.com/api/gyms/locate?country={}"
    all_countries = ["US", "CA"]
    for country in all_countries:
        response = session.get(start_url.format(country))
        data = json.loads(response.text)

        for poi in data["gyms"]:
            if poi["gym_status"] == "presale":
                continue
            store_url = poi["siteurl"]
            location_name = poi["gym_name"]
            street_address = poi["address"]
            if poi["address_2"]:
                street_address += " " + street_address
            city = poi["city"]
            state = poi["state"]
            zip_code = poi["postal_code"]
            country_code = poi["country"]
            store_number = poi["id"]
            phone = poi["gym_settings"]["phone"]
            location_type = poi["gym_type"]
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hours_of_operation = []
            for day, hours in poi["gym_settings"]["business_hours_this_week"].items():
                if hours["closedAllDay"]:
                    hours_of_operation.append("{} - closed".format(day))
                else:
                    open_h = hours["open"]["date"].split()[-1].split(".")[0]
                    close_h = hours["close"]["date"].split()[-1].split(".")[0]
                    hours_of_operation.append("{} {} - {}".format(day, open_h, close_h))
            hours_of_operation = (
                ", ".join(hours_of_operation).replace("00:00:00 - 00:00:00", "24h")
                if hours_of_operation
                else "<MISSING>"
            )
            if "Tu - closed, We - closed" in hours_of_operation:
                continue

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
