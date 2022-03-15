from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
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


def _street(val):
    return (
        val.replace("Fulton & Williams", "")
        .replace("26Th Street Btw 6Th & Broadway", "")
        .replace("50Th Street Btw 6Th & 7Th Ave", "")
        .replace("8Th Ave Btw 52Nd & 53Rd", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.meltshop.com/"
        base_url = "https://www.meltshop.com/locations"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.summary-item")
        for _ in locations:
            page_url = _.select_one("div.summary-title a")["href"]
            if not page_url.startswith("http"):
                page_url = "https://meltshop.olo.com" + page_url
            hours_of_operation = "; ".join(
                [hour for hour in _.select("div.summary-excerpt p")[0].stripped_strings]
            )
            if len(_.select("div.summary-excerpt p")) > 3:
                hours_of_operation += "; " + _.select("div.summary-excerpt p")[1].text
            block = [a for a in _.select("div.summary-excerpt p")[-2].stripped_strings]
            street_address = block[0]
            if len(block) > 3:
                street_address = " ".join(block[:2])
            street_address = street_address.replace(",", "")
            state_zip = block[-2]
            phone = block[-1]
            if len(block) == 2:
                state_zip = block[-1]
                phone = ""
            _address = street_address + " " + state_zip
            addr = parse_address_intl(_address)
            yield SgRecord(
                page_url="https://www.meltshop.com/locations",
                location_name=_.select_one("div.summary-title a").text,
                street_address=_street(addr.street_address_1),
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=_valid(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
