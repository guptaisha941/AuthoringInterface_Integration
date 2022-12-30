
function get()
{
    tim=setTimeout(get1,3);
}
function get1()
{
    var x = document.getElementById('tt').value;
    var n=document.getElementById("os");
    n.innerHTML='';
    var res =[];
    var s='';
    for(i=0;i<x.length;i++)
    {
        s=s+x[i];
        if(x[i]=='।' || x[i]=='?' || x[i]=='.')
        {
            res.push(s);
            s='';
        }
    }
    console.log(res);
    for(var i=0;i<res.length;i++)
    {
        var m=res[i]+'\n';
        const para = document.createElement("p");
        para.className='osc';
        para.id='p'+i;
        const node = document.createTextNode(m);
        para.appendChild(node);

        const element = document.getElementById("os");
        element.appendChild(para);
        //document.getElementById('os').value+=m;
    }
    const buttons = document.getElementsByTagName("p");
    const buttonPressed = e => {
        //console.log(e.target.id);  // Get ID of Clicked Element
        /*var i=e.target.id;
        var sentence=document.getElementById(i).innerHTML;
        console.log(sentence);
        var m=document.getElementById('hi');
        m.innerHTML=sentence;
        const api_url='https://127.0.0.1:5000/'+sentence;
        getapi(api_url);*/
        getapi();
        
    }
    for (let t of buttons) {
        t.addEventListener("click", buttonPressed);
    }
}
    async function getapi() {
        
        /*const response = await fetch(url,{
            method: 'GET',
            headers: {
              Accept: 'application/json',
    }});*/
    const request = new Request('usr.json');

  const response = await fetch(request);
  const find = await response.json();
  var y=Object.keys(find);
  var z=Object.values(find);
  
  var m=document.getElementById('hi');
    let no=find.Concept.length;
    

    const tbl = document.createElement("table");
    tbl.className='table';
    tbl.id='table';
    const tbBody = document.createElement("tbody");
    
    var j=0;
    for (let i = 0; i < 9; i++) 
    {
        const row = document.createElement("tr");
        var div = document.createElement("div");
        div.className='headerdiv';
        const h = document.createElement("th");
        const cellText = document.createTextNode(y[i]);
        console.log(cellText);
        h.appendChild(cellText);
        div.appendChild(h);
        row.appendChild(div);

        for(let k = 0; k < no; k++)
        {
            var div = document.createElement("div");
            div.className='headerdiv2';
            const cell = document.createElement("td");
            const cellText = document.createTextNode(z[j][k]);
            console.log(cellText);
            cell.appendChild(cellText);
            div.appendChild(cell);
            row.appendChild(div);
            if(i==8)
            {
                 cell.setAttribute("colspan","4");
                 break;
            }
        }
        j++;
        tbl.appendChild(row);
    }
    //tbl.setAttribute("border",'1');
  document.getElementById('usr').appendChild(tbl);

}
