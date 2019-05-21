'use strict';

const   axios       = require('axios'),
        converter   = require('../lib/converter'),
        fs          = require('fs-extra'),
        path        = require('path'),
        config      = require('../config.json');


(async() => {
    const apiurl = 'https://www.shopnsavefood.com/DesktopModules/StoreLocator/API/StoreWebAPI.asmx/GetAllStores';
    const fileLocation = `${config.General_Settings.filenamePrefix}${config.Website_Settings.ShopNSave.filenameBody}.csv`;

    try {
        const response = await axios.get(apiurl);
        if (response.status === 200){

            //Convert the file into a JSON Object
            const data = await converter.xml2json(response.data);
            
            //If a data file exists in our file system, delete current file, then create a new file. 
            if (await fs.existsSync(path.join(__dirname, fileLocation))) { 
                await fs.unlink(path.join(__dirname, fileLocation));
                await fs.writeFile(path.join(__dirname, fileLocation), config.General_Settings.headerRow); 
            } else { 
                await fs.writeFile(path.join(__dirname, fileLocation), config.General_Settings.headerRow); 
            }


            // const allLocationsData = data['ArrayOfStore']['Store]; <--- Use for all data including gas stations
            const storeData = data['ArrayOfStore']['Store'].filter((x) => x.IsGasStation === 'false');
            const gasStation = data['ArrayOfStore']['Store'].filter((x) => x.IsGasStation === 'true');

            
        
            //For Store Data -> Combines hours in one property, fills in empty data, formats phone numbers to 10 digits 
            for await (let obj of storeData) {
                
                if (obj.hasOwnProperty('Hours2') && obj['Hours2'] != '') {
                    obj['Hours'] = obj['Hours'] + ', ' + (obj['Hours2']);
                }

                for await(let property of Object.keys(obj)){
                    if (obj[property] === '') {
                        obj[property] = 'NO-DATA';
                    }
                    
                    if (property === 'Phone' && obj[property] != 'NO-DATA'){
                        obj[property] = converter.formatPhoneNumber(obj[property]);
                    }
                    if (property === 'IsGasStation' && obj[property] === 'false') {
                        obj[property] = 'Store';
                    }
                }
            }

            //For Gas Station Data -> Since it has no phone numbers or hours of operation
            for await (let obj of gasStation) {
                for await (let property of Object.keys(obj)) {
                    obj[property] = converter.sanitizeInput(obj[property]);
                    if (obj[property] === '') {
                        obj[property] = 'NO-DATA';
                    }
                    if (!obj.hasOwnProperty('Phone')) {
                        obj['Phone'] = 'NO-DATA';
                    }
                    if (!obj.hasOwnProperty('Hours')) {
                        obj['Hours'] = 'NO-DATA';
                    }
                    if (property === 'IsGasStation' && obj[property] === 'true') {
                        obj[property] = 'Gas Station';
                    }
                }
            }
        
            //Upload storeData, then gasStationData
            await updateShopCSV(storeData, fileLocation);
            await updateShopCSV(gasStation, fileLocation);
            
        } else {
            throw response.status;
        }
    } catch (error) {
        console.log(error);
    }
    
})();

const updateShopCSV = async (arrayOfObjects, fileLocation) => {

    for await (let obj of arrayOfObjects){
        let locatorDomain       = 'shopnsavefood.com__api',
            locationName        = obj.Name,
            streetAddress       = obj.Address1,
            city                = obj.City,
            state               = obj.State,
            zip                 = obj.Zip,
            countryCode         = 'US',
            storeNumber         = obj.StoreID,
            phone               = obj.Phone,
            locationType        = obj.IsGasStation,
            naics               = 'NO-DATA',
            latitude            = obj.Latitude,
            longitude           = obj.Longitude,
            hours_of_operation  = obj.Hours
    
        await fs.appendFile(
            path.join(__dirname, fileLocation), 
            `"${locatorDomain}","${locationName}","${streetAddress}","${city}","${state}","${zip}","${countryCode}","${storeNumber}","${phone}","${locationType}","${naics}","${latitude}","${longitude}","${hours_of_operation}"\n`
        );
    }
}


/*

Sample const "data" output

[ { StoreID: '119',
    Number: '1122',
    Name: 'Youngwood',
    Website: 'www.jamiesonfamilymarkets.com',
    Address1: '250 South Third Street',
    Address2: '',
    City: 'Youngwood',
    State: 'PA',
    Zip: '15697',
    Hours: 'Mon-Sun 7am-10pm',
    Hours2: '',
    Phone: '724-925-1810',
    PharmacyPhone: '',
    Fax: '',
    Latitude: '40.2358062',
    Longitude: '-79.5807462',
    IsGasStation: 'false',
    IsActive: 'true',
    IsPumpPerk: 'false',
    AreaID: '103' }
]
*/




