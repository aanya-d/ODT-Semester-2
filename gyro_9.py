#gyroscope code 9
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
        i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')
        time.sleep_ms(100)
    except:
        pass

def read_sensor():
    try:
        # Read accelerometer (0x3B, 6 bytes) for absolute tilt
        adata = i2c.readfrom_mem(MPU_ADDR, 0x3B, 6)
        ax = struct.unpack('>h', adata[0:2])[0] / 16384.0
        ay = struct.unpack('>h', adata[2:4])[0] / 16384.0
        return ax, ay
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
.btn{display:inline-block;background:#FFE81F;color:#000;font-family:Georgia,serif;font-size:18px;font-weight:900;letter-spacing:6px;text-transform:uppercase;padding:16px 48px;border-radius:2px;text-decoration:none;border:none;cursor:pointer}
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
<style>@keyframes tw{0%,100%{opacity:.2}50%{opacity:1}}</style>
<script>
var s=document.getElementById('stars');
for(var i=0;i<80;i++){
  var d=document.createElement('div');d.className='star';
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
#hud{position:fixed;top:0;left:0;width:100%;padding:8px 16px;display:flex;justify-content:space-between;align-items:center;background:rgba(0,0,0,.7);z-index:10;border-bottom:1px solid #FFE81F33}
#msg{position:fixed;top:48px;left:0;width:100%;text-align:center;font-size:12px;letter-spacing:2px;color:#FFE81F99;z-index:10;padding:4px 0}
#over{position:fixed;inset:0;background:rgba(0,0,0,.92);display:none;flex-direction:column;align-items:center;justify-content:center;z-index:20;text-align:center;gap:20px}
#over h2{font-size:clamp(28px,8vw,56px);letter-spacing:4px}
#over p{font-size:16px;color:#ccc;letter-spacing:2px}
.obtn{background:#FFE81F;color:#000;font-family:Georgia,serif;font-weight:900;letter-spacing:4px;font-size:14px;padding:14px 40px;text-decoration:none;border-radius:2px}
.score-label{font-size:10px;letter-spacing:3px;color:#aaa;text-transform:uppercase}
.score-val{font-size:22px;font-weight:900;letter-spacing:2px}
#timer-val{color:#FFE81F}
#timer-val.warn{color:#ff4400}
</style>
</head>
<body>
<div id="hud">
  <div><div class="score-label">Score</div><div class="score-val" id="sc">0</div></div>
  <div style="text-align:center">
    <div class="score-label">Time</div>
    <div class="score-val" id="timer-val">90</div>
  </div>
  <div style="text-align:center">
    <div class="score-label">Lives</div>
    <div class="score-val" id="lv">&#9679;&#9679;&#9679;</div>
  </div>
  <div style="text-align:right"><div class="score-label">Streak</div><div class="score-val" id="st">0</div></div>
</div>
<div id="msg">Hit the drones Jedi &mdash; Miss 3 and you lose!</div>
<canvas id="cv"></canvas>
<div id="over">
  <h2 id="ot">GAME OVER</h2>
  <p id="op">The Empire has won this day</p>
  <p id="ofin" style="color:#FFE81F;font-size:20px;letter-spacing:3px"></p>
  <a class="obtn" href="/game">Play Again</a>
  <a class="obtn" href="/" style="background:transparent;color:#FFE81F88;border:1px solid #FFE81F44;margin-top:8px">Home</a>
</div>
<script>
var cv=document.getElementById('cv'),ctx=cv.getContext('2d');
var W,H;
function resize(){W=cv.width=window.innerWidth;H=cv.height=window.innerHeight;}
resize();window.addEventListener('resize',resize);

// ---- game state ----
var score=0,lives=3,streak=0,gameOn=true;
var drones=[],stars=[],explosions=[];
var hitCooldown=0;

// ---- pointer: driven by absolute accelerometer tilt ----
// ax, ay are in g (-1..1 typical tilt range)
// We map them directly to screen coordinates
var ax=0, ay=0;       // raw accelerometer values from sensor
var smoothAx=0, smoothAy=0;
var ALPHA=0.12;       // low-pass smoothing (lower = smoother but slightly laggier)
// Tilt range: +/-TILT_MAX g maps to full screen width/height
// 0.5g = ~30 degrees of tilt = full screen. Adjust to taste.
var TILT_MAX=0.55;
var cx=0, cy=0;       // crosshair position in pixels — set after first resize

function tiltToScreen(){
  // ax: tilt left/right. negative ax = tilted right on most MPU orientations.
  // ay: tilt forward/back. positive ay = tilted forward (down).
  // Flip signs here if your physical orientation is different.
  var tx = W/2 + (-ax / TILT_MAX) * (W/2);
  var ty = H/2 + ( ay / TILT_MAX) * (H/2);
  tx = Math.max(20, Math.min(W-20, tx));
  ty = Math.max(20, Math.min(H-20, ty));
  return {x:tx, y:ty};
}

// ---- 90 second countdown ----
var timeLeft=90;
var timerEl=document.getElementById('timer-val');
var timerInterval=setInterval(function(){
  if(!gameOn) return;
  timeLeft--;
  timerEl.textContent=timeLeft;
  if(timeLeft<=15) timerEl.className='warn';
  if(timeLeft<=0){
    clearInterval(timerInterval);
    endGame('time');
  }
},1000);

// ---- starfield ----
for(var i=0;i<150;i++) stars.push({x:Math.random(),y:Math.random(),z:Math.random(),s:Math.random()*1.5+0.3});

// ---- drone factory ----
function mkDrone(){
  var lane=Math.floor(Math.random()*3);
  var tx=lane===0?W*0.2:lane===1?W*0.5:W*0.8;
  var ty=H*0.35+Math.random()*H*0.3;
  var sx=tx+(Math.random()-0.5)*W*0.3;
  drones.push({x:sx,y:-30,tx:tx,ty:ty,spd:0.35+Math.random()*0.5,r:10+Math.random()*6,hit:false,alpha:1});
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

// ---- draw helpers ----
function drawStarfield(){
  for(var i=0;i<stars.length;i++){
    var s=stars[i];
    s.z-=0.003;
    if(s.z<=0) s.z=1;
    var px=(s.x-0.5)/s.z*W+W/2;
    var py=(s.y-0.5)/s.z*H+H/2;
    if(px<0||px>W||py<0||py>H){s.z=0.9+Math.random()*0.1;continue;}
    var sz=s.s*(1-s.z)*2;
    var br=Math.floor((1-s.z)*255);
    ctx.fillStyle='rgb('+br+','+br+','+br+')';
    ctx.beginPath();ctx.arc(px,py,sz,0,Math.PI*2);ctx.fill();
  }
}

function drawDrone(d){
  ctx.save();
  ctx.translate(d.x,d.y);
  ctx.globalAlpha=d.alpha;
  var r=d.r;
  ctx.strokeStyle='#aaa';ctx.lineWidth=Math.max(1,r*0.08);
  ctx.beginPath();ctx.moveTo(-r*0.45,0);ctx.lineTo(-r*1.05,0);ctx.stroke();
  ctx.beginPath();ctx.moveTo(r*0.45,0);ctx.lineTo(r*1.05,0);ctx.stroke();
  // left panel
  ctx.save();ctx.translate(-r*1.5,0);
  ctx.fillStyle='#0a1a2a';ctx.strokeStyle='#4488cc';ctx.lineWidth=Math.max(0.8,r*0.06);
  ctx.beginPath();
  for(var i=0;i<6;i++){var a=i*Math.PI/3;ctx.lineTo(Math.cos(a)*r*0.6,Math.sin(a)*r*0.55);}
  ctx.closePath();ctx.fill();ctx.stroke();
  ctx.strokeStyle='#224466';ctx.lineWidth=Math.max(0.5,r*0.03);
  ctx.beginPath();ctx.moveTo(-r*0.6,0);ctx.lineTo(r*0.6,0);ctx.stroke();
  ctx.beginPath();ctx.moveTo(-r*0.3,-r*0.52);ctx.lineTo(-r*0.3,r*0.52);ctx.moveTo(r*0.3,-r*0.52);ctx.lineTo(r*0.3,r*0.52);ctx.stroke();
  ctx.restore();
  // right panel
  ctx.save();ctx.translate(r*1.5,0);
  ctx.fillStyle='#0a1a2a';ctx.strokeStyle='#4488cc';ctx.lineWidth=Math.max(0.8,r*0.06);
  ctx.beginPath();
  for(var i=0;i<6;i++){var a=i*Math.PI/3;ctx.lineTo(Math.cos(a)*r*0.6,Math.sin(a)*r*0.55);}
  ctx.closePath();ctx.fill();ctx.stroke();
  ctx.strokeStyle='#224466';ctx.lineWidth=Math.max(0.5,r*0.03);
  ctx.beginPath();ctx.moveTo(-r*0.6,0);ctx.lineTo(r*0.6,0);ctx.stroke();
  ctx.beginPath();ctx.moveTo(-r*0.3,-r*0.52);ctx.lineTo(-r*0.3,r*0.52);ctx.moveTo(r*0.3,-r*0.52);ctx.lineTo(r*0.3,r*0.52);ctx.stroke();
  ctx.restore();
  // cockpit
  ctx.fillStyle='#1a2030';ctx.strokeStyle='#6699cc';ctx.lineWidth=Math.max(1,r*0.1);
  ctx.beginPath();ctx.arc(0,0,r*0.45,0,Math.PI*2);ctx.fill();ctx.stroke();
  ctx.strokeStyle='#88bbee';ctx.lineWidth=Math.max(0.5,r*0.05);
  ctx.beginPath();
  for(var i=0;i<6;i++){var a=i*Math.PI/3-Math.PI/6;ctx.lineTo(Math.cos(a)*r*0.26,Math.sin(a)*r*0.26);}
  ctx.closePath();ctx.stroke();
  ctx.fillStyle='#aaddff';ctx.beginPath();ctx.arc(0,0,r*0.1,0,Math.PI*2);ctx.fill();
  ctx.restore();
}

function drawCrosshair(){
  var sz=24;
  ctx.save();
  ctx.strokeStyle='#00FF88';ctx.lineWidth=2;ctx.globalAlpha=0.9;
  ctx.beginPath();ctx.arc(cx,cy,sz,0,Math.PI*2);ctx.stroke();
  ctx.beginPath();ctx.arc(cx,cy,3,0,Math.PI*2);ctx.fillStyle='#00FF88';ctx.fill();
  ctx.beginPath();
  ctx.moveTo(cx-sz-6,cy);ctx.lineTo(cx-sz+6,cy);
  ctx.moveTo(cx+sz-6,cy);ctx.lineTo(cx+sz+6,cy);
  ctx.moveTo(cx,cy-sz-6);ctx.lineTo(cx,cy-sz+6);
  ctx.moveTo(cx,cy+sz-6);ctx.lineTo(cx,cy+sz+6);
  ctx.stroke();
  ctx.strokeStyle='#00FF88';ctx.lineWidth=3;ctx.globalAlpha=0.5;
  ctx.shadowColor='#00FF88';ctx.shadowBlur=8;
  ctx.beginPath();ctx.moveTo(cx,cy+sz+4);ctx.lineTo(cx,cy+sz+36);ctx.stroke();
  ctx.restore();
}

function drawExplosions(){
  for(var i=explosions.length-1;i>=0;i--){
    var e=explosions[i];
    var t=1-e.life/e.max;
    ctx.save();ctx.globalAlpha=e.life/e.max;
    for(var j=0;j<e.pts.length;j++){
      var p=e.pts[j];p.len+=p.spd;
      var ex=e.x+Math.cos(p.a)*p.len*e.life/e.max*4;
      var ey=e.y+Math.sin(p.a)*p.len*e.life/e.max*4;
      ctx.fillStyle=t<0.3?'#ffffff':t<0.6?'#FFE81F':'#ff4400';
      ctx.beginPath();ctx.arc(ex,ey,2.5,0,Math.PI*2);ctx.fill();
    }
    ctx.strokeStyle='#FFE81F';ctx.lineWidth=1;
    ctx.beginPath();ctx.arc(e.x,e.y,(e.max-e.life)*2.5,0,Math.PI*2);ctx.stroke();
    ctx.restore();
    e.life--;
    if(e.life<=0) explosions.splice(i,1);
  }
}

// ---- hit detection ----
function checkHits(){
  if(hitCooldown>0){hitCooldown--;return;}
  for(var i=drones.length-1;i>=0;i--){
    var d=drones[i];
    if(d.hit) continue;
    var dx=d.x-cx,dy=d.y-cy;
    if(Math.sqrt(dx*dx+dy*dy)<d.r+22){
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

// ---- spawn timing ----
var lastSpawn=0,spawnInterval=2200;

// ---- main loop ----
function loop(ts){
  if(!gameOn) return;
  ctx.fillStyle='#000';ctx.fillRect(0,0,W,H);
  drawStarfield();

  // Update crosshair from smoothed accelerometer tilt (absolute position)
  smoothAx += (ax - smoothAx) * ALPHA;
  smoothAy += (ay - smoothAy) * ALPHA;
  var pos = tiltToScreen();
  cx = pos.x;
  cy = pos.y;

  // Spawn drones
  if(ts-lastSpawn>spawnInterval && drones.filter(function(d){return !d.hit;}).length<5){
    mkDrone();lastSpawn=ts;
    spawnInterval=Math.max(900,spawnInterval-25);
  }
  while(drones.filter(function(d){return !d.hit;}).length<2) mkDrone();

  // Update & draw drones
  for(var i=drones.length-1;i>=0;i--){
    var d=drones[i];
    if(d.hit){
      d.alpha-=0.04;
      if(d.alpha<=0){drones.splice(i,1);continue;}
      drawDrone(d);continue;
    }
    var ddx=(d.tx-d.x),ddy=(d.ty-d.y);
    d.x+=ddx*0.004*d.spd;
    d.y+=ddy*0.004*d.spd+0.5*d.spd;
    d.r+=0.03*d.spd;
    if(d.r>55){
      drones.splice(i,1);
      lives--;streak=0;updateHUD();
      if(lives<=0){endGame('lives');}
      continue;
    }
    drawDrone(d);
  }

  checkHits();
  drawExplosions();
  drawCrosshair();
  requestAnimationFrame(loop);
}

function endGame(reason){
  if(!gameOn) return;
  gameOn=false;
  clearInterval(timerInterval);
  var over=document.getElementById('over');
  over.style.display='flex';
  if(reason==='time'){
    document.getElementById('ot').textContent=score>80?'WELL DONE, JEDI':'TIME UP!';
    document.getElementById('op').textContent=score>80?'The Force was strong with you':'The Empire outlasted you';
  } else {
    document.getElementById('ot').textContent='GAME OVER';
    document.getElementById('op').textContent='The Empire has won this day';
  }
  document.getElementById('ofin').textContent='Final Score: '+score;
}

// ---- accelerometer polling ----
// Polls /gyro route (now returns ax,ay from accelerometer, not gyroscope)
function pollSensor(){
  var x=new XMLHttpRequest();
  x.open('GET','/gyro',true);
  x.timeout=300;
  x.onload=function(){
    if(x.status===200){
      try{
        var d=JSON.parse(x.responseText);
        // server sends {gx, gy} but these are now ax, ay (accelerometer)
        ax = parseFloat(d.gx)||0;
        ay = parseFloat(d.gy)||0;
      }catch(e){}
    }
    setTimeout(pollSensor, 50);
  };
  x.onerror=x.ontimeout=function(){setTimeout(pollSensor,100);};
  x.send();
}

// init crosshair to centre
cx=W/2; cy=H/2;
updateHUD();
requestAnimationFrame(loop);
pollSensor();
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
            # Now returns accelerometer X and Y (absolute tilt, not rotation rate)
            # ax: left/right tilt (-1g to +1g), ay: forward/back tilt (-1g to +1g)
            ax_val, ay_val = read_sensor()
            body = '{{"gx":{:.3f},"gy":{:.3f}}}'.format(ax_val, ay_val)
            body_b = body.encode()
            conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: "
                      + str(len(body_b)).encode()
                      + b"\r\nConnection: close\r\n\r\n")
            conn.sendall(body_b)

        elif path == '/game':
            conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: "
                      + str(len(html2)).encode()
                      + b"\r\nConnection: close\r\n\r\n")
            conn.sendall(html2)

        else:
            conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: "
                      + str(len(html1)).encode()
                      + b"\r\nConnection: close\r\n\r\n")
            conn.sendall(html1)

        conn.close()
    except Exception as e:
        print("Error:", e)
        try:
            conn.close()
        except:
            pass
