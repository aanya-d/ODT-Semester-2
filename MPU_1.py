import network
import socket
import machine
import struct
import time

# ---------- MPU-6050 SETUP ----------
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21), freq=400000)
MPU_ADDR = 0x68

def mpu_init():
    try:
        i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')  # Wake up MPU-6050
        time.sleep_ms(100)
    except:
        pass

def read_sensor():
    try:
        gdata = i2c.readfrom_mem(MPU_ADDR, 0x43, 6)
        gx = struct.unpack('>h', gdata[0:2])[0] / 131.0
        gy = struct.unpack('>h', gdata[2:4])[0] / 131.0
        return gx, gy
    except:
        return 0.0, 0.0

mpu_init()

# ---------- ACCESS POINT SETUP ----------
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='StarWars-ODT', password='12345678')
print("Access Point Active")
print("Connect to WiFi: StarWars-ODT")
print("IP Address:", ap.ifconfig()[0])

# ---------- HTML PAGE 1 (HOME) ----------
html1 = b"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>STAR WARS</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#FFE81F;font-family:Georgia,serif;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px;overflow:hidden}
.stars{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none}
.star{position:absolute;background:#fff;border-radius:50%}
.wrap{position:relative;z-index:1;width:100%;max-width:480px;text-align:center}
.ep{font-size:11px;letter-spacing:6px;color:#aaa;margin-bottom:8px;text-transform:uppercase}
h1{font-size:clamp(36px,10vw,72px);font-weight:900;letter-spacing:4px;color:#FFE81F;text-shadow:0 0 30px #FFE81F88;line-height:1;margin-bottom:6px}
.sub{font-size:11px;letter-spacing:8px;color:#aaa;margin-bottom:28px}
.panel{background:rgba(255,232,31,0.05);border:1px solid #FFE81F44;border-radius:4px;padding:18px 20px;margin-bottom:28px;text-align:left}
.panel h2{font-size:11px;letter-spacing:4px;color:#FFE81F;margin-bottom:14px;text-align:center;text-transform:uppercase}
.panel ul{list-style:none;padding:0}
.panel ul li{font-size:13px;color:#ccc;padding:7px 0;border-bottom:1px solid #FFE81F22;line-height:1.5;display:flex;align-items:flex-start;gap:10px}
.panel ul li:last-child{border-bottom:none}
.dot{color:#FFE81F;font-size:16px;line-height:1.4;flex-shrink:0}
.btn{display:inline-block;background:#FFE81F;color:#000;font-family:Georgia,serif;font-size:18px;font-weight:900;letter-spacing:6px;text-transform:uppercase;padding:16px 48px;border-radius:2px;text-decoration:none;border:none;cursor:pointer;transition:background .2s}
.btn:hover{background:#fff}
.divider{width:60px;height:2px;background:#FFE81F44;margin:0 auto 24px}
</style>
</head>
<body>
<div class="stars" id="stars"></div>
<div class="wrap">
  <div class="ep">Episode I &mdash; The Drone Menace</div>
  <h1>STAR WARS</h1>
  <div class="sub">A long time ago in a galaxy far, far away</div>
  <div class="divider"></div>
  <div class="panel">
    <h2>&#9670; How to Play &#9670;</h2>
    <ul>
      <li><span class="dot">&#9670;</span><span>Push the button to change lightsaber colours</span></li>
      <li><span class="dot">&#9670;</span><span>Pick up the lightsaber to turn it on</span></li>
      <li><span class="dot">&#9670;</span><span>Move the saber to blast incoming drones</span></li>
      <li><span class="dot">&#9670;</span><span>Miss three drones and you lose &mdash; may the Force be with you!</span></li>
    </ul>
  </div>
  <a class="btn" href="/game">START</a>
</div>
<style>
@keyframes tw{0%,100%{opacity:.2}50%{opacity:1}}
</style>
<script>
var s=document.getElementById('stars');
for(var i=0;i<80;i++){
  var d=document.createElement('div');
  d.className='star';
  var sz=(Math.random()*2+0.5).toFixed(1);
  d.style.cssText='width:'+sz+'px;height:'+sz+'px;top:'+Math.random()*100+'%;left:'+Math.random()*100+'%;animation:tw '+(Math.random()*3+2).toFixed(1)+'s '+(Math.random()*3).toFixed(1)+'s infinite';
  s.appendChild(d);
}
</script>
</body>
</html>"""

# ---------- HTML PAGE 2 (GAME) ----------
html2 = b"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>STAR WARS &mdash; Drone Battle</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;overflow:hidden;font-family:Georgia,serif;color:#FFE81F;touch-action:none}
#cv{display:block;width:100vw;height:100vh}
#hud{position:fixed;top:0;left:0;width:100%;padding:8px 16px;display:flex;justify-content:space-between;align-items:center;background:rgba(0,0,0,.6);z-index:10;border-bottom:1px solid #FFE81F33}
#msg{position:fixed;top:44px;left:0;width:100%;text-align:center;font-size:12px;letter-spacing:2px;color:#FFE81F99;z-index:10;padding:4px 0}
#over{position:fixed;inset:0;background:rgba(0,0,0,.92);display:none;flex-direction:column;align-items:center;justify-content:center;z-index:20;text-align:center;gap:20px}
#over h2{font-size:clamp(28px,8vw,56px);letter-spacing:4px}
#over p{font-size:16px;color:#ccc;letter-spacing:2px}
#over a{background:#FFE81F;color:#000;font-family:Georgia,serif;font-weight:900;letter-spacing:4px;font-size:14px;padding:14px 40px;text-decoration:none;border-radius:2px}
.score-label{font-size:10px;letter-spacing:3px;color:#aaa;text-transform:uppercase}
.score-val{font-size:22px;font-weight:900;letter-spacing:2px}
</style>
</head>
<body>
<div id="hud">
  <div><div class="score-label">Score</div><div class="score-val" id="sc">0</div></div>
  <div style="text-align:center"><div class="score-label">Lives</div><div class="score-val" id="lv">&#9675;&#9675;&#9675;</div></div>
  <div style="text-align:right"><div class="score-label">Streak</div><div class="score-val" id="st">0</div></div>
</div>
<div id="msg">Hit the drones Jedi &mdash; Miss 3 and you lose!</div>
<canvas id="cv"></canvas>
<div id="over">
  <h2 id="ot">GAME OVER</h2>
  <p id="op">The Empire has won this day</p>
  <p id="ofin"></p>
  <a href="/game">Play Again</a>
  <a href="/" style="background:transparent;color:#FFE81F88;border:1px solid #FFE81F44;margin-top:8px">Home</a>
</div>
<script>
var cv=document.getElementById('cv'),ctx=cv.getContext('2d');
var W,H;
function resize(){W=cv.width=window.innerWidth;H=cv.height=window.innerHeight;}
resize();window.addEventListener('resize',resize);

var score=0,lives=3,streak=0,gameOn=true;
var drones=[],stars=[],explosions=[];
var cx=W/2,cy=H/2;
var gyroX=0,gyroY=0;
var smoothX=0,smoothY=0;
var ALPHA=0.18;   // smoothing — high enough to be responsive, low enough to kill jitter
var DEADZONE=0.3; // ignore readings below 0.3 deg/s (idle hand tremor)
var SPEED=1.4;    // pixels moved per deg/s — tuned for full screen coverage

// Stars background
for(var i=0;i<150;i++) stars.push({x:Math.random(),y:Math.random(),z:Math.random(),s:Math.random()*1.5+0.3});

function mkDrone(){
  // pick one of three horizontal lanes: left, centre, right
  var lane=Math.floor(Math.random()*3);
  var tx=lane===0?W*0.2:lane===1?W*0.5:W*0.8;
  var ty=H*0.35+Math.random()*H*0.3;
  var sx,sy;
  // always spawn from the top (perspective fly-in)
  sx=tx+(Math.random()-0.5)*W*0.3;
  sy=-30;
  drones.push({x:sx,y:sy,tx:tx,ty:ty,spd:0.4+Math.random()*0.6,r:10+Math.random()*6,rot:0,hit:false,alpha:1,age:0});
}

function addExplosion(x,y){
  var pts=[];
  for(var i=0;i<12;i++) pts.push({a:i/12*Math.PI*2,spd:2+Math.random()*4,len:0});
  explosions.push({x:x,y:y,pts:pts,life:40,max:40});
}

function updateHUD(){
  document.getElementById('sc').textContent=score;
  document.getElementById('st').textContent=streak;
  var lstr='';
  for(var i=0;i<3;i++) lstr+=i<lives?'\u25CF':'\u25CB';
  document.getElementById('lv').textContent=lstr;
}

function drawStar(x,y,r){
  ctx.beginPath();
  for(var i=0;i<5;i++){
    var a=i*Math.PI*2/5-Math.PI/2;
    var b=a+Math.PI/5;
    if(i===0) ctx.moveTo(x+r*Math.cos(a),y+r*Math.sin(a));
    else ctx.lineTo(x+r*Math.cos(a),y+r*Math.sin(a));
    ctx.lineTo(x+r*0.45*Math.cos(b),y+r*0.45*Math.sin(b));
  }
  ctx.closePath();
}

function drawDrone(d){
  ctx.save();
  ctx.translate(d.x,d.y);
  ctx.globalAlpha=d.alpha;
  var r=d.r;
  // --- struts connecting cockpit to panels ---
  ctx.strokeStyle='#aaa';ctx.lineWidth=Math.max(1,r*0.08);
  ctx.beginPath();ctx.moveTo(-r*0.45,0);ctx.lineTo(-r*1.05,0);ctx.stroke();
  ctx.beginPath();ctx.moveTo(r*0.45,0);ctx.lineTo(r*1.05,0);ctx.stroke();
  // --- left hexagonal solar panel ---
  ctx.save();ctx.translate(-r*1.5,0);
  ctx.fillStyle='#0a1a2a';ctx.strokeStyle='#4488cc';ctx.lineWidth=Math.max(0.8,r*0.06);
  ctx.beginPath();
  for(var i=0;i<6;i++){var a=i*Math.PI/3;ctx.lineTo(Math.cos(a)*r*0.6,Math.sin(a)*r*0.55);}
  ctx.closePath();ctx.fill();ctx.stroke();
  // panel grid lines
  ctx.strokeStyle='#224466';ctx.lineWidth=Math.max(0.5,r*0.03);
  ctx.beginPath();ctx.moveTo(-r*0.6,0);ctx.lineTo(r*0.6,0);ctx.stroke();
  ctx.beginPath();ctx.moveTo(-r*0.3,-r*0.52);ctx.lineTo(-r*0.3,r*0.52);
  ctx.moveTo(r*0.3,-r*0.52);ctx.lineTo(r*0.3,r*0.52);ctx.stroke();
  ctx.restore();
  // --- right hexagonal solar panel ---
  ctx.save();ctx.translate(r*1.5,0);
  ctx.fillStyle='#0a1a2a';ctx.strokeStyle='#4488cc';ctx.lineWidth=Math.max(0.8,r*0.06);
  ctx.beginPath();
  for(var i=0;i<6;i++){var a=i*Math.PI/3;ctx.lineTo(Math.cos(a)*r*0.6,Math.sin(a)*r*0.55);}
  ctx.closePath();ctx.fill();ctx.stroke();
  ctx.strokeStyle='#224466';ctx.lineWidth=Math.max(0.5,r*0.03);
  ctx.beginPath();ctx.moveTo(-r*0.6,0);ctx.lineTo(r*0.6,0);ctx.stroke();
  ctx.beginPath();ctx.moveTo(-r*0.3,-r*0.52);ctx.lineTo(-r*0.3,r*0.52);
  ctx.moveTo(r*0.3,-r*0.52);ctx.lineTo(r*0.3,r*0.52);ctx.stroke();
  ctx.restore();
  // --- central ball cockpit ---
  ctx.fillStyle='#1a2030';ctx.strokeStyle='#6699cc';ctx.lineWidth=Math.max(1,r*0.1);
  ctx.beginPath();ctx.arc(0,0,r*0.45,0,Math.PI*2);ctx.fill();ctx.stroke();
  // cockpit viewport (hex outline)
  ctx.strokeStyle='#88bbee';ctx.lineWidth=Math.max(0.5,r*0.05);
  ctx.beginPath();
  for(var i=0;i<6;i++){var a=i*Math.PI/3-Math.PI/6;ctx.lineTo(Math.cos(a)*r*0.26,Math.sin(a)*r*0.26);}
  ctx.closePath();ctx.stroke();
  // cockpit inner glow dot
  ctx.fillStyle='#aaddff';
  ctx.beginPath();ctx.arc(0,0,r*0.1,0,Math.PI*2);ctx.fill();
  ctx.globalAlpha=1;
  ctx.restore();
}

function drawCrosshair(){
  var sz=24;
  ctx.save();
  ctx.strokeStyle='#00FF88';
  ctx.lineWidth=2;
  ctx.globalAlpha=0.9;
  // outer circle
  ctx.beginPath();ctx.arc(cx,cy,sz,0,Math.PI*2);ctx.stroke();
  // inner dot
  ctx.beginPath();ctx.arc(cx,cy,3,0,Math.PI*2);ctx.fillStyle='#00FF88';ctx.fill();
  // tick lines
  ctx.beginPath();
  ctx.moveTo(cx-sz-6,cy);ctx.lineTo(cx-sz+6,cy);
  ctx.moveTo(cx+sz-6,cy);ctx.lineTo(cx+sz+6,cy);
  ctx.moveTo(cx,cy-sz-6);ctx.lineTo(cx,cy-sz+6);
  ctx.moveTo(cx,cy+sz-6);ctx.lineTo(cx,cy+sz+6);
  ctx.stroke();
  // lightsaber beam
  ctx.strokeStyle='#00FF88';ctx.lineWidth=3;ctx.globalAlpha=0.5;
  ctx.shadowColor='#00FF88';ctx.shadowBlur=8;
  ctx.beginPath();ctx.moveTo(cx,cy+sz+4);ctx.lineTo(cx,cy+sz+40);ctx.stroke();
  ctx.restore();
}

function drawExplosions(){
  for(var i=explosions.length-1;i>=0;i--){
    var e=explosions[i];
    var t=1-e.life/e.max;
    ctx.save();
    ctx.globalAlpha=e.life/e.max;
    for(var j=0;j<e.pts.length;j++){
      var p=e.pts[j];
      p.len+=p.spd;
      var ex=e.x+Math.cos(p.a)*p.len*e.life/e.max*4;
      var ey=e.y+Math.sin(p.a)*p.len*e.life/e.max*4;
      ctx.fillStyle=t<0.3?'#ffffff':t<0.6?'#FFE81F':'#ff4400';
      ctx.beginPath();ctx.arc(ex,ey,2.5,0,Math.PI*2);ctx.fill();
    }
    // ring
    ctx.strokeStyle='#FFE81F';ctx.lineWidth=1;
    ctx.beginPath();ctx.arc(e.x,e.y,(e.max-e.life)*2.5,0,Math.PI*2);ctx.stroke();
    ctx.restore();
    e.life--;
    if(e.life<=0) explosions.splice(i,1);
  }
}

function drawStarfield(){
  for(var i=0;i<stars.length;i++){
    var s=stars[i];
    s.z-=0.003;
    if(s.z<=0) s.z=1;
    var px=(s.x-0.5)/(s.z)*W+W/2;
    var py=(s.y-0.5)/(s.z)*H+H/2;
    if(px<0||px>W||py<0||py>H){s.z=0.9+Math.random()*0.1;continue;}
    var sz=s.s*(1-s.z)*2;
    var br=Math.floor((1-s.z)*255);
    ctx.fillStyle='rgb('+br+','+br+','+br+')';
    ctx.beginPath();ctx.arc(px,py,sz,0,Math.PI*2);ctx.fill();
  }
}

var lastSpawn=0,spawnInterval=2200;
var hitCooldown=0;

function checkHits(){
  if(hitCooldown>0){hitCooldown--;return;}
  for(var i=drones.length-1;i>=0;i--){
    var d=drones[i];
    if(d.hit) continue;
    var dx=d.x-cx,dy=d.y-cy;
    if(Math.sqrt(dx*dx+dy*dy)<d.r+20){
      d.hit=true;
      addExplosion(d.x,d.y);
      score+=10;streak++;
      if(streak>=3) score+=streak*2;
      updateHUD();
      hitCooldown=8;
      break;
    }
  }
}

function loop(ts){
  if(!gameOn) return;
  ctx.fillStyle='#000';ctx.fillRect(0,0,W,H);
  drawStarfield();

  // --- Pointer movement ---
  // gyroX from sensor = rotation around X axis = physical tilt UP/DOWN  -> moves pointer Y
  // gyroY from sensor = rotation around Y axis = physical tilt LEFT/RIGHT -> moves pointer X
  // Both negated so direction matches: tilt right = pointer goes right, tilt up = pointer goes up
  var rawX = Math.abs(gyroY) > DEADZONE ? -gyroY : 0;
  var rawY = Math.abs(gyroX) > DEADZONE ? -gyroX : 0;
  smoothX += (rawX - smoothX) * ALPHA;
  smoothY += (rawY - smoothY) * ALPHA;
  cx += smoothX * SPEED;
  cy += smoothY * SPEED;
  cx = Math.max(20, Math.min(W-20, cx));
  cy = Math.max(20, Math.min(H-20, cy));

  // spawn drones: min 2 max 5
  if(ts-lastSpawn>spawnInterval && drones.filter(function(d){return !d.hit;}).length<5){
    mkDrone();lastSpawn=ts;
    spawnInterval=Math.max(900,spawnInterval-30);
  }
  while(drones.filter(function(d){return !d.hit;}).length<2) mkDrone();

  // update & draw drones
  for(var i=drones.length-1;i>=0;i--){
    var d=drones[i];
    d.rot+=0.015;d.age++;
    if(d.hit){
      d.alpha-=0.04;
      if(d.alpha<=0){drones.splice(i,1);continue;}
      drawDrone(d);continue;
    }
    // perspective approach toward own lane target
    var dx=(d.tx-d.x),dy=(d.ty-d.y);
    d.x+=dx*0.004*d.spd;
    d.y+=dy*0.004*d.spd+0.5*d.spd;
    d.r+=0.03*d.spd;
    if(d.r>55){
      drones.splice(i,1);
      lives--;updateHUD();
      if(lives<=0){endGame();}
      continue;
    }
    drawDrone(d);
  }

  checkHits();
  drawExplosions();
  drawCrosshair();
  requestAnimationFrame(loop);
}

function endGame(){
  gameOn=false;
  document.getElementById('over').style.display='flex';
  document.getElementById('ot').textContent=score>80?'WELL DONE, JEDI':'GAME OVER';
  document.getElementById('op').textContent=score>80?'The Force was strong with you':'The Empire has won this day';
  document.getElementById('ofin').textContent='Final Score: '+score;
}

// ---------- GYRO POLLING ----------
function pollGyro(){
  var x=new XMLHttpRequest();
  x.open('GET','/gyro',true);
  x.timeout=300;
  x.onload=function(){
    if(x.status===200){
      try{
        var d=JSON.parse(x.responseText);
        gyroX=parseFloat(d.gx)||0;
        gyroY=parseFloat(d.gy)||0;
      }catch(e){}
    }
    setTimeout(pollGyro,40);
  };
  x.onerror=x.ontimeout=function(){setTimeout(pollGyro,100);};
  x.send();
}

updateHUD();
requestAnimationFrame(loop);
pollGyro();
</script>
</body>
</html>"""

# ---------- SOCKET SERVER ----------
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(5)
print("Web server running on port 80...")

while True:
    try:
        conn, addr = server.accept()
        request = conn.recv(1024).decode('utf-8', 'ignore')
        path = '/'
        try:
            path = request.split(' ')[1]
        except:
            pass

        if path == '/gyro':
            gx, gy = read_sensor()
            body = '{{"gx":{:.2f},"gy":{:.2f}}}'.format(gx, gy)
            body_b = body.encode()
            conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: " + str(len(body_b)).encode() + b"\r\nConnection: close\r\n\r\n")
            conn.sendall(body_b)

        elif path == '/game':
            conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: " + str(len(html2)).encode() + b"\r\nConnection: close\r\n\r\n")
            conn.sendall(html2)

        else:
            conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: " + str(len(html1)).encode() + b"\r\nConnection: close\r\n\r\n")
            conn.sendall(html1)

        conn.close()
    except Exception as e:
        print("Error:", e)
        try:
            conn.close()
        except:
            pass
