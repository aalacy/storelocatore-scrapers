from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

locator_domain = "https://haciendafiesta.com"


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("-", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa", " ")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xae", " ")
    )


def fetch_data():
    with SgRequests() as session:
        base_url = "https://haciendafiesta.com/locations"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#locations-list div.location")
        for _ in locations:
            page_url = locator_domain + _.a["href"]
            block = list(_.p.stripped_strings)
            if block[-1].startswith("Join"):
                del block[-1]
            state_zip = block[1].split(",")[1].strip().split(" ")
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            try:
                hour_block = soup1.find(
                    "strong", string=re.compile(r"HOURS", re.IGNORECASE)
                )
                for hour in (
                    hour_block.find_parents("tr")[0]
                    .find_next_sibling("tr")
                    .td.select("p")[-1]
                    .stripped_strings
                ):
                    if "Easter Sunday" in hour:
                        continue
                    hours.append(hour)
            except:
                hour_block = soup1.find(
                    "h3", string=re.compile(r"HOURS", re.IGNORECASE)
                )
                hours = [
                    hour.text
                    for hour in hour_block.find_next_siblings("p")
                    if hour.text.strip()
                ]

            yield SgRecord(
                page_url=page_url,
                location_name=_.a.text,
                street_address=block[0],
                city=block[1].split(",")[0].strip(),
                state=state_zip[0],
                zip_postal=state_zip[1],
                country_code="US",
                phone=block[-1],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
