let userId = null;

function register(){
    fetch("/register", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            username: document.getElementById("username").value,
            password: document.getElementById("password").value
        })
    }).then(r=>r.json()).then(d=>console.log(d));
}

function login(){
    fetch("/login", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            username: document.getElementById("username").value,
            password: document.getElementById("password").value
        })
    }).then(r=>r.json()).then(d=>{
        if(d.user_id){ userId=d.user_id; document.getElementById("login").style.display="none"; document.getElementById("chat").style.display="block"; loadDM(); }
    });
}

function sendDM(){
    const to = document.getElementById("dm_user").value;
    const msg = document.getElementById("dm_msg").value;
    fetch("/dm/send", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({from:userId,to:to,msg:msg})})
    .then(r=>r.json()).then(loadDM);
}

function loadDM(){
    const to = document.getElementById("dm_user").value;
    fetch(`/dm/history?a=${userId}&b=${to}`).then(r=>r.json()).then(d=>{
        const div = document.getElementById("dm_messages");
        div.innerHTML="";
        d.forEach(m=>div.innerHTML+=`<p>${m.sender_id}: ${m.message}</p>`);
    });
}

function sendGroup(){
    const gid = document.getElementById("group_id").value;
    const msg = document.getElementById("group_msg").value;
    fetch("/group/send", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({from:userId,group:gid,msg:msg})})
    .then(r=>r.json()).then(()=>loadGroup());
}

function loadGroup(){
    const gid = document.getElementById("group_id").value;
    fetch(`/group/history?group=${gid}`).then(r=>r.json()).then(d=>{
        const div = document.getElementById("group_messages");
        div.innerHTML="";
        d.forEach(m=>div.innerHTML+=`<p>${m.sender_id}: ${m.message}</p>`);
    });
}

// Автообновление каждые 2 сек
setInterval(()=>{ if(userId) { loadDM(); loadGroup(); } }, 2000);
