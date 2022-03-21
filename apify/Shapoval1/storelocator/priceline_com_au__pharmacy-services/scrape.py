import time
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "priceline.com.au/pharmacy-services"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "X-Prototype-Version": "1.7",
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.priceline.com.au",
        "Connection": "keep-alive",
        "Referer": "https://www.priceline.com.au/store-locator",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = {"ajax": "1"}

    for i in range(1, 28):

        r = session.post(
            f"https://www.priceline.com.au/store-locator?page={i}",
            headers=headers,
            data=data,
        )
        time.sleep(5)
        try:
            js = r.json()["markers"]
        except:
            try:
                time.sleep(10)
                r = session.post(
                    f"https://www.priceline.com.au/store-locator?page={i}",
                    headers=headers,
                    data=data,
                )
                js = r.json()["markers"]
            except:
                continue

        for j in js:

            location_name = "".join(j.get("title")) or "<MISSING>"
            slug = location_name.lower().strip().replace(" ", "-")
            page_url = f"https://www.priceline.com.au/store-locator/{slug}"
            ad = "".join(j.get("address"))
            location_type = j.get("product_types")
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "AU"
            city = a.city or "<MISSING>"
            store_number = j.get("location_id")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            phone = "".join(j.get("phone")).replace("Phone:", "").strip() or "<MISSING>"
            hours_of_operation = (
                "".join(j.get("notes"))
                .replace("<br/>", " ")
                .replace("</br>", " ")
                .replace("<BR/>", "")
                .replace("<BR>", "")
                .replace("<br />", "")
                .replace("<br>", "")
                .replace("\n", " ")
                .replace("\r", " ")
                .strip()
            )
            if hours_of_operation.find("<p>") != -1:
                hours_of_operation = hours_of_operation.split("<p>")[0].strip()
            if hours_of_operation.find("<b>") != -1:
                hours_of_operation = hours_of_operation.split("<b>")[0].strip()
            hours_of_operation = hours_of_operation.replace("<", "")
            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
