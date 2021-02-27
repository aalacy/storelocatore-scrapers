from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from dms2dec.dms_convert import dms2dec

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}


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


def _sign(original, val):
    if "-" in original:
        return f"-{val}"


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://amerisleep.com/"
        base_url = "https://amerisleep.com/retail/"
        r = session.get(base_url, headers=_headers, verify=False)
        soup = bs(r.text, "html.parser")
        divlist = soup.select("div.container .o-grid__item p span a")
        for div in divlist:
            link = div["href"]
            r = session.get(link, headers=_headers, verify=False)
            soup1 = bs(r.text, "lxml")
            loc = json.loads(
                soup1.find("script", type="application/ld+json")
                .string.strip()
                .replace("\n", "")
            )

            latitude = loc["geo"]["latitude"]
            longitude = loc["geo"]["longitude"]
            if "'" in loc["geo"]["latitude"]:
                latitude = _sign(
                    loc["geo"]["latitude"], dms2dec(loc["geo"]["latitude"])
                )
                longitude = _sign(
                    loc["geo"]["longitude"], dms2dec(loc["geo"]["longitude"])
                )
            yield SgRecord(
                page_url=link,
                location_name=loc["name"],
                street_address=loc["address"]["streetAddress"],
                city=loc["address"]["addressLocality"],
                state=loc["address"]["addressRegion"],
                zip_postal=loc["address"]["postalCode"],
                country_code="US",
                location_type=loc["@type"],
                phone=loc["telephone"],
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(loc["openingHours"])),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
