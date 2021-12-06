import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from sglogging import sglog

locator_domain = "https://ashleyfurniturestore.co.nz/"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetch_data(sgw: SgWriter):

    api_url = "https://shy.elfsight.com/p/boot/?a=&callback=__esappsPlatformBoot1638455246306&shop=ashley-furniture-homestore-new-zealand.myshopify.com&w=698b9be0-bef6-11e9-9eea-a35d26055ef1"
    log.info(f"Api URL: {api_url}")
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    try:
        r = SgRequests.raise_on_err(session.get(api_url, headers=headers))
        div = r.text.split("esappsPlatformBoot1638455246306(")[1].split(");")[0].strip()
        js = json.loads(div)
        for j in js["data"]["widgets"].values():
            info = j.get("data").get("settings").get("markers")
            for i in info:
                location_name = str(i.get("infoTitle")) or "<MISSING>"
                ad = str(i.get("infoAddress"))
                a = parse_address(International_Parser(), ad)
                street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                    "None", ""
                ).strip()
                state = a.state or "<MISSING>"
                postal = a.postcode or "<MISSING>"
                country_code = "NZ"
                city = location_name.split("-")[1].strip()
                coordinates = str(i.get("coordinates"))
                latitude = coordinates.split(",")[0].strip()
                longitude = coordinates.split(",")[1].strip()
                phone_info = i.get("infoDescription")
                l = html.fromstring(phone_info)
                page_url = "".join(l.xpath("//a/@href"))
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                phone = (
                    "".join(tree.xpath('//a[contains(@href, "tel")]/@href'))
                    .replace("tel:", "")
                    .strip()
                    or "<MISSING>"
                )
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//h3[./strong[text()="Store Hours"]]/following-sibling::p[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )

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
                    hours_of_operation=hours_of_operation,
                    raw_address=ad,
                )

                sgw.write_row(row)

    except Exception as e:
        log.info(f"Err at #L100: {e}")


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
