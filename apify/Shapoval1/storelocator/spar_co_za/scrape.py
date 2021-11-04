from sgpostal.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.spar.co.za/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.spar.co.za/Store-Finder",
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.spar.co.za",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    cities = ["Africa", "Namibia"]
    for c in cities:
        data = (
            '{"SearchText":"'
            + c
            + '","Types":["SPAR","SUPERSPAR","KWIKSPAR","SPAR Express","Savemor","Pharmacy","TOPS"],"Services":[]}'
        )

        r = session.post(
            "https://www.spar.co.za/api/stores/search", headers=headers, data=data
        )
        js = r.json()
        for j in js:
            slug = j.get("Alias")
            page_url = f"https://www.spar.co.za/Home/Store-View/{slug}"
            location_name = "".join(j.get("Name")) or "<MISSING>"
            location_type = j.get("Type") or "<MISSING>"
            street_address_info = (
                f"{j.get('PhysicalAddress')} {j.get('Suburb')}".strip() or "<MISSING>"
            )
            state = "<MISSING>"
            postal = "<MISSING>"
            street_address = "<MISSING>"
            city = "<MISSING>"
            country_code = "ZA"
            city_info = "".join(j.get("Town")) or "<MISSING>"
            ad = "<MISSING>"
            if street_address_info != "<MISSING>" and city_info != "<MISSING>":
                ad = street_address_info + " " + city_info
            if ad != "<MISSING>":
                a = parse_address(International_Parser(), ad)
                street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                    "None", ""
                ).strip()
                state = a.state or "<MISSING>"
                postal = a.postcode or "<MISSING>"
                city = a.city or "<MISSING>"
            if page_url.find("Botswana") != -1:
                state = "Botswana"
            if page_url.find("Botswana") != -1:
                state = "Botswana"
            if page_url.find("Eastern") != -1:
                state = "South Africa"
            if page_url.find("Namibia") != -1:
                state = "Namibia"
            if street_address.find("Otjiwarango") != -1:
                city = "Otjiwarango"
                street_address = street_address.replace("Otjiwarango", "").strip()
            if street_address == "<MISSING>":
                street_address = f"{j.get('PhysicalAddress')} {j.get('Suburb')}".strip()
            if ad.find("Windhoek") != -1 or street_address.find("Windhoek") != -1:
                city = "Windhoek"
            if street_address.find("Mariental") != -1:
                city = "Mariental"
                street_address = street_address.replace("Mariental", "").strip()
            if location_name != "Riteway Service Station" and city == "<MISSING>":
                city = location_name
                if city.find(" ") != -1:
                    city = city.split()[0].strip()
            if street_address.find("Swakopmund") != -1:
                city = "Swakopmund"
                street_address = street_address.replace("Swakopmund", "").strip()
            latitude = j.get("GPSLat") or "<MISSING>"
            longitude = j.get("GPSLong") or "<MISSING>"
            phone = "".join(j.get("TelephoneNumber")).strip() or "<MISSING>"
            hours_of_operation = (
                f"Mon to Fri {j.get('TradingHoursMonToFriOpen')} - {j.get('TradingHoursClose')} Sat {j.get('TradingHoursSatOpen')} - {j.get('TradingHoursSatClose')} Sun {j.get('TradingHoursSunOpen')} - {j.get('TradingHoursSunClose')}".strip()
                or "<MISSING>"
            )
            if hours_of_operation == "Mon to Fri  -  Sat  -  Sun  -":
                hours_of_operation = "<MISSING>"
            if hours_of_operation.find("Sun  -") != -1:
                hours_of_operation = hours_of_operation.replace("Sun  -", "Sun  Closed")

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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
