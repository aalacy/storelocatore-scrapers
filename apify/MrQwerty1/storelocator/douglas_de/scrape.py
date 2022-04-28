from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_name(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    return "".join(
        tree.xpath("//h1[@class='headline-bold store-detail-page__title']/text()")
    ).strip()


def fetch_data(sgw: SgWriter):
    apis = [
        "https://www.douglas.de/api/v2/stores?fields=FULL&pageSize=1000&sort=asc",
        "https://www.douglas.pl/api/v2/stores?fields=FULL&pageSize=1000&sort=asc",
        "https://www.douglas.at/api/v2/stores?fields=FULL&pageSize=1000&sort=asc",
        "https://www.douglas.ch/api/v2/stores?fields=FULL&pageSize=1000&sort=asc",
        "https://www.douglas.nl/api/v2/stores?fields=FULL&pageSize=1000&sort=asc",
    ]
    for api in apis:
        cc = api.split(".")[-1].split("/")[0]
        locator_domain = f"https://www.douglas.{cc}"
        r = session.get(api, headers=headers)
        js = r.json()["stores"]

        for j in js:
            a = j.get("address") or {}
            adr1 = a.get("line1") or ""
            adr2 = a.get("line2") or ""
            street_address = f"{adr1} {adr2}".strip()
            city = a.get("town")
            postal = a.get("postalCode")
            phone = a.get("phone")
            raw_address = a.get("formattedAddress")

            store_number = j.get("name")
            slug = j.get("url")
            page_url = f"{locator_domain}{slug}"
            location_name = j.get("displayName")
            if not location_name:
                location_name = get_name(page_url)

            g = j.get("geoPoint") or {}
            latitude = g.get("latitude")
            longitude = g.get("longitude")

            _tmp = []
            try:
                hours = j["openingHours"]["weekDayOpeningList"]
            except:
                hours = []

            for h in hours:
                day = h.get("weekDay")
                if h.get("closed"):
                    _tmp.append(f"{day}: Closed")
                    continue
                start = h["openingTime"]["formattedHour"]
                end = h["closingTime"]["formattedHour"]
                _tmp.append(f"{day}: {start}-{end}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=cc.upper(),
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.douglas.de",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Connection": "keep-alive",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
