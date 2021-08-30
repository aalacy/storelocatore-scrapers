from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
import dirtyjson as json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mcdonalds.mu"
base_url = "https://mcdonalds.mu/our-location"


def _v(val):
    return val.replace("#", "'").strip()


def fetch_data():
    with SgRequests() as session:
        data = (
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("div#map script")
            .string.strip()
        )
        locations = re.split(r"var\s\w+\s=", data)[1:]
        for loc in locations:
            if "long:" not in loc:
                continue
            _ = json.loads(
                loc.replace("&#39;", "#")
                .replace("&nbsp;", " ")
                .replace("\n", "")
                .replace("\\", "")
                .replace("\t", "")
                .split(";")[0]
                .strip()
            )
            info = bs(_["info"], "lxml")
            phone = ""
            for bb in list(info.stripped_strings):
                if "Tel" in bb:
                    phone = bb.split(":")[-1].strip()
                    break
            hours = []
            for hh in info.select("table tr"):
                hr = ": ".join(hh.stripped_strings).split("|")[0]
                if "Please be" in hr:
                    continue
                hours.append(hr)
            yield SgRecord(
                page_url=base_url,
                location_name=_v(info.strong.text.strip()),
                latitude=_["lat"],
                longitude=_["long"],
                country_code="Mauritius",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
