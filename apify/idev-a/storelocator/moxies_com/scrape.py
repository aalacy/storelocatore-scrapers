from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
from sgscrape.sgpostal import parse_address_intl

ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
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
    locator_domain = "https://moxies.com"
    base_url = "https://moxies.com/location-finder?usredirect=no"
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        links = soup.select(
            "ul.call-location-block__locations li.call-location-block__location > a"
        )
        for link in links:
            page_url = urljoin(locator_domain, link["href"])
            soup1 = bs(session.get(page_url).text, "lxml")
            location_name = soup1.select_one("h1.title span").text.strip()
            contact_info = soup1.select_one("div.contact-info p a")
            addr = parse_address_intl(" ".join(list(contact_info.stripped_strings)))
            phone = soup1.select("div.contact-info p")[1].a.text
            direction = contact_info["href"].split("/")[-1].strip().split(",")
            hours_of_operation = soup1.select_one("h2.subtitle").text
            if (
                "closed" in hours_of_operation.lower()
                or "temporarily closed"
                in soup1.select_one("div.field-name-field-location-description").text
            ):
                hours_of_operation = "Temporarily closed"
            else:
                tags = soup1.select("table.hours tr")
                hours = []
                for tag in tags:
                    hours.append(
                        f"{tag.select_one('td.day').text.strip()} {tag.select_one('td.opening').text.strip()}-{tag.select_one('td.closing').text}"
                    )
                hours_of_operation = "; ".join(hours)

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                latitude=direction[0],
                longitude=direction[1],
                zip_postal=addr.postcode,
                country_code="CA" if addr.state in ca_provinces_codes else "US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=_valid(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
