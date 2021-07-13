from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("suncoastcreditunion")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.suncoastcreditunion.com"
    start_url = "https://www.suncoastcreditunion.com/about-us/branch-and-atm-locator#"
    base_url = (
        "https://www.suncoastcreditunion.com/~/locator?address=57301&distance=5000"
    )
    streets = []
    with SgRequests() as session:
        hours = (
            bs(session.get(start_url, headers=_headers).text, "lxml")
            .select_one("div.general_block p")
            .stripped_strings
        )
        locations = session.get(base_url, headers=_headers).json()["MapData"][
            "Locations"
        ]
        dupe = 0
        logger.info(f"{len(locations)} found")
        for _ in locations:
            phone = _["Phone"].strip()
            if phone == "N/A":
                phone = ""
            _zz = _["Address2"].split(",")[1].strip().split(" ")
            zip_postal = ""
            if len(_zz) > 1:
                zip_postal = " ".join(_zz[1:]).strip()
            if zip_postal == "0000":
                zip_postal = ""
            if zip_postal.endswith("-"):
                zip_postal = zip_postal[:-1]
            _ss = (
                _["Address"]
                + _["Type"]
                + str(_["Coordinates"]["Latitude"])
                + str(_["Coordinates"]["Longitude"])
            )
            if _ss in streets:
                dupe += 1
                continue
            streets.append(_ss)
            page_url = ""
            if _["LocationDetailLink"]:
                page_url = locator_domain + _["LocationDetailLink"]
            yield SgRecord(
                page_url=page_url,
                location_name=_["Title"],
                street_address=_["Address"],
                city=_["Address2"].split(",")[0].strip(),
                state=_["Address2"].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=zip_postal,
                latitude=_["Coordinates"]["Latitude"],
                longitude=_["Coordinates"]["Longitude"],
                country_code="US",
                phone=phone,
                location_type=_["Type"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )

        logger.info(f"Duplicate {dupe}")


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
