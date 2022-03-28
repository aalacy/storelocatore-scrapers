from lxml import html
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
    postal = adr.postcode or SgRecord.MISSING

    return street, postal


def fetch_data(sgw: SgWriter):
    api = "https://stores.myvi.in//curlLoadMorePagination.php"

    for i in range(1, 10000):
        data = {"page": str(i)}
        r = session.post(api, headers=headers, data=data)
        js = r.json()["response"]["outlets"]

        for j in js:
            j = j["outlet"]
            adr_source = j.get("address_as_html") or "<html/>"
            tree = html.fromstring(adr_source)
            raw_address = " ".join(" ".join(tree.xpath("//text()")).split())
            street_address, postal = get_international(raw_address)
            city = j.get("city")
            state = j.get("state")
            country_code = "IN"
            store_number = j.get("uid")
            location_name = j.get("business_name")
            page_url = j.get("busniess_name_anchar_url")
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")

            _tmp = []
            hours_source = j.get("business_hours_as_html") or "<html/>"
            root = html.fromstring(hours_source)
            hours = root.xpath("//ul/li")
            for h in hours:
                day = "".join(h.xpath("./span[1]//text()")).strip()
                inter = "".join(h.xpath("./span[2]//text()")).strip()
                _tmp.append(f"{day}: {inter}")

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

        if len(js) < 6:
            break


if __name__ == "__main__":
    locator_domain = "https://vodafone.in/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://stores.myvi.in/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://stores.myvi.in",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
