from sgrequests import SgRequests
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    base_url = "https://www.omnisourceusa.com/locations"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    lat = []
    log = []
    ids = []
    k = soup.find_all("div", {"class": "contact-card-small"})
    name1 = soup.find_all("div", {"class": "contact-card-name mb-2"})
    script = soup.find_all("script")
    for i in script:
        if "var omniLocations" in i.text:
            jn = (
                i.text.replace("var omniLocations = [", "")
                .replace("];", "")
                .replace("'", '"')
                .strip()
                .replace("'", "")
                .replace("'", '"')
                .replace("\t", "")
                .replace("\n", "")
                .replace(",}", "}")
                .replace(",]", "]")
            )
            for o in range(len(jn.split("lng"))):
                if o > 0:
                    log.append(
                        jn.split("lng")[o]
                        .split(' "lat":')[0]
                        .replace('": "', "")
                        .replace('",', "")
                    )
                    lat.append(
                        jn.split("lng")[o]
                        .split(' "lat":')[1]
                        .replace('": "', "")
                        .replace('",', "")
                        .split("}")[0]
                        .replace('"', "")
                    )
                    ids.append(
                        jn.split("id")[o].split(",")[0].replace('":', "").strip()
                    )
    for index, i in enumerate(k):
        name = name1[index].text.strip().lstrip()
        try:
            phone = list(i.stripped_strings)[-1]
            if "-" not in phone:
                phone = ""
        except:
            phone = ""

        raw_data = list(i.stripped_strings)
        if len(raw_data) > 4:
            st = " ".join(raw_data[:2])
            city_line = raw_data[2]
        else:
            st = raw_data[0]
            city_line = raw_data[1]

        if st[-1:] == ",":
            st = st[:-1]

        city = city_line.split(",")[0]
        state = city_line.split(",")[1].split()[0]
        zip1 = city_line.split(",")[1].split()[1]

        sgw.write_row(
            SgRecord(
                locator_domain="https://www.omnisourceusa.com",
                page_url="https://www.omnisourceusa.com/locations",
                location_name=name,
                street_address=st,
                city=city,
                state=state,
                zip_postal=zip1,
                country_code="US",
                store_number=ids[index],
                phone=phone,
                location_type="",
                latitude=lat[index],
                longitude=log[index],
                hours_of_operation="",
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
