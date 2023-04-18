from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "http://www.familyfoodsstores.com/"
        base_url = "http://www.familyfoodsstores.com/locations.html"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul li a")
        for link in locations:
            page_url = locator_domain + link["href"]
            if link["href"].startswith("http"):
                page_url = link["href"]
            street_address = city = state = zip_postal = phone = ""
            hours_of_operation = ""
            if page_url == "https://www.nugentscorner.com/":
                soup = bs(session.get(page_url, headers=_headers).text, "lxml")
                phone = soup.find("a", href=re.compile(r"tel:")).text
                addr = soup.select("ul.contact-info li")[-1].text.strip().split(",")
                street_address = addr[0]
                city = addr[1]
                state = addr[2].strip().split(" ")[0].strip()
                zip_postal = addr[2].strip().split(" ")[-1].strip()
                hour_block = soup.find(
                    "", string=re.compile(r"Open Daily:")
                ).parent.next_sibling
                hours_of_operation = f"Daily {hour_block}"
            else:
                soup = bs(session.get(page_url, headers=_headers).text, "lxml")
                block = list(soup.table.select("tr")[2].td.stripped_strings)
                street_address = block[1]
                city = block[2].split(",")[0].strip()
                state = block[2].split(",")[1].strip().split(" ")[0].strip()
                zip_postal = block[2].split(",")[1].strip().split(" ")[-1].strip()
                phone = block[5]
            yield SgRecord(
                page_url=page_url,
                location_name=link.text,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                phone=phone,
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
