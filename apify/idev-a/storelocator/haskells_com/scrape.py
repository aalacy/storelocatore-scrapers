from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("haskells")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.haskells.com/"
    base_url = "https://www.haskells.com/about/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        script = soup.find("script", string=re.compile(r"var marker;")).string
        temp = re.split(r"jQuery\(\"\.(.*)\"\).", script)[1:]
        coords = []
        for x in range(0, len(temp), 2):
            coords.append(
                temp[x + 1].split("changeMarkerPos(")[1].split(")")[0].split(",")
            )
        links = soup.select("div.individual-location")
        logger.info(f"{len(links)} found")
        for x, link in enumerate(links):
            hours = [
                ":".join(hh.stripped_strings) for hh in link.select("div.hours p")
            ][1:]
            location_name = link.h2.text.strip().replace("&amp;", "&")
            city = state = zip_postal = ""
            if link.select_one('span[itemprop="addressLocality"]'):
                city_state = link.select_one(
                    'span[itemprop="addressLocality"]'
                ).text.split(",")
                city = city_state[0].strip()
                state = city_state[1].strip()
            if link.select_one('span[itemprop="postalCode"]'):
                zip_postal = link.select_one('span[itemprop="postalCode"]').text
            coord = coords[x]
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=link.select_one('span[itemprop="streetAddress"]').text,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                phone=link.h3.text.strip(),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
