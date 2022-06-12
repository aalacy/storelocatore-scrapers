from bs4 import BeautifulSoup
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):

    base_url = "https://www.enterprisetrucks.com"
    r = session.get(base_url + "/truckrental/en_US/locations.html")
    soup = BeautifulSoup(r.text, "lxml")
    main = soup.find("div", {"id": "allUSLocations"}).find_all("a")
    for atag in main:
        page_url = base_url + atag["href"]
        r1 = session.get(base_url + atag["href"])
        tree = html.fromstring(r1.text)
        soup1 = BeautifulSoup(r1.text, "lxml")
        if "Our apologies…an unexpected error occurred." not in r1.text:
            try:
                location_name = soup1.find("input", {"id": "location_name"})["value"]
            except TypeError:
                continue
            street_address = soup1.find("input", {"id": "location_address"})["value"]
            addr = soup1.find("input", {"id": "location_address2"})["value"]
            city = addr.split(",")[0]
            state = addr.split(",")[1].strip().split(" ")[0]
            try:
                zipp = addr.split(",")[1].strip().split(" ")[1]
                if len(zipp) < 5:
                    zipp = "<MISSING>"
            except:
                zipp = "<MISSING>"
            phone = soup1.find("input", {"id": "location_phone"})["value"]
            try:
                latitude = soup1.find("input", {"id": "location_latitude"})["value"]
                longitude = soup1.find("input", {"id": "location_longitude"})["value"]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            mon_open = "".join(tree.xpath('//input[@name="hr_op_mon_st"]/@value'))
            mon_close = "".join(tree.xpath('//input[@name="hr_op_mon_end"]/@value'))
            tue_open = "".join(tree.xpath('//input[@name="hr_op_tue_st"]/@value'))
            tue_close = "".join(tree.xpath('//input[@name="hr_op_tue_end"]/@value'))
            wed_open = "".join(tree.xpath('//input[@name="hr_op_wed_st"]/@value'))
            wed_close = "".join(tree.xpath('//input[@name="hr_op_wed_end"]/@value'))
            thu_open = "".join(tree.xpath('//input[@name="hr_op_thu_st"]/@value'))
            thu_close = "".join(tree.xpath('//input[@name="hr_op_thu_end"]/@value'))
            fri_open = "".join(tree.xpath('//input[@name="hr_op_fri_st"]/@value'))
            fri_close = "".join(tree.xpath('//input[@name="hr_op_fri_end"]/@value'))
            sat_open = "".join(tree.xpath('//input[@name="hr_op_sat_st"]/@value'))
            sat_close = "".join(tree.xpath('//input[@name="hr_op_sat_end"]/@value'))
            sun_open = "".join(tree.xpath('//input[@name="hr_op_sun_st"]/@value'))
            sun_close = "".join(tree.xpath('//input[@name="hr_op_sun_end"]/@value'))
            hours_of_operation = f"Monday {mon_open} - {mon_close} Tuesday {tue_open} - {tue_close} Wednesday {wed_open} - {wed_close} Thursday {thu_open} - {thu_close} Friday {fri_open} - {fri_close} Saturday {sat_open} - {sat_close} Sunday {sun_open} - {sun_close}"

            row = SgRecord(
                locator_domain=base_url,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="US",
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

    base_url = "https://www.enterprisetrucks.com"
    r = session.get(base_url + "/truckrental/en_US/locations.html")
    soup = BeautifulSoup(r.text, "lxml")
    main = soup.find("div", {"id": "allCALocations"}).find_all("a")
    for atag in main:
        page_url = base_url + atag["href"]
        r1 = session.get(base_url + atag["href"])
        tree = html.fromstring(r1.text)
        soup1 = BeautifulSoup(r1.text, "lxml")
        if "Our apologies…an unexpected error occurred." not in r1.text:
            try:
                location_name = soup1.find("input", {"id": "location_name"})["value"]
            except TypeError:
                continue
            street_address = soup1.find("input", {"id": "location_address"})["value"]
            addr = soup1.find("input", {"id": "location_address2"})["value"]
            city = addr.split(",")[0]
            state = addr.split(",")[1].strip().split(" ")[0]
            zipp = " ".join(addr.split(",")[1].strip().split(" ")[-2:])
            if len(zipp) < 5:
                zipp = "<MISSING>"
            phone = soup1.find("input", {"id": "location_phone"})["value"]
            try:
                latitude = soup1.find("input", {"id": "location_latitude"})["value"]
                longitude = soup1.find("input", {"id": "location_longitude"})["value"]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            mon_open = "".join(tree.xpath('//input[@name="hr_op_mon_st"]/@value'))
            mon_close = "".join(tree.xpath('//input[@name="hr_op_mon_end"]/@value'))
            tue_open = "".join(tree.xpath('//input[@name="hr_op_tue_st"]/@value'))
            tue_close = "".join(tree.xpath('//input[@name="hr_op_tue_end"]/@value'))
            wed_open = "".join(tree.xpath('//input[@name="hr_op_wed_st"]/@value'))
            wed_close = "".join(tree.xpath('//input[@name="hr_op_wed_end"]/@value'))
            thu_open = "".join(tree.xpath('//input[@name="hr_op_thu_st"]/@value'))
            thu_close = "".join(tree.xpath('//input[@name="hr_op_thu_end"]/@value'))
            fri_open = "".join(tree.xpath('//input[@name="hr_op_fri_st"]/@value'))
            fri_close = "".join(tree.xpath('//input[@name="hr_op_fri_end"]/@value'))
            sat_open = "".join(tree.xpath('//input[@name="hr_op_sat_st"]/@value'))
            sat_close = "".join(tree.xpath('//input[@name="hr_op_sat_end"]/@value'))
            sun_open = "".join(tree.xpath('//input[@name="hr_op_sun_st"]/@value'))
            sun_close = "".join(tree.xpath('//input[@name="hr_op_sun_end"]/@value'))
            hours_of_operation = f"Monday {mon_open} - {mon_close} Tuesday {tue_open} - {tue_close} Wednesday {wed_open} - {wed_close} Thursday {thu_open} - {thu_close} Friday {fri_open} - {fri_close} Saturday {sat_open} - {sat_close} Sunday {sun_open} - {sun_close}"

            row = SgRecord(
                locator_domain=base_url,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="CA",
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
