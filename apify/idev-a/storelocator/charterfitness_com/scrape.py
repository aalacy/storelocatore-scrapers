from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_usa
import re

locator_domain = "https://www.charterfitness.com/"
base_url = "https://www.charterfitness.com/charter-locations/"


def _valid1(val):
    if val:
        return (
            val.strip()
            .replace("–", "-")
            .encode("unicode-escape")
            .decode("utf8")
            .replace("\\xa0", "")
            .replace("\\xa0\\xa", "")
            .replace("\\xae", "")
        )
    else:
        return ""


def fetch_data():
    data = []

    with SgRequests() as session:
        res = session.get(base_url)
        soup = bs(res.text, "lxml")
        links = soup.select("div.elementor-widget-container table  a")
        for link in links:
            page_url = link["href"]
            r1 = session.get(page_url)
            soup1 = bs(r1.text, "lxml")
            block = soup1.find(string=re.compile("located at")).split("located at")[1]
            addr = parse_address_usa(block.strip())
            phone = soup1.find(string=re.compile("Phone Number:")).split(":")[1].strip()
            hours_of_operation = "; ".join(
                [_.text for _ in soup1.select("div.elementor-text-editor p")[1:]]
            )
            record = SgRecord(
                page_url=page_url,
                location_name=link.text,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=_valid1(hours_of_operation),
            )
            data.append(record)

    return data


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
