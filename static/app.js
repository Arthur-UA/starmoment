const form=document.querySelector('#moment-form'),dateInput=document.querySelector('#date'),description=document.querySelector('#description'),count=document.querySelector('#count'),submit=document.querySelector('#submit');
const views={empty:document.querySelector('#empty'),loading:document.querySelector('#loading'),story:document.querySelector('#story'),error:document.querySelector('#error')};
dateInput.min='1995-06-16';dateInput.max=new Date().toISOString().split('T')[0];
description.addEventListener('input',()=>count.textContent=`${description.value.length} / 500`);
document.querySelector('#retry').addEventListener('click',()=>{show('empty');form.scrollIntoView({behavior:'smooth'})});
function show(name){Object.entries(views).forEach(([key,node])=>node.classList.toggle('hidden',key!==name))}
function fail(message){document.querySelector('#error-message').textContent=message;show('error')}
form.addEventListener('submit',async event=>{
  event.preventDefault();submit.disabled=true;show('loading');
  const output=document.querySelector('#output');output.textContent='';document.querySelector('#cursor').classList.remove('hidden');
  try{
    const response=await fetch('/api/moment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({date:dateInput.value,description:description.value})});
    if(!response.ok){const body=await response.json();throw new Error(body.detail||'Something went wrong. Please try again.')}
    const reader=response.body.getReader(),decoder=new TextDecoder();let buffer='';
    while(true){const {value,done}=await reader.read();buffer+=decoder.decode(value||new Uint8Array(),{stream:!done});const lines=buffer.split('\n');buffer=lines.pop();
      for(const line of lines){if(!line)continue;const item=JSON.parse(line);
        if(item.type==='metadata'){
          const photo=document.querySelector('#photo');photo.classList.remove('loaded');photo.src=item.image_url;photo.onload=()=>photo.classList.add('loaded');
          const chosen=new Date(`${item.date}T12:00:00`);document.querySelector('#story-date').textContent=chosen.toLocaleDateString(undefined,{month:'long',day:'numeric',year:'numeric'});
          document.querySelector('#nasa-link').href=item.page_url;show('story');
        } else if(item.type==='delta')output.textContent+=item.text;
        else if(item.type==='done')document.querySelector('#cursor').classList.add('hidden');
        else if(item.type==='error')throw new Error(item.message);
      }
      if(done)break;
    }
  }catch(error){fail(error.message)}finally{submit.disabled=false}
});
