from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bluebottlecoffee")


_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa", "")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://bluebottlecoffee.com/"
        base_url = "https://bluebottlecoffee.com/api/cafe_search/fetch.json?cafe_type=all&coordinates=false&query=true&search_value=all"
        r = session.get(base_url, headers=_headers).json()
        for q, locations in r["cafes"].items():
            for dt in locations:
                address = bs(dt["address"], "lxml")
                full = list(address.stripped_strings)
                if full[-1] == "Ttukseom station — exit #1":
                    del full[-1]
                if len(full[-1].split(",")) == 1:
                    del full[-1]

                addr = parse_address_intl(", ".join(full).replace("00000", ""))
                street_address = " ".join(full[:-1])
                street_address = street_address.replace(
                    "Entrance is on 52nd St", ""
                ).replace("NW corner of Tower 4", "")
                if street_address.replace("-", "").strip().isdigit():
                    street_address = " ".join(full).split(",")[0]
                page_url = dt["url"]
                logger.info(page_url)
                soup = bs(session.get(page_url).text, "lxml")
                hours = []
                hours_of_operation = ""
                for _ in soup.select("div.mw5.mw-100-ns div.dt.wi-100.pb10.f5"):
                    time = "".join(
                        [_t for _t in _.select_one("div.dtc.tr").stripped_strings]
                    )
                    hours.append(f"{_.select_one('div.dtc').text}: {time}")

                if not hours:
                    if soup.find("div", {"class": "mw5 mw-100-ns"}):
                        hours_of_operation = soup.find(
                            "div", {"class": "mw5 mw-100-ns"}
                        ).text
                else:
                    hours_of_operation = re.sub(r"\s+", " ", "; ".join(hours)).strip()

                if "reopened" in hours_of_operation:
                    hours_of_operation = ""
                if dt["temporarily_closed"]:
                    hours_of_operation = "temporarily closed"
                zip_postal = addr.postcode
                if zip_postal == "00000":
                    zip_postal = ""
                yield SgRecord(
                    page_url=page_url,
                    store_number=dt["id"],
                    location_name=dt["name"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=zip_postal,
                    country_code=addr.country,
                    latitude=dt["latitude"],
                    longitude=dt["longitude"],
                    locator_domain=locator_domain,
                    hours_of_operation=_valid(hours_of_operation),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
