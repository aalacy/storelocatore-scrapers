from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import json
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.volvocars.com",
    "referer": "https://www.volvocars.com/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
}

locator_domain = ""
urls = {
    "Serbia": "https://www.volvocentar.rs/iframe_ajax?load_scripts=dealers",
    "Bosnia and Herzegovina": "https://www.volvocentar.ba/iframe_ajax?load_scripts=dealers",
    "Azerbaijan": "https://www.volvocars.com/az/s%C9%99rgi-salonunu-tap",
    "Lebanon": "https://www.volvocars.com/lb/v/legal/contact-us",
}


def _d(country, base_url, location_name, raw_address, phone, hours="", lat="", lng=""):
    raw_address = raw_address.replace("\xa0", "")
    if country not in raw_address:
        raw_address + ", " + country
    addr = parse_address_intl(raw_address)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    return SgRecord(
        page_url=base_url,
        location_name=location_name.replace(":", " "),
        street_address=street_address,
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code=country,
        phone=phone.split(":")[-1].replace("\xa0", ""),
        latitude=lat.strip(),
        longitude=lng.strip(),
        locator_domain=locator_domain,
        hours_of_operation=hours,
        raw_address=raw_address,
    )


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            logger.info(base_url)
            if country in ["Serbia", "Bosnia and Herzegovina"]:
                soup = bs(
                    session.get(base_url, headers=_headers).json()["content"], "lxml"
                )
                locations = soup.select("div.dealer_item")
                for _ in locations:
                    raw_address = _.p.text.strip()
                    street_address = city = state = zip_postal = ""
                    addr = raw_address.split(",")
                    street_address = addr[0]
                    city = addr[-1].strip().split()[-1].split("-")[0]
                    zip_postal = addr[-1].strip().split()[0]

                    block = list(_.stripped_strings)
                    phone = ""
                    for x, bb in enumerate(block):
                        if bb == "T:":
                            phone = block[x + 1]
                            break
                    lat, lng = (
                        _.select_one("a.location_link")["href"]
                        .split("q=")[-1]
                        .split(",")
                    )
                    hours = []
                    days = [
                        dd.text.strip()
                        for dd in _.select("div.termin_hours")[0].select(
                            "span.week-day"
                        )
                    ]
                    times = [
                        dd.text.strip()
                        for dd in _.select("div.termin_hours")[0].select(
                            "span.work-hour"
                        )
                    ]
                    for hh in range(len(days)):
                        hours.append(f"{days[hh]} {times[hh]}")
                    yield SgRecord(
                        page_url=base_url,
                        location_name=_.h2.text.strip(),
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_postal,
                        country_code=country,
                        phone=phone,
                        latitude=lat,
                        longitude=lng,
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                        raw_address=raw_address,
                    )

            elif country == "Azerbaijan":
                soup = bs(session.get(base_url, headers=_headers).text, "lxml")
                locations = soup.select("div.oxp-exteriorFeatureTwo div.extf-content")
                for _ in locations:
                    if not _.text.strip():
                        continue
                    location_name = raw_address = phone = ""
                    bb = [
                        b
                        for b in _.select("p", recursive=False)
                        if "Salonu ziyarət etmək" not in b.text
                    ]
                    for x, pp in enumerate(bb):
                        _pp = list(pp.stripped_strings)
                        p_text = " ".join(_pp)
                        if not p_text:
                            continue
                        if (
                            "SHOWROOM" in p_text
                            or "Authorized" in p_text
                            or "Genuine" in p_text
                            or "Email" in p_text
                            or "ელ.ფოსტა" in p_text
                        ):
                            continue
                        if "Salonun ad" in p_text:
                            location_name = p_text.split(":")[-1].strip()
                            continue
                        if "Hotline" in p_text or "Tel" in p_text:
                            if not phone:
                                if len(_pp) == 1:
                                    phone = _pp[0].split(":")[-1].split("If")[0].strip()
                                else:
                                    phone = _pp[1].split(":")[-1].split("If")[0].strip()
                        if "Ünvan" in p_text:
                            raw_address = p_text.split(":")[-1].strip()

                    addr = raw_address.split(",")
                    zip_postal = addr[-1].strip()
                    state = city = ""
                    street_address = ", ".join(addr[:-1])
                    yield SgRecord(
                        page_url=base_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_postal,
                        country_code=country,
                        phone=phone,
                        locator_domain=locator_domain,
                        raw_address=raw_address.strip(),
                    )

            elif country == "Lebanon":
                soup = bs(session.get(base_url, headers=_headers).text, "lxml")
                block = bs(
                    json.loads(
                        soup.find("script", string=re.compile(r'{"sitecore"'))
                        .text.replace("\\u002F", "/")
                        .replace("\\u003C\\u003Ch2\\u003E\\n", "</h2>")
                        .replace("\\u003Ch2\\u003E", "<h2>")
                        .replace("\\u003C\\u002Fp\\u003E\\n", "</p>")
                        .replace("\\u003Cp\\u003E", "<p>")
                        .replace("\\u003C\\u003Cstrong\\u003E\\n", "</strong>")
                        .replace("\\u003Cstrong\\u003E", "<strong>")
                    )["sitecore"]["route"]["placeholders"]["article-section"][0][
                        "fields"
                    ][
                        "body"
                    ][
                        "value"
                    ],
                    "lxml",
                )
                bb = list(block.select("p")[2].stripped_strings)
                aa = list(block.select("p")[3].stripped_strings)
                raw_address = bb[1] + ", " + aa[0]
                phone = ""
                for a in aa:
                    if "Tel" in a:
                        phone = a.split(":")[-1]
                        break
                yield _d(country, base_url, bb[0], raw_address, phone)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
