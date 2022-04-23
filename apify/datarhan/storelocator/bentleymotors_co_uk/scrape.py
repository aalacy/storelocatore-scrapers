from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "bentleymotors.co.uk"
    start_url = "https://www.bentleymotors.com/content/brandmaster/global/bentleymotors/en/apps/dealer-locator/jcr:content.api.6cac2a5a11b46ea2d9c31ae3f98bfeb0.json"
    data = session.get(start_url).json()
    for poi in data["dealers"]:
        data = session.get(urljoin(start_url, poi["url"])).json()
        location_name = data["dealerName"]
        for a in data["addresses"]:
            street_address = a["street"]
            city = a["city"]
            zip_code = a.get("postcode")
            country_code = a["country"]
            store_number = a["id"]
            phone = a["departments"][0].get("phone")
            phone = phone.split("/")[0] if phone else ""
            latitude = a["wgs84"]["lat"]
            longitude = a["wgs84"]["lng"]
            hoo = []
            for elem in a["departments"][0]["openingHours"]:
                if elem["periods"]:
                    day = elem["day"]
                    if elem["closed"] is False:
                        opens = elem["periods"][0]["open"]
                        closes = elem["periods"][0]["close"]
                        hoo.append(f"{day} {opens} - {closes}")
                    else:
                        hoo.append(f"{day} closed")

            hours_of_operation = ", ".join(hoo) if hoo else ""
            if hours_of_operation:
                if "Saturday" not in hours_of_operation:
                    hours_of_operation += ", Saturday closed Sunday closed"
                if "Sunday" not in hours_of_operation:
                    hours_of_operation += ", Sunday closed"
            else:
                hours_of_operation = "Monday closed, Tuesday closed, Wednesday closed, Thursday closed, Friday closed, Saturday closed, Sunday closed"
            page_url = f"https://www.bentleymotors.com/en/apps/dealer-locator.html/partner/{store_number}-{location_name.replace(' ', '-')}"
            location_type = ", ".join([dep["name"] for dep in a["departments"]])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state="",
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
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
