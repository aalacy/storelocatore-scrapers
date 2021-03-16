from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

locator_domain = "https://www.a1mri.com"


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("-", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa", "")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        base_url = "https://www.a1mri.com/locations"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div.dmDefaultListContentRow  div.dmRespColsWrapper .dmRespCol"
        )
        for _ in locations:
            if not _.text:
                continue

            page_url = locator_domain + _.a["href"]
            block = list(_.stripped_strings)
            if len(block) == 5:
                del block[0]
            state_zip = block[1].split(",")[1].strip().split(" ")
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            coord = soup1.select_one('div[data-type="inlineMap"]')
            hour_label = soup1.find(
                "font", string=re.compile(r"Business Hours", re.IGNORECASE)
            )
            hours_of_operation = (
                hour_label.find_parent("h3").find_next_sibling("div").text
            )
            yield SgRecord(
                page_url=page_url,
                location_name=_.a.text,
                street_address=block[0],
                city=block[1].split(",")[0],
                state=state_zip[0],
                zip_postal=state_zip[-1],
                country_code="US",
                phone=block[2].replace("ph:", "").strip(),
                latitude=coord["lat"],
                longitude=coord["lon"],
                locator_domain=locator_domain,
                hours_of_operation=_valid(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
