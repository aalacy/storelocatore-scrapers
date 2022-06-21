from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://joann.com/"
    api_url = "https://hosted.where2getit.com/joann/mystore/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E53EDE5D6-8FC1-11E6-9240-35EF0C516365%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Climit%3E2500%3C%2Flimit%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E98021%3C%2Faddressline%3E%3Clongitude%3E-122.2029132%3C%2Flongitude%3E%3Clatitude%3E47.7972338%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E3000%3C%2Fsearchradius%3E%3Cwhere%3E%3Cnew_in_store_meet_up%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fnew_in_store_meet_up%3E%3Cor%3E%3Ccustomframing%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcustomframing%3E%3Cedu_demos%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fedu_demos%3E%3Cbusykids%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fbusykids%3E%3Cbuyonline%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fbuyonline%3E%3Cvikingsewinggallery%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fvikingsewinggallery%3E%3Cproject_linus%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fproject_linus%3E%3Csewing_studio%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fsewing_studio%3E%3Cscissorsharpening%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fscissorsharpening%3E%3Cstore_features%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fstore_features%3E%3Cpetfriendly%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpetfriendly%3E%3Cglowforge%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fglowforge%3E%3Ccustom_shop%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcustom_shop%3E%3Cmonthlyevent%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fmonthlyevent%3E%3C%2For%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    poi = tree.xpath("//poi")
    for p in poi:

        location_name = "".join(p.xpath(".//name/text()"))
        ad1 = "".join(p.xpath(".//address1/text()")).strip()
        ad2 = "".join(p.xpath(".//address2/text()")).strip()
        street_address = (ad1 + " " + ad2).strip()

        city = "".join(p.xpath(".//city/text()"))
        state = "".join(p.xpath(".//state/text()")).strip()
        postal = "".join(p.xpath(".//postalcode/text()")).strip()
        country_code = "".join(p.xpath(".//country/text()"))
        store_number = "".join(p.xpath(".//clientkey/text()"))
        phone = "".join(p.xpath(".//phone/text()")).strip() or "<MISSING>"
        slug = city
        if slug.find(" ") != -1:
            slug = slug.replace(" ", "-")
        page_url = (
            f"https://stores.joann.com/{state.lower()}/{slug.lower()}/{store_number}/"
        )

        latitude = "".join(p.xpath(".//latitude/text()")).strip()
        longitude = "".join(p.xpath(".//longitude/text()")).strip()
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        tmp = []
        for d in days:
            day = d.capitalize()
            opens = "".join(p.xpath(f".//{d}open/text()")).strip()
            closes = "".join(p.xpath(f".//{d}close/text()")).strip()
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"
        cms = "".join(p.xpath(".//grandopening/text()")).strip()
        if cms.find("1") != -1:
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
