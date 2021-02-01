import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    calocs = [
        "Abbotsford|7 OAKS SHOPPING CENTRE, 32900 SOUTH FRASER WAY|ABBOTSFORD|BC",
        "Anjou|Les Galeries D'anjou 7895 Boulevard Les Galeries D'anjou|Anjou|QC",
        "Banff|125 BANFF AVENUE|Banff|AB",
        "Barrie|GEORGIAN MALL, 465 BAYFIELD STREET|Barrie|ON",
        "Bayshore|BAYSHORE SHOPPING CENTRE, 100 BAYSHORE DR.|Bayshore|ON",
        "Bloor St|2 BLOOR ST EAST|TORONTO|ON",
        "Boulevard|CENTRE D'ACHATS LE BOULEVARD, 4150 RUE JEAN-TALON E|MONTREAL|QC",
        "Bramalea|Masonville Place, 1680 Richmond Street|London|ON",
        "Brossard|MAIL CHAMPLAIN, 2151 BOUL. LAPINIERE|Brossard|QC",
        "Burlington Mall|BURLINGTON MALL, 777 GUELPH LINE|Burlington|ON",
        "Cambridge|CAMBRIDGE CENTRE, 355 HESPELER ROAD 355 HESPELER ROAD|Cambridge|ON",
        "Capitale|LES GALERIES DE LA CAPITALE, 5401 BOUL. DES GALERIES|Quebec City|QC",
        "Carrefour Laval|Carrefour Laval 3045 Boulevard Le Carrefour|Laval|QC",
        "Centrepoint|CENTERPOINT MALL, 6500 YONGE STREET|Willowdale|ON",
        "Chinook|Chinook Centre 6455 Macleod Trail S.w|Calgary|AB",
        "Coquitlam|COQUITLAM CENTRE, 100 2929 BARNET HIGHWAY|Coquitlam|BC",
        "Darmouth|MICMAC MALL, 21 MICMAC BLVD.|Dartmouth|NS",
        "Dorval|LES PROMENADES GATINEAU, 1100 BOUL. MALONEY O.|Gatineau|QC",
        "Edmonton Centre|EDMONTON CITY CENTRE, 1200-10250 102 AVENUE NW|Edmonton|AB",
        "Eglinton|EGLINTON SQUARE, 1 EGLINTON SQUARE|Toronto|ON",
        "Erin Mills|ERIN MILLS TOWN CENTRE, 5100 ERIN MILLS PARKWAY|Mississauga|ON",
        "Fairview|FAIRVIEW MALL, 1800 SHEPPARD AVE. EAST|Willowdale|ON",
        "Gatineaul|LES PROMENADES GATINEAU, 1100 BOUL. MALONEY O.|Gatineau|QC",
        "Guildford|GUILDFORD TOWN CENTRE, 1400 GUILDFORD TOWN CENTRE|Surrey|BC",
        "Kamloops|PACIFIC CENTRE, 674 GRANVILLE STREET|Vancouver|BC",
        "Kingston Cataraqi Centre|Cataraqui Centre 945 Gardiners Road|Kingston|QC",
        "Kingsway|KINGSWAY GARDEN MALL, 109TH ST PRINCESS ELIZ AVE|Edmonton|AB",
        "Kitchener|FAIRVIEW PARK SHOPPING CT, 3050 KINGSWAY DRIVE|Kitchener|ON",
        "Langley|WILLOWBROOK MALL, #320 - 19705 FRASER HWY|Langley|BC",
        "Lasalle|CARREFOUR ANGRIGNON, 7091 BOUL NEWMAN|Lasalle|ON",
        "Laurier|PLACE LAURIER, 2740 BOUL. LAURIER|Saint Foy|QC",
        "Laval|CENTRE LAVAL, 1600 BOUL. LE CORBUSIER DORVAL|Laval|QC",
        "Lethbridge|LETHBRIDGE CENTRE MALL, 200 4TH AVENUE SOUTH|Lethbridge|AB",
        "Limeridge|LIMERIDGE MALL, 999 UPPER WENTWORTH ST.|Hamilton|ON",
        "London White Oaks|WHITE OAKS MALL, 1105 WELLINGTON RD. SOUTH|London|ON",
        "Londonderry|LONDONDERRY MALL N.W.|Edmonton|AB",
        "Lougheed|LOUGHEED MALL, 9855 AUSTIN ROAD|Burnaby|BC",
        "Mapleview The Bay|Mapleview Mall, 900 Maple Avenue|Burlington|ON",
        "Market Mall The Bay|Market Mall, 3625 Shaganappi Trail Nw|Calgary|AB",
        "Markville|MARKVILLE SHOPPING CENTRE, 5000 HWY 7|Markham|ON",
        "Masonville|1680 Richmond Street|London|ON",
        "Mayfair|MAYFAIR SHOPPING CENTRE, #221 - 3125 DOUGLAS STREET|Victoria|BC",
        "Medicine Hat|MEDICINE HAT SHOPPING MALL, 3292 DUNMORE ROAD SE|Medicine Hat|AB",
        "Metrotown Centre The Bay|Metrotown Centre, 4850 Kingsway|Burnaby|BC",
        "Midtown Plaza The Bay|Midtown Plaza, 201 First Avenue South|Saskatoon|SK",
        "Montreal Temp|Montreal Dtn 585|Montreal|QC",
        "Nanaimo|WOODGROVE CENTRE, 6631 ISLAND HWY.|Nanaimo|BC",
        "Oakridge|OAKRIDGE SHOPPING CENTRE, 650 41ST AVENUE|Vancouver|BC",
        "Oakville Place|240 Leighland Ave|Oakville|ON",
        "Orchard Park The Bay|Orchard Park Shopping Centre, 1415-2271 Harvey Ave.|Kelowna|BC",
        "Orleans|PLACE D'ORLEANS, 110 PLACE D'ORLEANS DRIVE|Orleans|ON",
        "Oshawa|OSHAWA SHOPPING CENTRE, 419 KING STREET W|Oshawa|ON",
        "Park Royal|PARK ROYAL SHOPPING CTR, 725 PARK ROYAL NORTH W|Vancouver|BC",
        "Pen Centre|PEN CENTRE SHOPPING PLAZA, 221 GLENDALE AVENUE|St. Catherines|ON",
        "Penticton|CHERRY LANE SHOPPING CTR, 2111 MAIN STREET|Penticton|BC",
        "Pickering|PICKERING TOWN CENTRE, 1355 KINGSTON ROAD|Pickering|ON",
        "Pointe Claire Temp|La Baie D?udson - Fairview Pointe Claire 6790 Route Transcanada|Pointe-Claire|QC",
        "Polo Park|Polo Park 1485 Portage Avenue|Winnipeg|AB",
        "Prince George|PARKWOOD SHOPPING CENTRE, 140- 1600 15TH AVENUE|Prince George|BC",
        "Queen Street|The Bay Queens Street 176 Yonge Street|Toronto|ON",
        "Red Deer|BOWER MALL, 4900 MOLLY BANNISTER DR.|Red Deer|AB",
        "Regina|CORNWALL CENTRE REGINA, 2150 -11TH AVENUE|Regina|SK",
        "Richmond Hill|L4C4X5, 9350 YONGE STREET|Richmand Hill|ON",
        "Rideau|73 Rideau St|Ottawa|ON",
        "Rockland|CENTRE ROCKLAND, 2435 ROCKLAND ROAD TMR|Montreal|QC",
        "Rosemere|PLACE ROSEMERE, 401 BOUL. LABELLE|Rosemere|QC",
        "Saskatoon|MIDTOWN PLAZA, 201 FIRST AVENUE SOUTH|Saskatoon|SK",
        "Scarborough Toronto|Scarborough Town Centre, 300 Borough Drive|Scarborough|ON",
        "Sherbrooke|CARREFOUR DE L'ESTRIE, 3000 BOUL. DE PORTLAND|Sherbrooke|QC",
        "Sherway|Sherway Gardens 25 The West Mall|Etobicoke|ON",
        "South Centre Calgary|100 Anderson Road Se South Centre Mall|Calgary|AB",
        "Southgate Centre The Bay|150-5015 111th Street|Edmonton|AB",
        "Square One|Square One 100 City Centre Drive|Mississauga|ON",
        "St Bruno|LES PROMENADES SAIN-BRUNO, 800 BOUL DES PROMENADES|St. Bruno|QC",
        "St. Albert|ST. ALBERT CENTRE, 375 ST. ALBERT TRAIL|St. Albert|AB",
        "St.Laurent|ST. LAURENT CENTER, 1200 ST. LAUREN BOUL|Ottawa|ON",
        "St.Vital|ST. VITAL CENTRE, 1225 ST. MARY'S ROAD|Winnipeg|MB",
        "Sunridge|SUNRIDGE MALL, 2525 36 STREET NE|Calgary|AB",
        "Sydney|MAYFLOWER SHOPPING MALL, 800 GRAND LAKE ROAD|Sydney|NS",
        "Temp Calagary Dtn|Hudson's Bay - Calgary Downtown 200-8th Avenue S.w.|Calgary|AB",
        "The Bay Website|100 Metropolitan Rd|Scarborough|ON",
        "Upper Canada Mall Newmarket|Upper Canada Mall, 17600 Yonge St. N.|Newmarket|ON",
        "Vancouver|Pacific Centre 674 Granville Street|Vancouver|BC",
        "Vernon|VILLAGE GREEN MALL, STE 104900  27TH STREET VERNON|Vernon|BC",
        "Victoria|THE BAY CENTRE, 1150 DOUGLAS STREET|Victoria|BC",
        "Waterloo|CONESTOGA MALL, 550 KING STREET NORTH|Waterloo|ON",
        "West Edmonton Temp|Hudson's Bay - West Edmonton Mall 8882 170 St Nw|Edmonton|AB",
        "Windsor|DEVONSHIRE MALL, 3030 HOWARD AVENUE|Windsor|ON",
        "Winnipeg Dtn|450 PORTAGE AVE.|Winnipeg|MB",
        "Woodbine|WOODBINE PLAZA, 500 REXDALE BLVD|Toronto|ON",
        "Yorkdale|Yorkdale Plaza 3401 Dufferin Street|North York|ON",
    ]

    urls = [
        "https://www.topshop.com/store-locator?country=United+States",
        "https://www.topshop.com/store-locator?country=Canada",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '"stores":[' in line:
                items = (
                    line.split('"stores":[')[1]
                    .split('],"selectedStore":{}')[0]
                    .split('"storeId":"')
                )
                for item in items:
                    if "brandPrimaryEStoreId" in item:
                        store = item.split('"')[0]
                        typ = item.split('"brandName":"')[1].split('"')[0]
                        name = item.split('"name":"')[1].split('"')[0]
                        website = "topshop.com"
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                        add = item.split('"line2":"')[1].split('"')[0]
                        if "Nordstrom" in item:
                            typ = "Nordstrom Topshop"
                        if add == "":
                            add = item.split('"line1":"')[1].split('"')[0]
                        country = "US"
                        city = item.split('"city":"')[1].split('"')[0]
                        if "Canada" in url:
                            country = "CA"
                        state = "<MISSING>"
                        zc = item.split('"postcode":"')[1].split('"')[0]
                        hours = "Mon: " + item.split('"monday":"')[1].split('"')[0]
                        hours = (
                            hours
                            + "; Tue: "
                            + item.split('"tuesday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Wed: "
                            + item.split('"wednesday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Thu: "
                            + item.split('"thursday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Fri: "
                            + item.split('"friday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sat: "
                            + item.split('"saturday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sun: "
                            + item.split('"sunday":"')[1].split('"')[0]
                        )
                        if "-" not in hours:
                            hours = "<MISSING>"
                        loc = "<MISSING>"
                        phone = item.split('"telephoneNumber":"')[1].split('"')[0]
                        if phone == "":
                            phone = "<MISSING>"
                        if zc == "":
                            zc = "<MISSING>"
                        if "299 CENTRAL" in add:
                            name = "CENTRAL STATES DC"
                            add = "5050 CHAVELLE DRIVE"
                            city = "Washington"
                            state = "DC"
                        if "Cedar Rapids" in name:
                            city = "Cedar Rapids"
                        if country == "CA":
                            for lname in calocs:
                                if name == lname.split("|")[0]:
                                    add = lname.split("|")[1]
                                    city = lname.split("|")[2]
                                    state = lname.split("|")[3]
                                    if "," in add:
                                        add = add.split(",", 1)[1].strip()
                                    zc = "<MISSING>"
                        yield [
                            website,
                            loc,
                            name,
                            add,
                            city,
                            state,
                            zc,
                            country,
                            store,
                            phone,
                            typ,
                            lat,
                            lng,
                            hours,
                        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
