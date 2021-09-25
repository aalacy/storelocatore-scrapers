from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.amnb.com/"
    api_urls = [
        "https://www.amnb.com/_/api/branches/36.5868855/-79.3951675/500",
        "https://www.amnb.com/_/api/atms/36.5868855/-79.3951675/500",
    ]
    for api_url in api_urls:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        }

        r = session.get(api_url, headers=headers)
        try:
            js = r.json()["branches"]
        except:
            js = r.json()["atms"]
        for j in js:

            page_url = "https://www.amnb.com/about-us/locate-us"
            location_name = j.get("name") or "<MISSING>"
            location_type = "<MISSING>"
            if api_url.find("branches") != -1:
                location_type = "Branch"
            if api_url.find("atms") != -1:
                location_type = "Atm"
            ids = j.get("id")
            if location_name == "Yanceyville ATM" and ids == "14737496":
                location_name = "Yanceyville Atm"
            if location_name == "Gretna ATM" and ids == "14737490":
                location_name = "Gretna Atm"
            street_address = j.get("address") or "<MISSING>"
            state = j.get("state") or "<MISSING>"
            postal = j.get("zip") or "<MISSING>"
            country_code = "US"
            city = j.get("city") or "<MISSING>"
            latitude = j.get("lat") or "<MISSING>"
            longitude = j.get("lng") or "<MISSING>"
            phone = j.get("phone") or "<MISSING>"
            hours_of_operation = j.get("description") or "<MISSING>"
            if hours_of_operation != "<MISSING>":
                a = html.fromstring(hours_of_operation)
                hours_of_operation = " ".join(a.xpath("//*//text()"))
                if (
                    hours_of_operation.find("Hours:") != -1
                    and hours_of_operation.find("Drive") != -1
                ):
                    hours_of_operation = (
                        hours_of_operation.split("Hours:")[1].split("Drive")[0].strip()
                    )
                hours_of_operation = (
                    hours_of_operation.replace("Hour ATM Learn More", "")
                    .replace("(drive-thru until 5:30pm) ", "")
                    .strip()
                )
                if hours_of_operation.find("Hours By appointment") != -1:
                    hours_of_operation = "<MISSING>"
                if (
                    hours_of_operation.find("Hours:") != -1
                    and hours_of_operation.find("(") != -1
                ):
                    hours_of_operation = (
                        hours_of_operation.split("Hours:")[1].split("(")[0].strip()
                    )
                if hours_of_operation.find("Hours:") != -1:
                    hours_of_operation = hours_of_operation.split("Hours:")[1].strip()
                hours_of_operation = (
                    hours_of_operation.replace("*NOW DRIVE THRU ONLY*", "")
                    .replace("ATM available during business hours Learn More", "")
                    .replace("Hour ATM  Learn More", "")
                    .replace("No ATM Learn More", "")
                    .replace("24", "")
                    .replace("Hour ATM", "")
                    .replace("Sat:", "")
                    .strip()
                )

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
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
