/*

(async() => {

    const fileLocation = `${config.General_Settings.filenamePrefix}${config.Website_Settings.ShopNSave.filenameBody}.csv`;

    const data = await fs.readFile(path.join(__dirname, './test.json'), 'utf-8');
    const data2 = JSON.parse(data);

    //If a data file exists in our file system, delete current file, then create a new file. 
    if (await fs.existsSync(path.join(__dirname, fileLocation))) { 
        await fs.unlink(path.join(__dirname, fileLocation));
        await fs.writeFile(path.join(__dirname, fileLocation), config.General_Settings.headerRow); 
    } else { 
        await fs.writeFile(path.join(__dirname, fileLocation), config.General_Settings.headerRow); 
    }

    // const allLocationsData = data2['ArrayOfStore']['Store];
    const storeData = data2['ArrayOfStore']['Store'].filter((x) => x.IsGasStation === 'false');

    //Combines hours in one property, fills in empty data, formats phone numbers to 10 digits 
    for await (let obj of storeData) {
        if ( typeof(obj['Hours2'] != undefined) && obj['Hours2'] != '') {
            obj['Hours'] = obj['Hours'] + ', ' + (obj['Hours2']);
        }
        for await(let property of Object.keys(obj)){
            if (obj[property] === '') {
                obj[property] = 'NO-DATA';
            }
            if (property === "Phone" && obj[property] != 'NO-DATA'){
                obj[property] = converter.formatPhoneNumber(obj[property]);
            }
        }
    }

    //Upload data to .csv -> There is no data for country. 'US' used a placeholder until it becomes necessary to compare address with US addresses. 
    for await (let obj of storeData){
        let locatorDomain       = 'shopnsavefood.com__api',
            locationName        = obj.Name,
            streetAddress       = obj.Address1,
            city                = obj.City,
            state               = obj.State,
            zip                 = obj.Zip,
            countryCode         = 'US',
            storeNumber         = obj.StoreID,
            phone               = obj.Phone,
            locationType        = 'NO-DATA',
            naics               = 'NO-DATA',
            latitude            = obj.Latitude,
            longitude           = obj.Longitude,
            hours_of_operation  = obj.Hours
    
        await fs.appendFile(
            path.join(__dirname, fileLocation), 
            `"${locatorDomain}","${locationName}","${streetAddress}","${city}","${state}","${zip}","${countryCode}","${storeNumber}","${phone}","${locationType}","${naics}","${latitude}","${longitude}","${hours_of_operation}"\n`
        );
    }

})();
*/
