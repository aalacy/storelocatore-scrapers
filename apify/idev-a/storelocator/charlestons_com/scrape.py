from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_usa
from bs4 import BeautifulSoup as bs
import re

locator_domain = "https://charlestons.com/"
base_url = "https://charlestons.com/locations/"


def _headers():
    return {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "referer": "https://charlestons.com/",
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }


def fetch_data():
    data = []

    with SgRequests() as session:
        res = session.get(base_url, headers=_headers())
        soup = bs(res.text, "lxml")
        links = soup.select("div.state div.card")
        store_number = "<MISSING>"
        for link in links:
            for _ in link["class"]:
                _num = re.findall(r"^location-\d{3}", _)
                if _num:
                    store_number = _num[0].split("-")[1]
                    break
            page_url = link.select_one("a.is-link")["href"]
            r1 = session.get(page_url, headers=_headers())
            soup1 = bs(r1.text, "lxml")
            location_name = soup1.select_one("h1.title").text.strip()
            addr = parse_address_usa(
                soup1.select_one("address.address")
                .text.strip()
                .replace(",           Omaha, NE           68154", "")
            )
            phone = soup1.select_one("p.phone").text.strip()
            hours_of_operation = "; ".join([_.text for _ in soup1.select("p.hours")])
            record = SgRecord(
                page_url=page_url,
                store_number=store_number,
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )
            data.append(record)

    return data


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
