from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

locator_domain = "http://www.kaboom.com/"
base_url = "https://www.kaboom.com/locations"

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


def _url(locs, ID):
    for loc in locs:
        if loc["id"] == ID:
            return locator_domain + loc["route"]


def fetch_data():
    with SgRequests() as session:
        data = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("window.__BOOTSTRAP_STATE__ =")[1]
            .split("</script>")[0]
            .strip()[:-1]
        )
        locs = data["siteData"]["pagesMeta"]
        locations = data["siteData"]["page"]["properties"]["contentAreas"][
            "userContent"
        ]["content"]["cells"]
        for loc in locations[1:]:
            _ = loc["content"]["properties"]["repeatables"][0]
            addr = []
            phone = []
            if type(_["text"]["content"]) == str:
                continue

            no_loc = False
            blocks = _["text"]["content"]["quill"]["ops"]
            for x, ops in enumerate(blocks):
                tt = ops["insert"].strip()
                if not tt:
                    continue
                if "Click" in tt:
                    no_loc = True
                    break
                if x < len(blocks) - 2 and "(" not in tt:
                    addr.append(tt)
                else:
                    phone.append(tt)

            if no_loc:
                continue

            location_type = ""
            try:
                if (
                    "temporarily closed"
                    in _["callout"]["content"]["quill"]["ops"][0]["insert"]
                ):
                    location_type = "temporarily closed"
            except:
                pass

            location_name = _["title"]["content"]["quill"]["ops"][0]["insert"].strip()
            yield SgRecord(
                page_url=_url(locs, _["image"]["link"]["link"]["page"]["pageID"]),
                location_name=location_name,
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=" ".join(addr[-1].split(",")[1].strip().split()[1:]),
                country_code="CA",
                location_type=location_type,
                phone=_p("".join(phone)),
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
