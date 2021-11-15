from lxml import html
from sgpostal.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog

locator_domain = "http://wendysjamaica.com"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetch_data(sgw: SgWriter):

    api_url = "http://wendysjamaica.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    try:
        r = SgRequests.raise_on_err(session.get(api_url, headers=headers))
        log.info(f"## Response: {r}")
        tree = html.fromstring(r.text)
        div = tree.xpath("//div[./h4]")
        for d in div:

            page_url = "http://wendysjamaica.com/locations/"
            location_name = "".join(d.xpath("./h4/text()"))
            slug = (
                " ".join(location_name.split()[1:])
                .replace("Wendy's Barbican", "Kings House Road")
                .replace("Fairview", "Montego Bay")
            )
            info = " ".join(d.xpath(".//div/p//text()")).replace("\n", "").strip()
            ad = info.split("Phone")[0].strip()
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "Jamaica"
            city = a.city or "<MISSING>"
            latitude = (
                "".join(
                    d.xpath(
                        f'.//preceding::div[./div[contains(text(), "{slug}")]]/@data-lat'
                    )
                )
                or "<MISSING>"
            )
            longitude = (
                "".join(
                    d.xpath(
                        f'.//preceding::div[./div[contains(text(), "{slug}")]]/@data-lng'
                    )
                )
                or "<MISSING>"
            )
            phone = info.split("Phone:")[1].split("Hours")[0].strip()
            hours_of_operation = info.split("Hours:")[1].strip()
            hours_of_operation = " ".join(hours_of_operation.split())

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
            )

            sgw.write_row(row)

    except Exception as e:
        log.info(f"Err at #L100: {e}")


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
