from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bodystreet.us"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Origin": "https://www.bodystreet.us",
        "Connection": "keep-alive",
        "Referer": "https://www.bodystreet.us/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
    }

    params = {
        "lang": "en",
        "site": "60757f830034a5d6b657b643",
    }

    json_data = {
        "itemTypes": [
            "entry",
        ],
        "searchTerm": "",
        "size": 50,
        "from": 0,
        "exactSearch": False,
        "categoryFilter": [
            {
                "type": "or",
                "items": [
                    "5f563083e3dd66054dd93b3d",
                ],
            },
            {
                "type": "or",
                "items": [],
            },
        ],
        "tagFilter": [],
        "location": None,
        "sort": None,
        "geoDistance": None,
        "enableMaxRange": False,
        "highlightFields": [
            "title",
        ],
        "aggregations": True,
        "showMarkers": True,
    }

    r = session.post(
        "https://www.bodystreet.com/api/v1/entries/entrysearch",
        params=params,
        headers=headers,
        json=json_data,
    )
    js = r.json()["hits"]

    for j in js:
        slug = j.get("slug")
        a = j.get("address")
        page_url = f"https://www.bodystreet.at/studio/{slug}"
        location_name = j.get("title")
        street_address = (
            f"{a.get('street')} {a.get('houseNumber')}".replace("None", "")
            .replace("Ave 947", "Ave")
            .strip()
        )
        postal = a.get("zip")
        country_code = "US"
        city = a.get("city")
        state = "<MISSING>"
        if str(postal).find(" ") != -1:
            state = str(postal).split()[0].strip()
            postal = str(postal).split()[1].strip()
        latitude = j.get("geoPoint").get("lat")
        longitude = j.get("geoPoint").get("lon")
        phone = j.get("contact").get("phone")
        hours_of_operation = "<MISSING>"

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "application/json",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/json",
            "Origin": "https://www.bodystreet.us",
            "Connection": "keep-alive",
            "Referer": "https://www.bodystreet.us/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
        }

        r = session.get(
            f"https://www.bodystreet.com/api/v1/entries/entryslug/{slug}",
            headers=headers,
        )
        js = r.json()
        hours = js.get("openingHoursData").get("data").get("include")
        tmp = []
        if hours:
            for h in hours:
                day = (
                    str(h.get("dayoption"))
                    .replace("0", "Sonntag")
                    .replace("1", "Montag")
                    .replace("2", "Dienstag")
                    .replace("3", "Mittwoch")
                    .replace("4", "Donnerstag")
                    .replace("5", "Freitag")
                    .replace("6", "Samstag")
                    .replace("8", "Alle Tage (Mo-Mo)")
                    .replace("9", "Alle Werktage (Mo-Fr)")
                    .replace("10", "Alle Tage auÃŸer Sonntags (Mo-Sa)")
                )
                opens = h.get("opening_from")
                closes = h.get("opening_to")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
