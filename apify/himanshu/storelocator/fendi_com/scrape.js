const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
var items=[];
 
var country =['US','CA'];
async function scrape(){

return new Promise(async (resolve,reject)=>{
  
  function mainhead(i)

  {

      if(country.length>i)

      {

  var url = 'https://www.fendi.com/au/store-locator?listJson=true&country-selectize=&fendiType=BOUTIQUE&service=&line=&xlat=25.82&xlng=-124.38999999999999&ylat=49.38&ylng=-66.94&country='+country[i];

request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
   
     const $  =cheerio.load(html);
       
        
        var ref = JSON.parse(res.body);
         
        
                function mainhead1(i1){

                  if(ref.length>i1)

                  {
                    var obj = ref[i1];
                    var location_name = obj.displayName;
                    
                    var address = obj.address.line1;
                    var city =obj.address.town;
                    var state = '<MISSING>';
                    var zip = obj.address.postalCode.trim();
                    var phone = obj.address.phone.trim();
                    var latitude = obj.geoPoint.latitude;
                    var longitude = obj.geoPoint.longitude;
                    var country_code = obj.address.country.isocode;
                    var hour=  '<INACCESSIBLE>';

                           items.push({
                                locator_domain : 'https://www.fendi.com/',
                                location_name : location_name,
                                street_address : address,
                                city:city,
                                state:state,
                                zip:zip,
                                country_code: country_code,
                                store_number:'<MISSING>',
                                phone:phone,
                                location_type:'fendi',
                                latitude:latitude,
                                longitude :longitude,
                                hours_of_operation:hour
                                
                                });  
                                mainhead1(i1+1);
                     }

                 else{

                  mainhead(i+1);

                    }

            }
               
             mainhead1(0);

            }
    });

    
                }

                else{
   
                  resolve(items);
  
                 }
            }
  
          mainhead(0);
 
  });
}

  
    
   
  
  Apify.main(async () => {
  
      
  
      const data = await scrape();
     
      await Apify.pushData(data);
     
    
    });
