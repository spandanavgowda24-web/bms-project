const API="http://127.0.0.1:5000"


/* SPEAK */

function speak(text){

let speed=document.getElementById("speed").value
let voiceType=document.getElementById("voice").value

const speech=new SpeechSynthesisUtterance(text)

speech.rate=parseFloat(speed)

const voices=speechSynthesis.getVoices()

if(voiceType==="male"){
speech.voice=voices.find(v=>v.name.toLowerCase().includes("male")) || voices[0]
}else{
speech.voice=voices.find(v=>v.name.toLowerCase().includes("female")) || voices[1]
}

speechSynthesis.speak(speech)

}



/* LISTEN */

function listen(callback){

const recognition=new(window.SpeechRecognition || window.webkitSpeechRecognition)()

recognition.lang="en-US"

recognition.start()

recognition.onresult=function(event){

const text=event.results[0][0].transcript.toLowerCase()

callback(text)

}

}



/* UPLOAD */

function uploadFile(){

const token=localStorage.getItem("token")

let file=document.getElementById("file").files[0]

let link=document.getElementById("link").value

if(!file && link===""){

alert("Upload file or paste link")

return

}



if(file){

const formData=new FormData()

formData.append("file",file)

fetch(API+"/api/upload",{

method:"POST",

headers:{
"Authorization":"Bearer "+token
},

body:formData

})

.then(res=>res.json())

.then(data=>{

if(!data.filename){
alert("Upload failed")
return
}

analyzeFile(data.filename)

})

}

else{

fetch(API+"/api/analyze_link",{

method:"POST",

headers:{
"Content-Type":"application/json",
"Authorization":"Bearer "+token
},

body:JSON.stringify({link:link})

})

.then(res=>res.json())

.then(data=>{

startInteraction(data)

})

}

}



/* ANALYZE */

function analyzeFile(filename){

const token=localStorage.getItem("token")

fetch(API+"/api/analyze/"+filename,{

headers:{
"Authorization":"Bearer "+token
}

})

.then(res=>res.json())

.then(data=>{

document.getElementById("result").innerText=JSON.stringify(data,null,2)

startInteraction(data)

})

}



/* START INTERACTION */

function startInteraction(data){

if(data.type==="steps"){

speak("I detected instructions. Shall I start guiding you? Say yes to begin.")

listen(function(answer){

if(answer.includes("yes")){

runSteps(data.content)

}

else{

speak("Okay stopping guidance")

}

})

}

else{

speak("Here is the summary")

speak(data.content)

}

}



/* STEP GUIDE */

function runSteps(steps){

let index=0

function nextStep(){

if(index>=steps.length){

speak("All steps completed")

return

}

speak("Step "+(index+1)+". "+steps[index])

speak("Say next repeat or stop")

listen(function(cmd){

if(cmd.includes("next")){

index++

nextStep()

}

else if(cmd.includes("repeat")){

nextStep()

}

else if(cmd.includes("stop")){

speak("Guidance stopped")

}

})

}

nextStep()

}



/* START VOICE */

function startVoice(){

speak("Hello. How can I help you?")

listen(function(text){

speak("You said "+text)

})

}