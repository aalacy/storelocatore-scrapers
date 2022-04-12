import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jysk.com/"
    api_url = "https://www.jysk.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="menu menu--jysk-nordic nav"]/li/a')
    for d in div:
        country_url = "".join(d.xpath(".//@href"))
        if country_url == "https://jysk.ru/":
            continue
        if country_url == "https://jysk.ua/":
            continue
        country_code = "".join(d.xpath(".//text()"))
        r = session.get(country_url)
        tree = html.fromstring(r.text)
        slug = "".join(
            tree.xpath('//div[@class="mb-4 mb-md-0 col-sm-3 col-6"][2]//a/@href')
        )
        single_page_url = f"{country_url}{slug}".replace("//", "/").replace(
            "https:/", "https://"
        )
        r = session.get(single_page_url)
        tree = html.fromstring(r.text)
        js_block = (
            "".join(
                tree.xpath(
                    "//div[@data-jysk-react-properties]/@data-jysk-react-properties"
                )
            )
            .split('storesCoordinates":')[1]
            .split(',"initialPapersCatalogueBlock"')[0]
            .strip()
        )
        js = json.loads(js_block)
        for j in js:
            location_name = j.get("name")
            latitude = j.get("lat")
            longitude = j.get("lng")
            store_number = j.get("id")
            api_page_url = f"{country_url}/services/store/get/{store_number}".replace(
                "//", "/"
            ).replace("https:/", "https://")
            r = session.get(api_page_url)
            js = r.json()

            page_url = f"{country_url}/stores-locator?storeId={store_number}".replace(
                "//", "/"
            ).replace("https:/", "https://")
            location_type = "<MISSING>"
            try:
                street_address = f"{js.get('street')} {js.get('house')}".strip()
                state = "<MISSING>"
                postal = js.get("zipcode")
                city = js.get("city")
                phone = js.get("tel") or "<MISSING>"
                hours = js.get("opening")
                tmp = []
                for h in hours:
                    day = (
                        "".join(h.get("day"))
                        .replace("0", "Sunday")
                        .replace("1", "Monday")
                        .replace("2", "Tuesday")
                        .replace("3", "Wednesday")
                        .replace("4", "Thursday")
                        .replace("5", "Friday")
                        .replace("6", "Saturday")
                    )
                    time = h.get("format_time")
                    line = f"{day} {time}"
                    if line == "Sunday 0:00 - 24:00":
                        line = "Sunday Closed"
                    tmp.append(line)
                hours_of_operation = "; ".join(tmp)
            except:
                street_address, city, state, postal, phone, hours_of_operation = (
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                )
            if street_address == "<MISSING>":
                continue

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
