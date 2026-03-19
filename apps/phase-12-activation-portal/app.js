
const data = window.PHASE12_CONTENT;

let state = JSON.parse(localStorage.getItem("p12")) || {
completed:0,
missions:[],
reflections:{}
};

const lesson = data.lessons[0];

document.getElementById("title").innerText = lesson.title;
document.getElementById("hook").innerText = lesson.hook;
document.getElementById("reality").innerText = lesson.reality;

const actionsDiv = document.getElementById("actions");
lesson.actions.forEach(a=>{
const div=document.createElement("div");
div.innerText="• "+a;
actionsDiv.appendChild(div);
});

document.getElementById("completeAction").onclick=()=>{
state.completed++;
state.missions.push(lesson.title);
save();
render();
};

document.getElementById("saveReflection").onclick=()=>{
state.reflections[lesson.title]=document.getElementById("reflectionInput").value;
save();
};

function render(){
document.getElementById("progress").innerText="Completed: "+state.completed;
const ul=document.getElementById("missions");
ul.innerHTML="";
state.missions.forEach(m=>{
const li=document.createElement("li");
li.innerText=m;
ul.appendChild(li);
});
}

function save(){
localStorage.setItem("p12",JSON.stringify(state));
}

render();
