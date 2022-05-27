from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.volvocars.com/ma"
urls = {
    "Morocco": "https://www.volvocars.com/ma/find-a-showroom",
    "Oman": "https://www.volvocars.com/en-om/buy/research/find-a-showroom",
    "Qatar": "https://www.volvocars.com/en-qa/buy/research/find-a-showroom",
    "Mauritius": "https://www.volvocars.com/mu/find-showroom",
}


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            soup = bs(session.get(base_url, headers=_headers).text, "lxml")
            if country == "Morocco":
                locations = [
                    pp for pp in soup.select("div.extf-content p") if pp.text.strip()
                ]
                location_name = phone = ""
                addr = []
                for x in range(len(locations)):
                    _ = locations[x]
                    if x % 2 == 0:
                        location_name = _.text.split(":")[0].strip()
                    else:
                        temp = list(_.stripped_strings)
                        for y, pp in enumerate(temp):
                            if "Tel" in pp:
                                phone = temp[y + 1]
                                break
                            elif "Fax" in pp:
                                break
                            else:
                                addr.append(pp)
                    if location_name and addr:
                        if len(addr) == 2 or not addr[-1].replace(" ", "").isdigit():
                            street_address = " ".join(addr[:-1])
                            city = addr[-1].split()[0].strip()
                            zip_postal = " ".join(addr[-1].split()[1:])
                        else:
                            street_address = " ".join(addr[:-2])
                            city = addr[-2]
                            zip_postal = addr[-1]
                        yield SgRecord(
                            page_url=base_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            zip_postal=zip_postal,
                            country_code=country,
                            phone=phone,
                            locator_domain=locator_domain,
                            raw_address=", ".join(addr),
                        )
                        location_name = phone = ""
                        addr = []

            elif country == "Oman":
                pp = soup.select("div.extf-content p")
                phone = ""
                if "Tel" in pp[2].text:
                    phone = pp[2].text.split(":")[-1].strip()
                raw_address = pp[1].text.strip()
                yield SgRecord(
                    page_url=base_url,
                    location_name=pp[0].text.strip(),
                    city=raw_address.strip(),
                    country_code=country,
                    phone=phone,
                    locator_domain=locator_domain,
                    raw_address=raw_address,
                )
            elif country == "Qatar":
                pp = soup.select("div.extf-content p")
                phone = ""
                if "Tel" in pp[3].text:
                    phone = pp[3].text.split(":")[-1].strip()
                raw_address = pp[0].text.strip() + " " + pp[2].text.strip()
                addr = raw_address.split(",")
                yield SgRecord(
                    page_url=base_url,
                    location_name=soup.select_one("h2.h2").text.strip(),
                    street_address=addr[0],
                    city=addr[1],
                    country_code=country,
                    phone=phone,
                    locator_domain=locator_domain,
                    raw_address=raw_address,
                )
            elif country == "Mauritius":
                pp = soup.select("div.extf-content p")
                phone = ""
                if "Tel" in pp[4].text:
                    phone = pp[4].text.split(":")[-1].strip()
                addr = list(pp[3].stripped_strings)
                yield SgRecord(
                    page_url=base_url,
                    location_name=pp[1].text.strip(),
                    street_address=addr[0].replace(",", "").strip(),
                    city=addr[1],
                    country_code=country,
                    phone=phone,
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
