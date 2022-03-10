from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "http://davinails.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Api-Key": "da2-kczsxgnisnd2fgf4ap3hzmabxe",
        "x-amz-user-agent": "aws-amplify/4.3.3 js",
        "Origin": "https://my.atlistmaps.com",
        "Connection": "keep-alive",
        "Referer": "https://my.atlistmaps.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
    }

    data = '{"query":"query GetMap($id: ID!) {\\n  getMap(id: $id) {\\n    id\\n    name\\n    owner\\n    markerColor\\n    markerShape\\n    markerSize\\n    markerIcon\\n    markerProgrammaticIconType\\n    markerBorder\\n    markerCustomImage\\n    markerCustomIcon\\n    markerCustomStyle\\n    defaultZoom\\n    gestureHandling\\n    zoomHandling\\n    zoomControl\\n    fullscreenControl\\n    streetViewControl\\n    mapType\\n    showTraffic\\n    showTransit\\n    showBicycling\\n    showSidebar\\n    showModals\\n    showDirectionsButton\\n    showSearchbox\\n    showCurrentLocation\\n    showTitle\\n    showLightbox\\n    showBranding\\n    highlightSelectedMarker\\n    permission\\n    password\\n    mapStyle\\n    mapStyleGenerated\\n    mapStyleRoads\\n    mapStyleLandmarks\\n    mapStyleLabels\\n    mapStyleIcons\\n    modalPosition\\n    modalBackgroundColor\\n    modalPadding\\n    modalRadius\\n    modalShadow\\n    modalTail\\n    modalTitleVisible\\n    modalTitleColor\\n    modalTitleSize\\n    modalTitleWeight\\n    modalAddressVisible\\n    modalAddressLink\\n    modalAddressColor\\n    modalAddressSize\\n    modalAddressWeight\\n    modalNoteVisible\\n    modalNoteColor\\n    modalNoteSize\\n    modalNoteWeight\\n    itemsOrder\\n    groupsCollapsed\\n    categories(limit: 1000) {\\n      items {\\n        id\\n        name\\n        collapsed\\n        itemsOrder\\n        markerColor\\n        markerSize\\n        markerIcon\\n        markerProgrammaticIconType\\n        markerShape\\n        markerBorder\\n        markerCustomImage\\n        markerCustomIcon\\n      }\\n      nextToken\\n    }\\n    shapes(limit: 1000) {\\n      items {\\n        id\\n        lat\\n        long\\n        zoom\\n        name\\n        paths\\n        fill\\n        stroke\\n        color\\n        width\\n        height\\n        type\\n      }\\n      nextToken\\n    }\\n    markers(limit: 1000) {\\n      items {\\n        id\\n        name\\n        lat\\n        long\\n        placeId\\n        formattedAddress\\n        notes\\n        createdAt\\n        color\\n        icon\\n        size\\n        shape\\n        border\\n        customImage\\n        customIcon\\n        customStyle\\n        useCoordinates\\n        useHTML\\n        images(limit: 1000) {\\n          items {\\n            id\\n            name\\n            image\\n          }\\n          nextToken\\n        }\\n      }\\n      nextToken\\n    }\\n  }\\n}\\n","variables":{"id":"b37b90e4-2e04-4604-acdf-ad47099f14bb"}}'

    r = session.post(
        "https://hin73p6qljbg7aoenfajej2dim.appsync-api.us-east-1.amazonaws.com/graphql",
        headers=headers,
        data=data,
    )
    js = r.json()
    for j in js["data"]["getMap"]["itemsOrder"]:
        slug = j
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Api-Key": "da2-kczsxgnisnd2fgf4ap3hzmabxe",
            "x-amz-user-agent": "aws-amplify/4.3.3 js",
            "Origin": "https://my.atlistmaps.com",
            "Connection": "keep-alive",
            "Referer": "https://my.atlistmaps.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "TE": "trailers",
        }

        data = (
            '{"query":"query GetMarker($id: ID!) {\\n  getMarker(id: $id) {\\n    id\\n    name\\n    lat\\n    long\\n    placeId\\n    formattedAddress\\n    notes\\n    createdAt\\n    updatedAt\\n    color\\n    icon\\n    size\\n    shape\\n    border\\n    customImage\\n    customStyle\\n    useCoordinates\\n    useHTML\\n    imagesOrder\\n    map {\\n      id\\n      name\\n      owner\\n      createdAt\\n      updatedAt\\n      markerColor\\n      mapStyle\\n      defaultZoom\\n      zoomControl\\n      fullscreenControl\\n      streetViewControl\\n      scaleControl\\n      mapType\\n      markers {\\n        nextToken\\n      }\\n    }\\n    comments {\\n      items {\\n        id\\n        owner\\n        content\\n      }\\n      nextToken\\n    }\\n    images(limit: 1000) {\\n      items {\\n        id\\n        name\\n        image\\n      }\\n      nextToken\\n    }\\n  }\\n}\\n","variables":{"id":"'
            + slug
            + '"}}'
        )

        r_1 = session.post(
            "https://hin73p6qljbg7aoenfajej2dim.appsync-api.us-east-1.amazonaws.com/graphql",
            headers=headers,
            data=data,
        )
        jj = r_1.json()["data"]["getMarker"]
        try:
            line = "".join(jj.get("formattedAddress")).replace("\n", " ").strip()
            line = " ".join(line.split()).replace("# ", "#")
        except:
            continue
        if line.find("DaVi Nails inside WM") != -1:
            line = " ".join(
                " ".join(line.split("DaVi Nails inside WM")[1].split("#")[1:]).split()[
                    1:
                ]
            )
        if line.find("DaVi Nails in WM") != -1:
            line = " ".join(
                " ".join(line.split("DaVi Nails in WM")[1].split("#")[1:]).split()[1:]
            )
        if line.find("DaVi Nails (Inside WM)") != -1:
            line = " ".join(
                " ".join(
                    line.split("DaVi Nails (Inside WM)")[1].split("#")[1:]
                ).split()[1:]
            )
        if line.find("DaVi nails inside WM") != -1:
            line = " ".join(
                " ".join(line.split("DaVi nails inside WM")[1].split("#")[1:]).split()[
                    1:
                ]
            )
        if line.find("DaVi Nals inside WM") != -1:
            line = " ".join(
                " ".join(line.split("DaVi Nals inside WM")[1].split("#")[1:]).split()[
                    1:
                ]
            )
        if line.find("DaVi Nails inside HEB") != -1:
            line = " ".join(
                " ".join(line.split("DaVi Nails inside HEB")[1].split("#")[1:]).split()[
                    1:
                ]
            )
        if line.find("DaVi Nails at") != -1:
            line = " ".join(line.split("DaVi Nails at")[1].split()[1:])
        if line.find("DaVi Nails insie WM") != -1:
            line = " ".join(
                " ".join(line.split("DaVi Nails insie WM")[1].split("#")[1:]).split()[
                    1:
                ]
            )

        a = parse_address(USA_Best_Parser(), line)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        info = "".join(jj.get("formattedAddress")).split("\n")
        info = list(filter(None, [a.strip() for a in info]))
        if city == "<MISSING>":
            city = info[-1].split(",")[0].strip()
        location_name = "".join(jj.get("name")).split(",")[0]
        phone = jj.get("notes")
        phone = str(phone)
        if phone.find("\n") != -1:
            phone = phone.split("\n")[0]
        phone = (
            phone.replace("Phone :", "")
            .replace("<b>Phone:</b>", "")
            .replace("Phone:", "")
            .replace("\n", "")
            .replace("<b>", "")
            .replace("</b>", "")
            .replace("None", "")
            .strip()
        )
        if phone.find("phone & fax") != -1:
            phone = phone.split("phone & fax")[0].strip()
        phone = phone or "<MISSING>"
        latitude = jj.get("lat")
        longitude = jj.get("long")
        page_url = "http://davinails.com/locations/"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=line,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
