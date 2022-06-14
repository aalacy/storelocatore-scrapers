from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

locator_domain = "https://www.thenorthface.cl"
base_url = "https://www.thenorthface.cl/tiendas"
json_url = r"https://www.thenorthface.cl/graphql\?query\=query\+GetCmsPage"

headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "",
    "content-type": "application/json",
    "referer": "https://www.thenorthface.cl/tiendas",
    "store": "the_north_face_store_view",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "x-magento-cache-id": "null",
}


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        driver.wait_for_request(json_url)
        soup = bs(driver.page_source, "lxml")
        locations = soup.select("main div.main-page-ioz div.pagebuilder-column")
        for _ in locations:
            p = _.select("p")
            coord = p[3].a["href"].split("/@")[1].split("/data")[0].split(",")
            location_name = p[0].text.strip()
            city = location_name.split("-")[0].split("–")[0].strip()
            if (
                "Costanera Center" in city
                or "Parque Arauco" in city
                or "Mall Sport" in city
                or "Alto Las Condes" in city
            ):
                city = ""
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=p[1].text.strip(),
                city=city,
                country_code="CL",
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation=p[2].text.strip(),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
