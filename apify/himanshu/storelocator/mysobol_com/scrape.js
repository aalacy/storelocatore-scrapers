const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://mysobol.com/wp-admin/admin-ajax.php?page=1&sortBy=id&sortDir=asc&perpage=0&with_schema=true&action=mapsvg_data_get_all&map_id=2365&table=database';
 
async function scrape(){

  return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
    var ref = JSON.parse(res.body);
    var ref1 = ref.objects;
    // console.log(ref1);
        const $  =cheerio.load(html);
        var items=[];
        function mainhead(i)

                    {
                        if(ref1.length>i)

                            {

          
          var obj = ref1[i];
          var location_name = obj.title;
          var address_tmp = obj.address;
          var address_tmp1 = address_tmp.split(',');
          var phone = obj.phone.replace('Location orders only\t','<MISSING>').replace('.','').replace('.','');
          var latitude = obj.location.lat;
          var longitude = obj.location.lng;
          var hour = obj.hours;
          var store_number = obj.id;


          if(address_tmp1.length == 2){
            var address_tmp2 = address_tmp1[0].split('\n') ;
          var state_tmp = address_tmp1[1].split(' ');
          var state = state_tmp[1];
          var zip = state_tmp[2];
          var address = address_tmp2[0];
          var city = address_tmp2[1];
          

          }

          else if (address_tmp1.length == 3){
            var address = address_tmp1[0];
            var city_tmp = address_tmp1[1].split('\n');
            var city = city_tmp[1];
            var state_tmp = address_tmp1[2];
            var state_tmp1 =state_tmp.split(' ');
            var state =state_tmp1[1];
            var zip = state_tmp1[2];

           

          }
          
          items.push({  

            locator_domain: 'https://mysobol.com/', 

            location_name: location_name, 

            street_address: address,

            city: city, 

            state: state,

            zip:  zip,

            country_code: 'US',

            store_number: store_number,

            phone: phone,

            location_type: 'yourasecu',

            latitude: latitude,

            longitude: longitude, 

            hours_of_operation: hour}); 

            

            mainhead(i+1);

          }


          else{
      
          resolve(items);
      
          }
   } 

mainhead(0);
        
       

}
});
});


}
 

Apify.main(async () => {

    

    const data = await scrape();
    
   
    await Apify.pushData(data);
  
  });
