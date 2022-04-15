from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords(url):
    r = session.get(url, headers=headers)
    if r.status_code != 200:
        return SgRecord.MISSING, SgRecord.MISSING
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//a[contains(@href, 'map')]/@href"))

    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def fetch_data(sgw: SgWriter):
    api = "https://exercisecoach.com/find-a-studio/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='wpb_text_column wpb_content_element ']")

    for d in divs:
        location_name = "".join(d.xpath(".//div[@class='StudioName']/a/text()")).strip()
        page_url = "".join(d.xpath(".//div[@class='StudioName']/a/@href"))
        line = d.xpath(".//div[@class='StudioAddress']//text()")
        line = list(filter(None, [li.replace("\xa0", "").strip() for li in line]))

        index = 0
        for li in line:
            if "@" in li:
                break
            index += 1

        line = line[:index]
        phone = line.pop()
        csz = line.pop()
        street_address = " ".join(line).strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = csz.split(", ")[0]
        sz = csz.split(", ")[1]
        state = sz[:2]
        postal = sz.replace(state, "").replace(".", "").strip()
        country_code = "US"
        latitude, longitude = get_coords(page_url)

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
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://exercisecoach.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
