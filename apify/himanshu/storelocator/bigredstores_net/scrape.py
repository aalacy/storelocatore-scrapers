from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bigredstores_net")

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://bigredstores.net/"
    locator_domain = base_url
    country_code = "US"
    latitude = ""
    longitude = ""

    location_url = "https://bigredstores.net/locations/"
    r = session.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for link in soup.find_all("div", class_="has-post-thumbnail"):
        list_add = list(link.stripped_strings)
        street_address = list_add[0].strip()

        city = list_add[-1].strip()
        page_url = link.a["href"]
        r_loc = session.get(link.a["href"], headers=headers)
        soup_loc = BeautifulSoup(r_loc.text, "html.parser")
        try:
            coords = soup_loc.find("div", class_="et_pb_map_pin")
            if coords == None:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            else:
                latitude = coords["data-lat"]
                longitude = coords["data-lng"]
            content = list(
                soup_loc.find_all("div", class_="et_pb_tab_content")[1].stripped_strings
            )

            if "|" not in " ".join(content):

                if len(content) > 2:
                    location_name = content[0].strip()
                    state = content[2].split(",")[1].split()[0].strip()
                    zipp = content[2].split(",")[1].split()[-1].strip()
                    phone_list = re.findall(
                        re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
                        str(content[-1]),
                    )
                    if phone_list:
                        phone = phone_list[-1]
                    else:
                        phone = "<MISSING>"

                else:
                    location_name = "<MISSING>"
                    state = content[-1].split(",")[1].split()[0].strip()
                    zipp = content[-1].split(",")[1].split()[-1].strip()
                    phone = "<MISSING>"

            else:
                location_name = "<MISSING>"
                state = content[-1].split(",")[1].split()[0].strip()
                zipp = content[-1].split(",")[1].split()[-1].strip()
                phone = "<MISSING>"

        except:
            location_name = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
            phone = "<MISSING>"

        if "72015" in phone:
            phone = "<MISSING>"
        if "3544 Airport Road, Pearcy, AR" in street_address:
            street_address = list_add[0].split(",")[0].strip()
            city = list_add[0].split(",")[1].strip()
            state = list_add[0].split(",")[-1].strip()
            zipp = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
