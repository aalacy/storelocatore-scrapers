from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from sglogging import sglog

locator_domain = "http://curvesindonesia.com/"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetch_data(sgw: SgWriter):

    api_url = "http://curvesindonesia.com/lokasi/?lang=en"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-md-4 col-sm-6 col-xs-12"]')
    for d in div:

        page_url = "".join(d.xpath("./a[1]/@href"))
        location_name = (
            "".join(d.xpath('.//div[@class="title my-elipsis"]/text()[1]'))
            .replace("\n", "")
            .strip()
        )
        state = (
            "".join(d.xpath('.//div[@class="title my-elipsis"]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        try:
            r = SgRequests.raise_on_err(session.get(page_url, headers=headers))
            log.info(f"## Response: {r}")
            tree = html.fromstring(r.text)
            ad = (
                "".join(tree.xpath('//div[@class="alamat-lokasi"]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            postal = a.postcode or "<MISSING>"
            country_code = "IN"
            city = a.city or "<MISSING>"
            latitude = "".join(tree.xpath("//div/@data-lat"))
            longitude = "".join(tree.xpath("//div/@data-lng"))
            phone = (
                "".join(tree.xpath('//div[@class="kontak-lokasi"]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if phone.find("(") != -1:
                phone = phone.split("(")[0].replace("-", "").strip()
            hours_of_operation = (
                " ".join(tree.xpath('//div[@class="email-lokasi"]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if hours_of_operation.find("Jadwal:") != -1:
                hours_of_operation = hours_of_operation.split("Jadwal:")[1].strip()

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
