from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo():
    hoo = dict()
    api = "https://holidaymarket.storebyweb.com/s/1000-21/api/cs/1000-74"
    r = session.get(api, headers=headers)
    source = r.json()["content"]
    tree = html.fromstring(source)
    divs = tree.xpath("//a[not(contains(@href, 'tel:'))]")

    for d in divs:
        _id = "".join(d.xpath("./@href")).split("/")[-1]
        lines = d.xpath("./preceding-sibling::div/text()")
        ho = SgRecord.MISSING
        for li in lines:
            if "Open" in li:
                ho = li.replace(".", "").replace("Open", "").strip()
        hoo[_id] = ho

    return hoo


def fetch_data(sgw: SgWriter):
    hoo = get_hoo()
    api = "https://holidaymarket.storebyweb.com/s/1000-28/api/stores"
    r = session.get(api, headers=headers)
    js = r.json()["data"]

    for j in js:
        try:
            a = j["addresses"][0]
        except:
            a = dict()

        adr1 = a.get("street1") or ""
        adr2 = a.get("street2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("city")
        state = a.get("state")
        postal = a.get("postal")
        country_code = a.get("country")
        store_number = j.get("id")
        page_url = f"https://holidaymarket.storebyweb.com/s/{store_number}"
        location_name = j.get("name")
        phone = j["phones"][0]["phone"]
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = hoo.get(store_number)

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
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://holidaymarket.storebyweb.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
