const paymentResult=document.getElementById("payment-result")
const bookTripItem=document.getElementById("booktripItem");
var main="";
var context="";


bookTripItem.addEventListener("click",()=>{
  window.location.href="/booking";
})

function getPaymentResult(){
let token = localStorage.getItem("token");
if(token){
url=window.location.href
order_number= url.split('=')[1]
fetch(`/api/orders/${order_number}`,{
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
})
.then((resp) => {
  return resp.json().then((data) => {
    if (!resp.ok) {
      throw new Error(`HTTP error! status: ${resp.status}, message: ${data.message}`);
    }
    return data;
  });
})
.then((data)=>{
  console.log(data)
  //attractionId=data.data.trip.attraction.id
  ordernumber=data.data.number;
  attractionname=data.data.trip.attraction.name;
  address=data.data.trip.attraction.address;
  time=data.data.trip.time; 
  date=data.data.trip.date;
  price=data.data.price;
  status=data.data.status;
  contactName=data.data.contact.name;
  contactEmail=data.data.contact.email;
  contactPhone=data.data.contact.phone;

  let paymentStatus;
  if (status==0){
    paymentStatus="付款成功";
  }else{
    paymentStatus="付款失敗";
  }
  img= data.data.trip.attraction.image;
  let itineraryText=document.getElementById("itinerary-text");
  let itineraryImg=document.getElementById("itinerary-img");
  let contactWrap=document.getElementById("contact-wrap")
  itineraryImg.src=img;
  main += `
    <p><b>訂單編號：</b>${ordernumber}</p>
    <p class="itinerary-title">台北一日遊：${attractionname}</p>
    <p><b>日期：</b>${date}</p>
    <p><b>時間：</b>${time}</p> 
    <p><b>費用：</b>新台幣${price}元</p>
    <p><b>地點：</b>${address}</p>
  `;
  context +=`
    <p><b>聯絡姓名:</b>${contactName}</p>
    <p><b>連絡信箱:</b>${contactEmail}</p>
    <p><b>手機號碼:</b>${contactPhone}</p>
  `;            
  itineraryText.innerHTML=main;
  paymentResult.innerHTML=paymentStatus;
  contactWrap.innerHTML=context; 
})
.catch(error=>{
  console.error('Error',error);

}) 
} else {
window.location.href='/'
}
}

getPaymentResult()

function deleteToken() {
let token = localStorage.removeItem("token");
// console.log("user signed out");
window.location.reload();
return token;
}

