from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

_headers = {
    "referer": "https://www.selfridges.com/US/en/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}
locator_domain = "https://www.selfridges.com"
base_url = "https://www.selfridges.com/US/en/features/info/stores/london/"


def fetch_data():
    with SgRequests(proxy_country="us") as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        page_links = soup.select("ul.navigation-root a")
        for link in page_links:
            if "newsletter" in link.text:
                break
            page_url = locator_domain + link["href"]
            soup = bs(session.get(page_url, headers=_headers).text, "lxml")
            coord = (
                soup.select_one('a[rel="noopener noreferer"]')["href"]
                .split("ll=")[1]
                .split(",")
            )
            addr = list(
                soup.find("", string=re.compile(r"Selfridges & Co"))
                .find_parent()
                .stripped_strings
            )
            street_address = ", ".join(addr[:-2]).replace("Selfridges & Co,", "")
            city = addr[-2]
            if "Birmingham" in city:
                street_address += " " + city
                city = "Birmingham"

            hr = soup.find("strong", string=re.compile(r"Our store opening hours"))
            hours = []
            for hh in hr.find_parent().find_next_siblings("p"):
                if not hh.text.strip():
                    break
                hours.append(": ".join(hh.stripped_strings).split("(")[0].strip())

            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip(),
                street_address=street_address,
                city=city,
                zip_postal=addr[-1],
                country_code="UK",
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("\xa0", " "),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=10
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
