from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mountpleasantgroup.com/"
    api_url = "https://www.mountpleasantgroup.com/en-CA/Locations.aspx"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[./div[@class="row rowitemheight "]]')
    for d in div:

        page_url = "".join(d.xpath('.//div[@class="product-image"]/a/@href'))
        if page_url.find("http") == -1:
            page_url = f"https://www.mountpleasantgroup.com{page_url}"

        location_name = "".join(d.xpath(".//h3/text()"))
        if location_name == "About Our Cremation Centres":
            continue
        ad = (
            " ".join(d.xpath(".//text()"))
            .replace("\r", "")
            .replace("\n", "")
            .replace("\t", "")
            .strip()
        )
        adr = ad.split(f"{location_name}")[1].split("Tel")[0].strip()
        a = parse_address(International_Parser(), adr)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        city = a.city or "<MISSING>"
        if street_address.find("mississauga") != -1:
            street_address = street_address.replace("mississauga", "").strip()
            city = "Mississauga"
        phone = ad.split("Tel")[1].split("Fax")[0].replace(":", "").strip()

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        latitude = "".join(tree.xpath("//input/@data-latlng")).split(",")[0].strip()
        longitude = "".join(tree.xpath("//input/@data-latlng")).split(",")[1].strip()

        row = SgRecord(
            locator_domain=locator_domain,
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
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
