from concurrent import futures
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_phone(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    phone = "".join(
        tree.xpath(
            "//div[@class='row align-items-center']//a[contains(@href, 'tel:')]/text()"
        )
    ).strip()
    phone = (
        phone.replace(".", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
    )
    iscoming = False
    if tree.xpath("//span[contains(text(), 'COMING SOON')]"):
        iscoming = True

    return {"phone": phone, "page_url": page_url, "iscoming": iscoming}


def get_additional():
    out = dict()
    r = session.get("https://mayweather.fit/locations/")
    tree = html.fromstring(r.text)
    urls = tree.xpath("//a[@class='btn btn-hollow light']/@href")

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_phone, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            _tmp = future.result()
            out[_tmp["phone"]] = _tmp

    return out


def fetch_data(sgw: SgWriter):
    _tmp = get_additional()
    api = "https://mayweather.fit/wp-admin/admin-ajax.php?action=cr_load_map_locations"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        phone = j.get("Phone")
        phone = (
            phone.replace(".", "")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
        )
        p = _tmp.get(phone) or {}
        a = j.get("Address") or {}
        l = j.get("Location") or {}
        location_name = j.get("Name")
        page_url = p.get("page_url")

        store_number = j.get("Id")
        street_address = a.get("Street")
        city = a.get("City")
        state = a.get("StateProv")
        postal = a.get("PostalCode")
        country_code = "US"
        latitude = l.get("lat")
        longitude = l.get("lng")

        if p.get("iscoming"):
            hours_of_operation = "Coming Soon"
        else:
            hours_of_operation = SgRecord.MISSING

        if "Your" in phone:
            continue

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://mayweather.fit/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
