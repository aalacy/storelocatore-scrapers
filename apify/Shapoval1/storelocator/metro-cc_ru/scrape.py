from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.metro-cc.ru/"
    api_url = "https://www.metro-cc.ru/sxa/search/results?s={0F3B38A3-7330-4544-B95B-81FC80A6BB6F}&sig=store-locator&o=Title%2CAscending&p=10000&v={BECE07BD-19B3-4E41-9C8F-E9D9EC85574F}&itemid=5457cad1-1fc2-4087-9726-268bc617ac74&q=&g="
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js["Results"]:
        latitude = j.get("Geospatial").get("Latitude")
        longitude = j.get("Geospatial").get("Longitude")
        info = j.get("Html")
        a = html.fromstring(info)
        hours_of_operation = (
            " ".join(a.xpath('//div[@class="hours-details"]/div/div//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

        slug = "".join(j.get("Url")).split("/")[-1]
        page_url = f"https://www.metro-cc.ru/torgovye-centry/{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = (
            "".join(tree.xpath('//a[@class="store-address"]/text()'))
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        location_name = "".join(tree.xpath('//h1[@class="store-name"]/text()'))
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        postal = ad.split(",")[-1].strip()
        country_code = "RU"
        city = a.city or "<MISSING>"
        phone = (
            "".join(tree.xpath('//a[@class="store-phone"]/text()'))
            .replace("\n", "")
            .replace("тел.", "")
            .strip()
        )
        if phone.find(";") != -1:
            phone = phone.split(";")[0].strip()
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        if phone.find("(доб") != -1:
            phone = phone.split("(доб")[0].strip()
        if phone.find("доб") != -1:
            phone = phone.split("доб")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
