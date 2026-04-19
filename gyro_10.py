#gyro 10

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
        # Set accelerometer range to ±2g (register 0x1C, value 0x00)
        i2c.writeto_mem(MPU_ADDR, 0x1C, b'\x00')
        # Set gyro range to ±250 deg/s (register 0x1B, value 0x00)
        i2c.writeto_mem(MPU_ADDR, 0x1B, b'\x00')
    except:
        pass

def read_sensor():
    try:
        # Read accel (6 bytes at 0x3B) + gyro (6 bytes at 0x43)
        adata = i2c.readfrom_mem(MPU_ADDR, 0x3B, 6)
        gdata = i2c.readfrom_mem(MPU_ADDR, 0x43, 6)

        # Accel: raw / 16384.0 => g  (for ±2g range)
        ax = struct.unpack('>h', adata[0:2])[0] / 16384.0
        ay = struct.unpack('>h', adata[2:4])[0] / 16384.0
        az = struct.unpack('>h', adata[4:6])[0] / 16384.0

        # Gyro: raw / 131.0 => deg/s  (for ±250 deg/s range)
        gx = struct.unpack('>h', gdata[0:2])[0] / 131.0
        gy = struct.unpack('>h', gdata[2:4])[0] / 131.0

        return gx, gy, ax, ay, az
    except:
        return 0.0, 0.0, 0.0, 0.0, 1.0

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

/* ── Debug overlay ── */
#dbg{
  position:fixed;bottom:10px;left:10px;
  background:rgba(0,0,0,.72);
  border:1px solid #FFE81F44;
  border-radius:3px;
  padding:7px 11px;
  font-size:11px;
  line-height:1.7;
  letter-spacing:1px;
  color:#00FF88;
  z-index:30;
  font-family:monospace;
  pointer-events:none;
}

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

<!-- Live sensor debug readout -->
<div id="dbg">
  GX: <span id="d-gx">0.00</span> &deg;/s &nbsp;|&nbsp; GY: <span id="d-gy">0.00</span> &deg;/s<br>
  AX: <span id="d-ax">0.00</span> g &nbsp;&nbsp;|&nbsp; AY: <span id="d-ay">0.00</span> g &nbsp;&nbsp;|&nbsp; AZ: <span id="d-az">0.00</span> g<br>
  Pitch: <span id="d-pt">0.0</span> &deg; &nbsp;|&nbsp; Roll: <span id="d-rl">0.0</span> &deg;<br>
  Pointer: <span id="d-cx">0</span>, <span id="d-cy">0</span>
</div>

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

// ─────────────────────────────────────────────
//  ABSOLUTE POINTER via COMPLEMENTARY FILTER
//  (PS Move style — tilt angle drives position)
// ─────────────────────────────────────────────
//
//  The gyroscope gives ANGULAR VELOCITY (deg/s).
//  Adding velocity to position every frame = drift.
//
//  Fix: maintain a TILT ANGLE for each axis using
//  a complementary filter that blends:
//    • Gyro integration  (fast, smooth, drifts over time)
//    • Accelerometer tilt (slow, absolute, noisy)
//  Result: stable absolute angle → mapped to screen XY.
//
//  angle = CF_ALPHA*(angle + gyro*dt) + (1-CF_ALPHA)*accel_angle
//
var pitchAngle = 0;   // tilt up/down  → screen Y
var rollAngle  = 0;   // tilt left/right → screen X

// Tuning knobs
var CF_ALPHA   = 0.96;  // complementary filter weight for gyro leg
                        // 0.96 = 96% gyro short-term, 4% accel long-term correction

var DEADZONE   = 1.8;   // deg/s — gyro readings below this are treated as zero
                        // raised so a resting hand doesn't drift the pointer

// Tilt range that maps to full screen width/height.
// ±TILT_RANGE degrees of physical tilt = pointer travels edge to edge.
var TILT_RANGE = 30;    // degrees — reduce for more sensitive, increase for less

var lastTime   = null;

// Live sensor values (updated by pollGyro)
var gyroX=0,gyroY=0,accelX=0,accelY=0,accelZ=1;

// Pointer starts dead-centre
var cx=null,cy=null;  // null until first sensor read so we can centre properly

