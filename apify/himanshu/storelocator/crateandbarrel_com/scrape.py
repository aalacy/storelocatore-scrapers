import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.crateandbarrel.com/"
    api_url = "https://www.crateandbarrel.com/stores/list-state/retail-stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="dd"]/ul/li//a')
    for d in div:

        location_type = "".join(d.xpath(".//text()"))
        location_type_url = "".join(d.xpath(".//@href"))
        r = session.get(location_type_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="state-list"]//ul//li//a')
        for d in div:

            state = "".join(d.xpath(".//text()"))
            state_url_slug = "".join(d.xpath(".//@href"))
            state_url = f"https://www.crateandbarrel.com{state_url_slug}"
            r = session.get(state_url, headers=headers)
            tree = html.fromstring(r.text)
            div = tree.xpath(
                '//div[@class="responsive-stores stores-search-results list-state content-layout"]/script/text()'
            )
            for d in div:

                js = json.loads(str(d))
                location_name = js.get("name") or "<MISSING>"
                a = js.get("address")
                street_address = a.get("streetAddress") or "<MISSING>"
                postal = a.get("postalCode") or "<MISSING>"
                country_code = a.get("addressCountry") or "<MISSING>"
                city = a.get("addressLocality") or "<MISSING>"
                try:
                    latitude = js.get("geo").get("latitude")
                    longitude = js.get("geo").get("longitude")
                except:
                    latitude, longitude = "<MISSING>", "<MISSING>"
                phone = js.get("telephone") or "<MISSING>"
                hours_of_operation = " ".join(js.get("openingHours"))
                page_url_slug = "".join(
                    tree.xpath(f'//a[./h2[text()="{location_name}"]]/@href')
                )
                page_url = f"https://www.crateandbarrel.com{page_url_slug}"
                try:
                    store_number = page_url.split("/str")[1].strip()
                except:
                    store_number = "<MISSING>"

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
