from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.samsung.com/us/samsung-experience-store/locations/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='container info-component']")

    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        if "– Grand" in location_name:
            location_name = location_name.split("– Grand")[0].strip()
        line = d.xpath(".//h3[@class='title']/text()")
        line = list(filter(None, [li.strip() for li in line]))
        if line[-1][-1].isalpha():
            line.pop()

        street_address = ", ".join(line[:-1])
        csz = line.pop()
        city = csz.split(", ")[0]
        sz = csz.split(", ")[1]
        state, postal = sz.split()
        country_code = "US"
        page_url = "".join(d.xpath(".//a[@class='cta-button']/@href"))
        phone = "".join(d.xpath(".//a[@class='phone-number']/text()")).strip()

        text = "".join(d.xpath(".//a[@class='header-cta']/@href"))
        try:
            latitude, longitude = text.split("/@")[1].split(",")[:2]
        except IndexError:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        _tmp = []
        hours = d.xpath(".//p[contains(text(), 'hours')]/following-sibling::p/text()")
        for h in hours:
            if not h.strip():
                continue
            if "pick" in h:
                break
            _tmp.append(h.strip())

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
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.samsung.com/us/samsung-experience-store/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
