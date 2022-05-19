from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.chrome import ChromeDriverManager

logger = SgLogSetup().get_logger("citycoboston")
locator_domain = "https://citycoboston.com/"
base_url = "https://www.citycoboston.com/locations/"


def _flat(nestedlist):
    flatlist = []
    for sublist in nestedlist:
        if type(sublist) == list:
            for element in sublist:
                flatlist.append(element)
        elif sublist:
            flatlist.append(sublist)

    return flatlist


def fetch_data():
    with SgChrome(executable_path=ChromeDriverManager().install()) as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        locations = soup.select("div.bu_collapsible_container")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            block = list(_.select("p")[1].select_one("span.address").stripped_strings)
            driver.get(_.select_one("span.address").a["href"])
            addr = parse_address_intl(block[0])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            temp = [list(hh.stripped_strings) for hh in _.select("span.hours")][1:]
            if not temp:
                temp = list(_.select("p > span")[1].stripped_strings)
            else:
                temp = _flat(temp)
                if len(temp) == 1 and "Hours" in temp[0]:
                    temp = list(
                        _.select("span.hours")[-1].find_parent("p").stripped_strings
                    )[1:]

            temp = _flat(temp)
            hours = []
            for hh in temp:
                if "subway" in hh.lower() or "healthy" in hh.lower():
                    break
                hours.append(hh)
            coord = driver.current_url.split("/@")[1].split("/data")[0].split(",")
            yield SgRecord(
                page_url=base_url,
                location_name=_.h3.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=block[-1].split("|")[-1],
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours)
                .replace("\xa0", "")
                .replace("–", "-"),
                raw_address=block[0],
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
