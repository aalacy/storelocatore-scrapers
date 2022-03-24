from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    if len(street) < 5:
        street = line.split(",")[0].strip()

    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://sostrenegrene.com/umbraco/api/store/search?latitude=0&longitude=0"
    params = [
        "en-GB",
        "da-DK",
        "fr-FR",
        "nl-NL",
        "de-AT",
        "nl-BE",
        "de-CH",
        "de-DE",
        "en-IE",
        "nb-NO",
        "sv-SE",
        "en-FI",
    ]

    for param in params:
        headers = {"culture": param}
        r = session.get(api, headers=headers)
        js = r.json()["stores"]

        for j in js:
            j = j.get("store")

            raw_address = j.get("address")
            street_address, city, state, postal = get_international(raw_address)
            country_code = param.split("-")[-1]
            store_number = j.get("id")
            page_url = f'https://sostrenegrene.com{j.get("url")}'
            location_name = j.get("name")
            phone = j.get("phone")
            loc = j.get("location")
            latitude = loc.get("latitude")
            longitude = loc.get("longitude")

            _tmp = []
            days = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            hours = j.get("openingHours") or []
            if len(hours) > 7:
                hours = hours[:7]

            for h in hours:
                index = h.get("dayOfWeek")
                day = days[index]

                start = h.get("opens")
                if start:
                    end = h.get("closes")
                    _tmp.append(f"{day}: {start}-{end}")
                else:
                    _tmp.append(f"{day}: Closed")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://sostrenegrene.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
