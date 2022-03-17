import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import International_Parser, parse_address

locator_domain = "https://www.mannings.com.hk/"


def fetch_data(sgw: SgWriter):

    api_url = "https://www.mannings.com.hk/store-finder/storefilter?q=&page=0&pharmacySelectedOption=&areaSelectedOption=&Selectedservices=&storetype=mannings&selectedPickableOption=&userLat=&userLong="
    with SgFirefox() as driver:
        driver.get(api_url)

        js_block = driver.find_element_by_xpath("//body").text
        js = json.loads(js_block)
        for j in js["data"]:

            page_url = "https://www.mannings.com.hk/store-finder"
            ad = f"{j.get('line1')} {j.get('town')} {j.get('region')}"
            location_name = j.get("name")
            a = parse_address(International_Parser(), ad)
            street_address = j.get("line1")
            state = a.state or "<MISSING>"
            state = state.replace("N.T New Territories", "N.T").replace(
                "New Territories New Territories", "New Territories"
            )
            postal = a.postcode or "<MISSING>"
            country_code = "HK"
            city = a.city or "<MISSING>"
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            location_type = "GNC"
            phone = j.get("phone")
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            hours_of_operation = "<MISSING>"
            hours = j.get("openings")
            tmp = []
            if hours:
                for d in days:
                    day = d
                    times = j.get("openings").get(f"{d}")
                    line = f"{day} {times}"
                    tmp.append(line)
                hours_of_operation = (
                    "; ".join(tmp).replace("Sat  - ; Sun  -", "").strip() or "<MISSING>"
                )
            if str(location_name).find("Temporarily closed") != -1:
                hours_of_operation = "Temporarily closed"

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
