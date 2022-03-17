from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import dirtyjson
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mainstreamboutique")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    locator_domain = "https://mainstreamboutique.com"
    base_url = "https://mainstreamboutique.com/apps/store-locator"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        coords = (
            res.split("= 'You Are Here';")[1]
            .strip()
            .split("function initialize()")[0]
            .split("markersCoords.push(")
        )
        locs = []
        for temp in coords:
            if not temp:
                continue
            _ = dirtyjson.loads(temp[:-2])
            locs.append(_)

        soup = bs(res, "lxml")
        locations = soup.select("div#addresses_list ul li")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            store_number = _["onmouseover"].split("(")[1][:-1]
            city = _.select_one("span.city").text.strip()
            page_url = (
                "https://mainstreamboutique.com/pages/"
                + _.select_one("div.store_website a")["href"].split("/")[-1]
            )
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            hours = []
            phone = ""
            if res.status_code == 200:
                sp1 = bs(res.text, "lxml")
                _addr = []
                for aa in sp1.select("div.shg-row div.shg-theme-text-content p"):
                    if "get direction" in aa.text.lower():
                        break
                    if "Free Ship" in aa.text:
                        break
                    if not aa.text.strip():
                        continue
                    _addr.append(aa.text.strip())
                if _addr and _addr[0].startswith("Monday"):
                    _addr = []
                    for aa in sp1.select("div.shg-row div.shg-theme-text-content div"):
                        if "get direction" in aa.text.lower():
                            break
                        if "Free Ship" in aa.text:
                            break
                        if not aa.text.strip():
                            continue
                        _addr.append(aa.text.strip())

                if "We are closed" in sp1.select("div.shg-row > div")[1].text:
                    hours = ["Closed"]
                elif "COMING SOON" in sp1.select("div.shg-row > div")[1].text:
                    continue
                else:
                    txt = sp1.select("div.shg-row > div")[1].text
                    if "temporarily closed" in txt.lower():
                        hours = ["Temporarily Closed"]
                    else:
                        hh = list(sp1.select("div.shg-row > div")[1].stripped_strings)[
                            1:
                        ]
                        for x in range(0, len(hh), 2):
                            hours.append(f"{hh[x]} {hh[x+1]}")
                phone = ""
                for pp in sp1.select("div.shg-row > div")[2].select("p"):
                    if not pp.text.strip():
                        continue
                    phone = pp.text.strip().split(":")[-1].strip()
                    break
                zip_postal = ""
                if _.select_one("span.postal_zip"):
                    zip_postal = _.select_one("span.postal_zip").text.strip()
                if not zip_postal:
                    zip_postal = _addr[-1].split()[-1].strip()
                    if not zip_postal.isdigit():
                        zip_postal = ""
                coord = ["", ""]
                for loc in locs:
                    if str(loc["id"]) == store_number:
                        coord = loc
                        break
            yield SgRecord(
                page_url=page_url,
                location_name=_.select_one("span.name").text.strip(),
                street_address=_.select_one("span.address").text.strip(),
                city=city,
                state=_.select_one("span.prov_state").text.strip(),
                latitude=coord["lat"],
                longitude=coord["lng"],
                zip_postal=zip_postal,
                country_code=_.select_one("span.country").text,
                locator_domain=locator_domain,
                phone=_p(phone),
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(_addr),
            )


if __name__ == "__main__":
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
