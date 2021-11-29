import re
import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

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
        data = json.loads(json.loads(data[0]))["L"][0]["O"]
        for poi in data:

            store_url = "https://www.tods.com/us-en/store-locator.html"
            location_name = poi.get("U").get("name") or "<MISSING>"
            info = poi.get("U").get("timeTable") or "<MISSING>"
            street_address = (
                "".join(poi.get("U").get("address")).replace("\n", " ").strip()
                or "<MISSING>"
            )
            city = poi.get("U").get("city") or "<MISSING>"
            state = poi.get("U").get("region") or "<MISSING>"
            if state == "Other" or state == "x" or state == "13":
                state = "<MISSING>"
            zip_code = str(poi.get("U").get("zipCode")) or "<MISSING>"
            if zip_code == "None":
                zip_code = "<MISSING>"
            phone = poi.get("U").get("phone") or "<MISSING>"
            latitude = poi.get("U").get("latitiude") or "<MISSING>"
            longitude = poi.get("U").get("longitude") or "<MISSING>"
            country_code = poi.get("U").get("countryCode") or "<MISSING>"
            if country_code == "AU":
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
            if poi["U"]["G"].get("hours"):
                for elem in poi["U"]["G"]["hours"]:
                    day = days_dict[elem["day"]]
                    if elem.get("From1"):
                        opens = elem["From1"]
                        closes = elem["To1"]
                        hoo.append(f"{day} {opens} - {closes}")
                    else:
                        hoo.append(f"{day} closed")
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
            if "closed" in info:
                hours_of_operation = "Closed"

            if country_code == "PR":
                state = "PR"
                country_code = "US"

            row = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