// Stars background
for(var i=0;i<150;i++) stars.push({x:Math.random(),y:Math.random(),z:Math.random(),s:Math.random()*1.5+0.3});

function mkDrone(){
  var lane=Math.floor(Math.random()*3);
  var tx=lane===0?W*0.2:lane===1?W*0.5:W*0.8;
  var ty=H*0.35+Math.random()*H*0.3;
  var sx=tx+(Math.random()-0.5)*W*0.3;
  var sy=-30;
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

function updateDebug(){
  document.getElementById('d-gx').textContent=gyroX.toFixed(2);
  document.getElementById('d-gy').textContent=gyroY.toFixed(2);
  document.getElementById('d-ax').textContent=accelX.toFixed(3);
  document.getElementById('d-ay').textContent=accelY.toFixed(3);
  document.getElementById('d-az').textContent=accelZ.toFixed(3);
  document.getElementById('d-pt').textContent=pitchAngle.toFixed(1);
  document.getElementById('d-rl').textContent=rollAngle.toFixed(1);
  document.getElementById('d-cx').textContent=Math.round(cx);
  document.getElementById('d-cy').textContent=Math.round(cy);
}

function drawDrone(d){
  ctx.save();
  ctx.translate(d.x,d.y);
  ctx.globalAlpha=d.alpha;
  var r=d.r;
  ctx.strokeStyle='#aaa';ctx.lineWidth=Math.max(1,r*0.08);
  ctx.beginPath();ctx.moveTo(-r*0.45,0);ctx.lineTo(-r*1.05,0);ctx.stroke();
  ctx.beginPath();ctx.moveTo(r*0.45,0);ctx.lineTo(r*1.05,0);ctx.stroke();
  ctx.save();ctx.translate(-r*1.5,0);
  ctx.fillStyle='#0a1a2a';ctx.strokeStyle='#4488cc';ctx.lineWidth=Math.max(0.8,r*0.06);
  ctx.beginPath();
  for(var i=0;i<6;i++){var a=i*Math.PI/3;ctx.lineTo(Math.cos(a)*r*0.6,Math.sin(a)*r*0.55);}
  ctx.closePath();ctx.fill();ctx.stroke();
  ctx.strokeStyle='#224466';ctx.lineWidth=Math.max(0.5,r*0.03);
  ctx.beginPath();ctx.moveTo(-r*0.6,0);ctx.lineTo(r*0.6,0);ctx.stroke();
  ctx.beginPath();ctx.moveTo(-r*0.3,-r*0.52);ctx.lineTo(-r*0.3,r*0.52);
  ctx.moveTo(r*0.3,-r*0.52);ctx.lineTo(r*0.3,r*0.52);ctx.stroke();
  ctx.restore();
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
  ctx.fillStyle='#1a2030';ctx.strokeStyle='#6699cc';ctx.lineWidth=Math.max(1,r*0.1);
  ctx.beginPath();ctx.arc(0,0,r*0.45,0,Math.PI*2);ctx.fill();ctx.stroke();
  ctx.strokeStyle='#88bbee';ctx.lineWidth=Math.max(0.5,r*0.05);
  ctx.beginPath();
  for(var i=0;i<6;i++){var a=i*Math.PI/3-Math.PI/6;ctx.lineTo(Math.cos(a)*r*0.26,Math.sin(a)*r*0.26);}
  ctx.closePath();ctx.stroke();
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

// ─────────────────────────────────────────────
//  COMPLEMENTARY FILTER — called every frame
//  dt   = seconds since last frame
//  The filter keeps absolute tilt angles that
//  don't drift but also don't jitter.
// ─────────────────────────────────────────────
function updateAngles(dt){
  // ── Gyroscope leg: integrate angular velocity ──
  // Apply deadzone first — zero out tiny noise
  var gxFiltered = Math.abs(gyroX) > DEADZONE ? gyroX : 0;
  var gyFiltered = Math.abs(gyroY) > DEADZONE ? gyroY : 0;

  // ── Accelerometer leg: compute tilt angles ──
  // pitch = forward/backward tilt  (rotation around X) → moves pointer Y
  // roll  = left/right tilt        (rotation around Y) → moves pointer X
  //
  // atan2 gives absolute angle from gravity vector.
  // clamp accelZ away from zero to avoid atan2 singularity at 90°.
  var az_safe = accelZ !== 0 ? accelZ : 0.001;
  var accelPitch = Math.atan2(accelY, az_safe) * (180 / Math.PI);   // deg
  var accelRoll  = Math.atan2(-accelX, az_safe) * (180 / Math.PI);  // deg

  // ── Blend them ──
  pitchAngle = CF_ALPHA * (pitchAngle + gxFiltered * dt) + (1 - CF_ALPHA) * accelPitch;
  rollAngle  = CF_ALPHA * (rollAngle  + gyFiltered * dt) + (1 - CF_ALPHA) * accelRoll;
}

// Map tilt angle (±TILT_RANGE) → screen pixel coordinate
function angleToScreen(angle, screenSize){
  // clamp to tilt range
  var clamped = Math.max(-TILT_RANGE, Math.min(TILT_RANGE, angle));
  // normalise to 0..1
  var norm = (clamped + TILT_RANGE) / (2 * TILT_RANGE);
  return norm * screenSize;
}

function loop(ts){
  if(!gameOn) return;

  // ── dt in seconds (cap at 100 ms to avoid startup jump) ──
  var dt = 0;
  if(lastTime !== null){
    dt = Math.min((ts - lastTime) / 1000, 0.1);
  }
  lastTime = ts;

  // ── Update complementary filter ──
  updateAngles(dt);

  // ── Map angles to screen — absolute, no drift ──
  // On first frame, initialise cx/cy from current tilt so pointer
  // snaps to where the controller actually is instead of top-left.
  if(cx === null){ cx = W/2; cy = H/2; }

  cx = angleToScreen(rollAngle,  W);
  cy = angleToScreen(pitchAngle, H);

  ctx.fillStyle='#000';ctx.fillRect(0,0,W,H);
  drawStarfield();

  if(ts-lastSpawn>spawnInterval && drones.filter(function(d){return !d.hit;}).length<5){
    mkDrone();lastSpawn=ts;
    spawnInterval=Math.max(900,spawnInterval-30);
  }
  while(drones.filter(function(d){return !d.hit;}).length<2) mkDrone();

  for(var i=drones.length-1;i>=0;i--){
    var d=drones[i];
    d.rot+=0.015;d.age++;
    if(d.hit){
      d.alpha-=0.04;
      if(d.alpha<=0){drones.splice(i,1);continue;}
      drawDrone(d);continue;
    }
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
  updateDebug();
  requestAnimationFrame(loop);
}

function endGame(){
  gameOn=false;
  document.getElementById('over').style.display='flex';
  document.getElementById('ot').textContent=score>80?'WELL DONE, JEDI':'GAME OVER';
  document.getElementById('op').textContent=score>80?'The Force was strong with you':'The Empire has won this day';
  document.getElementById('ofin').textContent='Final Score: '+score;
}

// ─────────────────────────────────────────────
//  GYRO POLLING — fetches gx, gy, ax, ay, az
//  Returns all 5 values so the CF can use both
// ─────────────────────────────────────────────
function pollGyro(){
  var x=new XMLHttpRequest();
  x.open('GET','/gyro',true);
  x.timeout=300;
  x.onload=function(){
    if(x.status===200){
      try{
        var d=JSON.parse(x.responseText);
        gyroX  = parseFloat(d.gx) || 0;
        gyroY  = parseFloat(d.gy) || 0;
        accelX = parseFloat(d.ax) || 0;
        accelY = parseFloat(d.ay) || 0;
        accelZ = parseFloat(d.az) || 1;
      }catch(e){}
    }
    setTimeout(pollGyro, 40);   // ~25 Hz — fast enough, not hammering the ESP32
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
            gx, gy, ax, ay, az = read_sensor()
            # Print to serial so you can watch raw values live
            print("GX:{:.2f} GY:{:.2f}  AX:{:.3f} AY:{:.3f} AZ:{:.3f}".format(gx, gy, ax, ay, az))
            body = '{{"gx":{:.2f},"gy":{:.2f},"ax":{:.3f},"ay":{:.3f},"az":{:.3f}}}'.format(gx, gy, ax, ay, az)
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
