import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "precisiontune.com"
    start_url = "https://www.precisiontune.com/modules/location/ajax.aspx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    scraped_urls = []

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    for state in states:
        formdata = {
            "StartIndex": "0",
            "EndIndex": "10000",
            "Longitude": "",
            "Latitude": "",
            "StateCode": state,
            "CountryCode": "US",
            "ZipCode": "",
            "City": "",
            "RangeInMiles": "50",
            "F": "GetNearestLocations",
        }
        response = session.post(start_url, data=formdata)
        data = json.loads(response.text)

        for poi in data["Locations"]:
            store_url = "https://www.precisiontune.com" + poi["CustomUrl"]
            if store_url in scraped_urls:
                continue
            scraped_urls.append(store_url)
            location_name = poi["Name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["Address1"]
            if poi["Address2"]:
                street_address += ", " + poi["Address2"]
            street_address = street_address if street_address else "<MISSING>"

            store_response = session.get(store_url, headers=hdr)
            if store_response.status_code != 200:
                continue
            store_dom = etree.HTML(store_response.text)
            cs = store_dom.xpath(
                '//span[contains(text(), "GRAND OPENING COMING SOON!")]'
            )
            if cs:
                continue
            city = poi["City"]
            city = city if city else "<MISSING>"
            state = poi["State"]
            state = state if state else "<MISSING>"
            zip_code = poi["Zip"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["Country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = ""
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["Phone"]
            phone = phone if phone else "<MISSING>"
            location_type = ""
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["Latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["Longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = [
                elem.strip()
                for elem in store_dom.xpath('//div[@class="hours"]//text()')
                if elem.strip()
            ]
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

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
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
