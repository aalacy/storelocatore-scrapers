from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
import lxml.html

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("cinemark_com")

session = SgRequests()


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_url = "https://cinemark.com/"

    r = session.get("https://cinemark.com/full-theatre-list")

    stores_sel = lxml.html.fromstring(r.text)
    links = stores_sel.xpath('//div[@class="columnList wide"]//a/@href')
    for link in links:
        page_url = "https://cinemark.com" + link
        if "now-closed" in page_url:
            continue
        logger.info(page_url)
        r1 = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(r1.text)
        info = "".join(
            store_sel.xpath('//script[@type="application/ld+json"]/text()')
        ).strip()

        try:
            if (
                "permanently closed"
                in store_sel.xpath('//div[@class="theatre-status-label"]/text()')[
                    0
                ].lower()
            ):
                continue
        except:
            pass

        try:
            if (
                "coming soon"
                in str(store_sel.xpath('//div[@class="clearfix"]//text()')[:5]).lower()
            ):
                continue
        except:
            pass

        data = json.loads(info)
        for address in data["address"]:
            street_address = (
                address["streetAddress"].split("(")[0].split(", The Common")[0].strip()
            )
            city = address["addressLocality"]
            state = address["addressRegion"]
            zipp = address["postalCode"]
            country_code = address["addressCountry"]
        phone = data["telephone"]
        location_name = data["name"].strip()
        if "NOW CLOSED".lower() in location_name.lower():
            continue
        location_type = ""
        latitude = (
            "".join(store_sel.xpath('//div[@class="theatreMap"]/a/img/@data-src'))
            .split("pp=")[1]
            .split(",")[0]
        )
        longitude = (
            "".join(store_sel.xpath('//div[@class="theatreMap"]/a/img/@data-src'))
            .split("pp=")[1]
            .split(",")[1]
            .split("&")[0]
        )

        sgw.write_row(
            SgRecord(
                locator_domain=base_url,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="",
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
