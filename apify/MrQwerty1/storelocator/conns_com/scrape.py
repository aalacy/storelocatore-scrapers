from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://stores.conns.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@id='storeList']/div")

    for d in divs:
        location_name = "".join(d.xpath("./div[@class='listing-title']/text()")).strip()
        page_url = "".join(d.xpath("./div[@class='storemapdata']/@data-url"))

        line = d.xpath("./div[@class='listing-address']/a/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        if street_address.endswith(","):
            street_address = street_address[:-1]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "".join(d.xpath("./div[@class='storemapdata']/@data-storeid"))
        phone = "".join(d.xpath("./div[@class='listing-phone']/a/text()")).strip()

        try:
            latitude, longitude = "".join(
                d.xpath("./div[@class='storemapdata']/@data-location")
            ).split(",")
        except IndexError:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        _tmp = []
        try:
            hours = d.xpath(".//ul[@class='toggle-time2 store-specific-hours']")[
                0
            ].xpath(".//li[./span]")
        except:
            hours = []

        for h in hours:
            day = "".join(h.xpath("./span[1]/text()")).strip()
            inter = "".join(h.xpath("./span[2]/text()")).strip()
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp) or "Closed"

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
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://conns.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
