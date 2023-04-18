from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

locator_domain = "https://telekom.me"
base_url = "https://telekom.me/privatni-korisnici/korisnicka-zona/clanak/kako-do-nas"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        script = "return window.__NUXT__"
        locations = bs(
            driver.execute_script(script)["state"]["widgets"]["widgets"][0][
                "tabsAccordionItem"
            ][1]["content"]["value"],
            "lxml",
        ).select("table tr")[1:]
        for _ in locations:
            td = _.select("td")
            location_name = td[0].text.strip()
            city = "".join([c for c in location_name if not c.isdigit()]).strip()
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=td[1].text.strip(),
                city=city,
                country_code="ME",
                locator_domain=locator_domain,
                hours_of_operation=td[-1].text.strip(),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
