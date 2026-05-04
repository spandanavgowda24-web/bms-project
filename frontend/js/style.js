const SERVER = "http://127.0.0.1:5000";

document.addEventListener("DOMContentLoaded", function () {

const authWrapper = document.querySelector('.auth-wrapper');
const loginTrigger = document.querySelector('.login-trigger');
const registerTrigger = document.querySelector('.register-trigger');

/* OPEN SIGNUP FIRST */
authWrapper.classList.add("toggled");


/* SWITCH TO SIGNUP */
registerTrigger.addEventListener("click", function(e){
e.preventDefault();
authWrapper.classList.add("toggled");
});


/* SWITCH TO LOGIN */
loginTrigger.addEventListener("click", function(e){
e.preventDefault();
authWrapper.classList.remove("toggled");
});


/* REGISTER */

document.getElementById("registerForm").addEventListener("submit", async function(e){

e.preventDefault();

const username = document.getElementById("regUsername").value;
const email = document.getElementById("regEmail").value;
const password = document.getElementById("regPassword").value;

try{

const response = await fetch(SERVER + "/api/auth/register",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
username:username,
email:email,
password:password
})
});

const data = await response.json();

alert(data.message);

if(response.ok){
authWrapper.classList.remove("toggled");
}

}catch(err){
alert("Server error");
}

});


/* LOGIN */

document.getElementById("loginForm").addEventListener("submit", async function(e){

e.preventDefault();

const username = document.getElementById("loginUsername").value;
const password = document.getElementById("loginPassword").value;

try{

const response = await fetch(SERVER + "/api/auth/login",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
username:username,
password:password
})
});

const data = await response.json();

if(response.ok){

localStorage.setItem("token",data.token);
localStorage.setItem("user_id",data.user_id);
localStorage.setItem("username",data.username);

alert("Login successful");

/* redirect to home feed */
window.location.href="home_feed.html";

}else{

alert(data.message);

}

}catch(err){

alert("Server connection failed");

}

});

});