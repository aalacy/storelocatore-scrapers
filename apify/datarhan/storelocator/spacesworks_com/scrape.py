import json
from datetime import datetime, timezone
from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    # Your scraper here
    session = SgRequests()

    domain = "spacesworks.com"
    start_url = "https://api.spacesworks.com/ws/rest/marketing/v1/locations?itemsPerPage=100&pageIndex=1&locale=en_GB"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "authorization": "Basic c3BhY2Vzd29ya3NAc3BhY2VzYnYtSzdUTVJIOmVmNmJlYWJjLTYwMTctNGYzMC04NDlhLTQ1YjY0N2I1NWVkMg==",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
        "x-ga-clientid": "1722608705.1614690743",
        "x-geo-iso2": "US",
    }
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)
    all_locations = data["data"]["items"]
    total_pages = data["data"]["totalItems"] // 100 + 2
    for page in range(2, total_pages):
        response = session.get(
            add_or_replace_parameter(start_url, "pageIndex", str(page)), headers=headers
        )
        data = json.loads(response.text)
        all_locations += data["data"]["items"]

    for poi in all_locations:
        street_address = poi["addressLine1"]
        if poi.get("addressLine2"):
            street_address += " " + poi["addressLine2"]
        time = str(poi["openingDate"])
        location_type = ""
        if datetime.fromisoformat(time) > datetime.now(timezone.utc):
            location_type = "coming soon"
        hoo = []
        days_dict = {
            0: "Sunday",
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
        }
        if poi.get("days"):
            for elem in poi["days"]:
                day = days_dict[elem["day"]]
                opens = elem["openingTime"]
                closes = elem["closingTime"]
                hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        store_url = "https://www.spacesworks.com/{}/{}/".format(
            poi["city"].replace(" ", "-").lower(), poi["name"].lower().replace(" ", "-")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi.get("state"),
            zip_postal=poi.get("postalCode"),
            country_code=poi.get("countryId"),
            store_number=poi["id"],
            phone=poi.get("phone"),
            location_type=location_type,
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
