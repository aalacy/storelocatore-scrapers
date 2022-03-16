import yaml
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_root(_id):
    r = session.get(
        f"https://stores.boldapps.net/front-end/get_store_info.php?shop=rocky-mountain-chocolate-factory.myshopify.com&data=detailed&store_id={_id}"
    )
    source = r.json()["data"]

    return html.fromstring(source)


def remove_comma(text):
    if text.endswith(","):
        return text[:-1]
    return text


def fetch_data(sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'markersCoords.push(')]/text()")
    )
    tex = text.split("markersCoords.push(")
    tex.pop(0)
    for t in tex:
        _id = t.split("id:")[1].split(",")[0].strip()
        if _id == "0":
            break

        j = yaml.load(t.split(", id")[0] + "}", Loader=yaml.Loader)
        root = get_root(_id)

        street_address = "".join(root.xpath("//span[@class='address']/text()")).strip()
        city = remove_comma("".join(root.xpath("//span[@class='city']/text()")).strip())
        state = "".join(root.xpath("//span[@class='prov_state']/text()")).strip()
        postal = remove_comma(
            "".join(root.xpath("//span[@class='postal_zip']/text()")).strip()
        )
        store_number = _id
        location_name = "".join(root.xpath("//span[@class='name']/text()")).strip()
        if location_name.find("(") != -1:
            location_name = location_name.split("(")[0].strip()

        phone = "".join(root.xpath("//span[@class='phone']/text()")).strip()
        latitude = j.get("lat")
        longitude = j.get("lng")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="CA",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://rockychoc.com/"
    page_url = "https://shop.rockychoc.com/apps/store-locator/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
