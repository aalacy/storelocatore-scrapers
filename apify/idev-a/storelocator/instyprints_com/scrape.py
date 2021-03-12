from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import re

locator_domain = "https://www.instyprints.com/"
base_url = "https://www.instyprints.com/instyprints/frontend/locationsMap.js"


def _valid1(val):
    if val:
        return (
            val.strip()
            .replace("–", "-")
            .encode("unicode-escape")
            .decode("utf8")
            .replace("\\xc3\\xa9", "e")
            .replace("\\xa0", "")
            .replace("\\xa0\\xa", "")
            .replace("\\xae", "")
        )
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url)
        locations = json.loads(
            res.text.split("var franchiseeLocations =")[1]
            .split("var youAreHereLat")[0]
            .strip()[:-1]
        )
        for _ in locations:
            page_url = _["MicroSiteUrl"]
            page = session.get(page_url)
            base = bs(page.text, "lxml")
            hours = []
            for _hour in base.select("div.oprationalHours div.row.rows")[2:]:
                hours.append(": ".join([tt for tt in _hour.stripped_strings]))
            if not hours:
                if base.select_one("h1.font_0"):
                    temp = [tt for tt in base.select_one("h1.font_0").stripped_strings]
                    for i in range(0, len(temp), 2):
                        hours.append(f"{temp[i]}: {temp[i+1]}")

            if not hours:
                hour_block = base.find("p", string=re.compile("Hours Of Operation:"))
                if hour_block:
                    hours.append(hour_block.next_sibling.next_sibling.text)

            phone_number = (
                base.select_one("h3.phoneNumber")
                and base.select_one("h3.phoneNumber").text
                or _["PhoneWithCountryCode"]
            )
            yield SgRecord(
                store_number=_["LocationNumber"],
                page_url=page_url,
                location_name=_["LocationName"],
                street_address=f'{_["Line1"]} {_["Line2"]}',
                city=_["City"],
                state=_["State"],
                zip_postal=_["Postal"],
                country_code="US",
                phone=phone_number,
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                locator_domain=locator_domain,
                hours_of_operation=_valid1("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
