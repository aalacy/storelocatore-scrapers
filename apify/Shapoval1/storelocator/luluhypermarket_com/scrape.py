from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.luluhypermarket.com/en-ae/"
    api_url = "https://www.luluhypermarket.com/en-ae/store-finder"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="dropdown-menu country-dropdown "]/a')
    for d in div:
        country_code = "".join(d.xpath(".//@data-isocode")).upper()
        slug_url = "".join(d.xpath(".//@data-url"))
        country_url = f"https://www.luluhypermarket.com{slug_url}"
        r = session.get(country_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//select[@id="storelocator-query"]/option[position()>1]')
        for d in div:
            city = "".join(d.xpath(".//text()"))
            city_slug = "".join(d.xpath(".//@value"))
            for i in range(0, 10):
                api_url = f"https://www.luluhypermarket.com{slug_url}?q={city_slug}&page={i}&latitude=0&longitude=0"
                r = session.get(api_url, headers=headers)
                try:
                    js = r.json()["data"]
                except:
                    continue
                for j in js:
                    page_url = "https://www.luluhypermarket.com/en-ae/store-finder"
                    location_name = j.get("displayName") or "<MISSING>"
                    street_address = j.get("line1") or "<MISSING>"
                    if street_address == "<MISSING>":
                        street_address = j.get("line2") or "<MISSING>"
                    postal = j.get("postalCode") or "<MISSING>"
                    store_number = j.get("name")
                    latitude = j.get("latitude") or "<MISSING>"
                    longitude = j.get("longitude") or "<MISSING>"
                    phone = (
                        "".join(j.get("phone"))
                        .replace("Tel:", "")
                        .replace("Phone:", "")
                        .strip()
                        or "<MISSING>"
                    )

                    row = SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=SgRecord.MISSING,
                        zip_postal=postal,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=SgRecord.MISSING,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=SgRecord.MISSING,
                    )

                    sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
