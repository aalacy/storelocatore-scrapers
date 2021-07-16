from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("codeninjas")

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
}


def fetch_data():
    addresses = []
    with SgRequests() as session:
        locator_domain = "https://www.codeninjas.com/"
        base_url = "https://services.codeninjas.com/api/locations/queryarea?latitude=37.09024&longitude=-95.712891&includeUnOpened=false&miles=5117.825778587137"
        json_data = session.get(
            base_url,
            headers=_headers,
        ).json()
        for data in json_data:
            if data["status"] != "OPEN":
                continue
            street_address = data["address1"] or ""

            if data["address2"]:
                street_address += " " + data["address2"]

            page_url = "https://www.codeninjas.com/" + data["cnSlug"]
            logger.info(page_url)

            soup1 = bs(
                session.get(
                    page_url,
                    headers=_headers,
                ).text,
                "lxml",
            )

            hours = []
            if soup1.select_one("div#centerHours ul li"):
                for hh in soup1.select_one("div#centerHours ul li").stripped_strings:
                    if "Birthday" in hh:
                        break
                    hours.append(hh)
                if hours and (
                    hours[0].lower() == "by appointment only"
                    or hours[0].lower() == "by appointment"
                    or "Program hours may vary" in hours[0]
                ):
                    hours = []
            if street_address in addresses:
                continue
            addresses.append(street_address)

            yield SgRecord(
                page_url=page_url,
                location_name=data["name"],
                street_address=street_address,
                city=data["city"],
                state=data["state"]["code"],
                zip_postal=data["postalCode"],
                country_code=data["countryCode"],
                longitude=data["longitude"],
                latitude=data["latitude"],
                phone=data["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .split("or")[0]
                .split("To")[0]
                .split("#")[0]
                .split("*")[0]
                .replace("|", ";")
                .strip(),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
