from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(url):
    _tmp = []
    r = session.get(url)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='location__hours__container']/div[last()]/div[contains(@class, 'location__hours__day')]"
    )

    for d in divs:
        day = "".join(d.xpath("./span[1]//text()")).strip()
        time = "".join(d.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp) or "<MISSING>"


def get_tree(url):
    r = session.get(url)
    tree = html.fromstring(r.text)
    return tree


def get_phone(url):
    tree = get_tree(url)
    kurl = tree.xpath("/html/head/script/@src")[-1]
    if kurl.startswith("/"):
        kurl = f"https://smartstopselfstorage.com{kurl}"
    r = session.get(kurl)
    try:
        phone = (r.text.split('"phone":')[1]).split(",")[0].replace('"', "")
    except IndexError:
        phone = SgRecord.MISSING

    return phone


def fetch_data(sgw: SgWriter):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    api_url = "https://smartstopselfstorage.com/umbraco/rhythm/locationsapi/findlocations?size=&latitude=36.563752659280766&longitude=-73.941626814556&radius=3915.6025249727622&culture=en-us"

    r = session.get(api_url, headers=headers)
    js = r.json()["items"]

    for j in js:
        street_address = j.get("address1") or SgRecord.MISSING
        csz = j.get("address2")
        city = csz.split(",")[0].strip()
        csz = csz.split(",")[1].strip()
        state = csz.split()[0]
        if state == "ONT":
            state = "ON"
        postal = csz.split(state)[1].replace("T ", "").strip()

        country_code = "US"
        if len(postal) > 5 or not postal.isdigit():
            country_code = "CA"
        slug = j.get("url") or ""
        page_url = f"https://smartstopselfstorage.com{slug}"
        location_name = f"Self Storage in {city} {state}"
        phone = j.get("phone") or get_phone(page_url)
        latitude = j.get("latitude") or SgRecord.MISSING
        longitude = j.get("longitude") or SgRecord.MISSING
        hours_of_operation = get_hours(page_url)

        row = SgRecord(
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://smartstopselfstorage.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
