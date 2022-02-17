from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://www.mcdonalds.com.pe/api/restaurantsByCountry"
    r = session.get(api, headers=headers, params=params)
    js = r.json()["content"]["restaurants"]

    for j in js:
        source = j.get("name") or "<html/>"
        tree = html.fromstring(source)
        text = tree.xpath("./text()")
        if len(text) == 1:
            t = text[0]
            if t.strip().endswith(","):
                location_name = t.split()[0].strip()
                raw_address = " ".join(t.split()[1:]).replace(",", "").strip()
            elif "< br/>" in t:
                location_name = t.split("< br/>")[0].strip()
                raw_address = t.split("< br/>")[1].strip()
            elif "\t" in t:
                location_name = t.split("\t")[0].strip()
                raw_address = t.split("\t")[1].strip()
            else:
                location_name = t
                raw_address = ""
        else:
            location_name = text[0].replace(",", "").strip()
            raw_address = " ".join(text[1].split())

        if not raw_address:
            raw_address = "".join(tree.xpath(".//small/text()")).strip()

        street_address, city, state, postal = get_international(raw_address)
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        store_number = j.get("id")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="PE",
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.mcdonalds.com.pe/"
    page_url = "https://www.mcdonalds.com.pe/locales"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.mcdonalds.com.pe/locales",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    params = (("country", "PE"),)

    session = SgRequests(verify_ssl=False)
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
