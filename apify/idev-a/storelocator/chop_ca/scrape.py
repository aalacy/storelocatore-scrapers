from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://chop.ca"
base_url = "https://chop.ca/location-finder"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("li.location-block__location")
        for link in links:
            page_url = locator_domain + link.a["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            soup1 = bs(res, "lxml")
            phone = link.select_one("span.phone-text-hide").text.strip()
            hours = []
            days = soup1.select("div.hours-wrapper")[-1].select("span.day")
            times = soup1.select("div.hours-wrapper")[-1].select("span.hours")
            for x in range(len(days)):
                hours.append(f"{days[x].text.strip()} {times[x].text.strip()}")

            script = json.loads(
                res.split("jQuery.extend(Drupal.settings,")[1]
                .split("</script>")[0]
                .strip()[:-2]
            )
            raw_address = " ".join(list(soup1.select_one("div.adr").stripped_strings))
            yield SgRecord(
                page_url=page_url,
                location_name=soup1.select_one("span.loc-name").text.strip(),
                street_address=" ".join(
                    list(soup1.select_one("div.street-address").stripped_strings)
                ),
                city=soup1.select_one("span.locality").text.strip(),
                state=soup1.select_one("span.region").text.strip(),
                zip_postal=soup1.select_one("span.postal-code").text.strip(),
                country_code="CA",
                phone=phone,
                latitude=script["ss_menu_location"]["lat"],
                longitude=script["ss_menu_location"]["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
