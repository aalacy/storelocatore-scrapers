import re
import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data():
    session = SgRequests()
    start_url = "https://www.geocms.it/Server/servlet/S3JXServletCall?parameters=method_name%3DGetObject%26callback%3Dscube.geocms.GeoResponse.execute%26id%3D7%26query%3D%255BcountryCode%255D%2520%253D%2520%255B{}%255D%26clear%3Dtrue%26licenza%3Dgeo-todsgroupspa%26progetto%3DTods%26lang%3DALL&encoding=UTF-8"
    domain = "https://www.tods.com/"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get(
        "https://www.tods.com/etc/designs/todssite/statics/geocms/language/en_GB.js?fdsf=",
        headers=hdr,
    )
    countries = re.findall(r"COUNTRY_LABEL\['(.+?)'\] =", response.text)
    for country in countries:
        response = session.get(start_url.format(country), headers=hdr)
        data = re.findall(r'GeoResponse.execute\((.+),"",7\)', response.text)
        if not data:
            continue
        data = json.loads(json.loads(data[0]))

        for poi in data["L"][0]["O"]:
            poi = poi["U"]
            store_url = "https://www.tods.com/us-en/store-locator.html"
            location_name = poi["name"]
            info = poi.get("timeTable")
            street_address = poi["address"].replace("\n", " ").strip()
            city = poi["city"]
            state = poi.get("region")
            if state == "Other" or state == "x" or state == "13":
                state = ""
            zip_code = poi.get("zipCode")
            phone = poi.get("phone")
            latitude = poi["latitiude"]
            longitude = poi["longitude"]
            country_code = poi["countryCode"]
            if country_code == "AU" and len(zip_code.split()) == 2:
                state = zip_code.split()[0].strip()
                zip_code = zip_code.split()[1].strip()
            days_dict = {
                "1": "Monday",
                "2": "tuesday",
                "3": "wednesday",
                "4": "thursday",
                "5": "friday",
                "6": "saturday",
                "7": "sunday",
            }
            hoo = []
            if poi["G"].get("hours"):
                for elem in poi["G"]["hours"]:
                    day = days_dict[elem["day"]]
                    if elem.get("From1"):
                        opens = elem["From1"]
                        closes = elem["To1"]
                        hoo.append(f"{day} {opens} - {closes}")
                    else:
                        hoo.append(f"{day} closed")
            hours_of_operation = " ".join(hoo) if hoo else ""
            if info and "closed" in info:
                hours_of_operation = "Closed"

            if country_code == "PR":
                state = "PR"
                country_code = "US"

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=poi["shopCode"],
                phone=phone,
                location_type="",
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
