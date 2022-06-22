import time
import ssl
import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sglogging import sglog
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address

from tenacity import retry, stop_after_attempt
import tenacity
import random

locator_domain = "https://www.extendedstayamerica.com/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
}
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)
ssl._create_default_https_context = ssl._create_unverified_context


@retry(stop=stop_after_attempt(3), wait=tenacity.wait_fixed(5))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        log.info(response)
        time.sleep(random.randint(7, 10))
        if response.status_code == 200:
            log.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response


def fetch_data(sgw: SgWriter):

    api_url = "https://api.prod.bws.esa.com/cms-proxy-api/sitemap/property"
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//url/loc[contains(text(), '/hotels/')]")
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        log.debug(f"fetching {page_url} ...")
        r = get_response(page_url)
        tree = html.fromstring(r.text)
        js_block = "".join(
            tree.xpath('//script[contains(text(), "openingHoursSpecification")]/text()')
        )
        try:
            js = json.loads(js_block)
            a = js.get("address")
            street_address = a.get("streetAddress") or "<MISSING>"
            city = a.get("addressLocality") or "<MISSING>"
            state = a.get("addressRegion") or "<MISSING>"
            postal = a.get("postalCode") or "<MISSING>"
            country_code = "US"
            location_name = js.get("name") or "<MISSING>"
            phone = js.get("telephone") or "<MISSING>"
            store_number = js.get("identifier") or "<MISSING>"
            latitude = js.get("geo").get("latitude") or "<MISSING>"
            longitude = js.get("geo").get("longitude") or "<MISSING>"
            hours_of_operation = "Open 24 hours a day, seven days a week"
        except:
            location_name = "".join(tree.xpath("//h1//text()"))
            ad = (
                "".join(
                    tree.xpath(
                        "//div[./h1]/following-sibling::div[1]/div/div[2]/text()"
                    )
                )
                .replace("\n", "")
                .strip()
            )
            a = parse_address(USA_Best_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "US"
            city = a.city or "<MISSING>"
            phone = (
                "".join(
                    tree.xpath(
                        "//div[./h1]/following-sibling::div[1]/div/div[1]//a//text()"
                    )
                )
                .replace("\n", "")
                .strip()
            )
            ll = "".join(tree.xpath("//div[@data-latlng]/@data-latlng"))
            latitude = ll.split(",")[0].strip()
            longitude = ll.split(",")[1].strip()
            hours_of_operation = "Open 24 hours a day, seven days a week"
            try:
                store_number = (
                    "".join(
                        tree.xpath(
                            '//script[contains(text(), "openingHoursSpecification")]/text()'
                        )
                    )
                    .split('"identifier": "')[1]
                    .split('"')[0]
                    .strip()
                )
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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
