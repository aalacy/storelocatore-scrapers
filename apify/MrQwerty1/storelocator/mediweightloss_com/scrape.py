from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo(page_url):
    _tmp = []
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='box-content']//li[./span/i]")
    for d in divs:
        day = "".join(d.xpath("./span[1]//text()")).strip()
        inter = "".join(d.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day}: {inter}")

    return " ".join(";".join(_tmp).split())


def fetch_data(sgw: SgWriter):
    api = "https://mediweightloss.com/api/clinics/"
    r = session.get(api, headers=headers)
    js = r.json()["clinics"]

    for j in js:
        store_number = j.get("weight_loss")
        if not j.get("active") or not store_number:
            continue
        location_name = j.get("name") or ""
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        slug = location_name.lower().replace(" ", "-").replace(".", "").replace("/", "")
        page_url = f"https://mediweightloss.com/locations/{slug}"
        postal = j.get("zip")
        state = j.get("state")
        city = j.get("city")
        street_address = f'{j.get("address_1")} {j.get("address_2") or ""}'.strip()
        country_code = j.get("country")
        phone = j.get("phone")
        try:
            hours_of_operation = get_hoo(page_url)
        except:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://mediweightloss.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
