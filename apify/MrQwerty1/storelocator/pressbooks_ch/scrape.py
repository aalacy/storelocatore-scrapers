from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_geo(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    try:
        lat, lng = "".join(tree.xpath("//div/@data-geolocation")).split(",")
    except:
        lat, lng = SgRecord.MISSING, SgRecord.MISSING

    return lat, lng


def get_phone(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]/text()"))
    if not phone:
        phone = (
            "".join(tree.xpath("//p[contains(text(), 'Telefon')]/text()"))
            .replace("Telefon", "")
            .strip()
        )

    return phone


def fetch_data(sgw: SgWriter):
    api = "https://www.pressbooks.ch/about/filialen?bpmbutton127365-0-141538:65370=1&bpmtoken=NqsKV3s7IV"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@data-template='infoBox']")

    for d in divs:
        location_name = "".join(d.xpath(".//span[@class='storeTitle']/text()")).strip()
        if "(" in location_name:
            location_name = location_name.split("(")[0].strip()
        street_address = "".join(d.xpath(".//span[@class='sVenue']/text()")).strip()
        city = "".join(d.xpath(".//span[@class='sCity']/text()")).strip()
        postal = "".join(d.xpath(".//span[@class='sZip']/text()")).strip()
        country_code = "CH"
        store_number = "".join(d.xpath("./@id")).split(":")[-1]
        slug = "".join(d.xpath(".//span[@class='storeDetailLink']/a/@href"))
        key = slug.split("detail/")[1].split("-")[0]
        page_url = f"https://www.pressbooks.ch{slug}"
        try:
            latitude, longitude = "".join(
                tree.xpath(f".//li[@data-marker='{key}']/@data-latlng")
            ).split(",")
        except:
            latitude, longitude = get_geo(page_url)

        phone = SgRecord.MISSING
        location_type = "Kiosk"
        if "kiosk" not in page_url:
            location_type = "Press Books"
            try:
                phone = get_phone(page_url)
            except:
                phone = SgRecord.MISSING

        _tmp = []
        hours = d.xpath(
            ".//div[@class='openingHours']//span[@class='value']/span/text()"
        )
        for h in hours:
            if "andere" in h or not h.strip():
                continue
            _tmp.append(h.strip())

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            location_type=location_type,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.pressbooks.ch/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
