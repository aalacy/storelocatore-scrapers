const Apify = require('apify');
const axios = require('axios');

Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

function stripNumbers(text) {
    return text.replace(/[0-9]/g, '');
}

function isLetters(c) {
    return c.toLowerCase() != c.toUpperCase();
}

async function scrape() {

    var response = await axios.get('https://www.muji.com/storelocator/index.php?_ACTION=_SEARCH&c=us&lang=EN&swLat=-89.99919060379034&swLng=-180&neLat=89.9944437326464&neLng=180');

    var existingLatitudeLongitudePairs = {};
    var existingStoreNames = {};

    var stores = response.data.map(store => {
        if(existingStoreNames[store.shopname] == true) {
            return null;
        } 
        existingStoreNames[store.shopname]  = true;

        var lat = '<MISSING>';
        var lng = '<MISSING>';
        if(existingLatitudeLongitudePairs[store.latitude+store.longitude] == null) {
            existingLatitudeLongitudePairs[store.latitude+store.longitude] = true;
            lat = parseFloat(store.latitude);
            lng = parseFloat(store.longitude);
        }

        //default country code is JA
        var countryCode = 'JA';
        if(isLetters(store.shopid.substring(0,2))) {
            countryCode = store.shopid.substring(0,2);
        }

        var addressParts = store.shopaddress.split(',')
            .filter(p => p != null && p.trim() != "");
        var address1 = "<MISSING>", address2 = "", city = "<MISSING>", state = "<MISSING>", zip = store.zipcode || "<MISSING>";
        if(addressParts.length === 3) {
            address1 = addressParts[0];
            city = addressParts[1];
            state = stripNumbers(addressParts[2]);
        }
        if(addressParts.length === 4) {
            address1 = addressParts[0];
            address2 = addressParts[1];
            city = addressParts[2];
            state = stripNumbers(addressParts[3]);

            if(countryCode === 'CA') {
                address2 = "<MISSING>";
                city = addressParts[1]
                state = addressParts[2];
                zip = addressParts[3];
            }
        }
        if(addressParts.length === 5) {
            address1 = addressParts[0];
            address2 = addressParts[1] + addressParts[2];
            city = addressParts[3];
            state = stripNumbers(addressParts[4]);
        }
        if(addressParts.length === 6) {
            address1 = addressParts[0] + addressParts[1];
            address2 = addressParts[2] + addressParts[3];
            city = addressParts[4];
            state = stripNumbers(addressParts[5]);
        }
        
        var phone = "<MISSING>";
        if(store.tel && store.tel.trim() != "") {
            phone = store.tel;
        }

        return {
            locator_domain: 'muji.com',
            location_name: store.shopname,
            street_address: (address1 + " " + address2).trim(),
            city: city.trim(),
            state: state.trim(),
            zip: zip.trim(),
            country_code: countryCode,
            store_number: store.shopid,
            phone:  phone.trim(),
            location_type: store.shopname,
            latitude: lat,
            longitude: lng,
            hours_of_operation: store.opentime || "<MISSING>",
        };
    }).filter(s => s != null);


    return stores;

}
