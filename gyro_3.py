#gyroscope remote gemini 3
import network
import socket
import machine
import struct
import time
import gc

# ---------- MPU-6050 SETUP ----------
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21), freq=400000)
MPU_ADDR = 0x68

def mpu_init():
    try:
        i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')
        time.sleep_ms(100)
    except:
        print("MPU Init Failed")

def read_gyro():
    try:
        data = i2c.readfrom_mem(MPU_ADDR, 0x43, 6)
        gx = struct.unpack('>h', data[0:2])[0] / 131.0
        gy = struct.unpack('>h', data[2:4])[0] / 131.0
        gz = struct.unpack('>h', data[4:6])[0] / 131.0
        return gx, gy, gz
    except:
        return 0.0, 0.0, 0.0

mpu_init()

# ---------- ACCESS POINT SETUP ----------
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='StarWars-ODT', password='12345678')
print("WiFi IP:", ap.ifconfig()[0])

# ---------- HTML PAGE 1 (HOME) ----------
html1 = b"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>STAR WARS</title><style>
body{background:#000;color:#FFE81F;font-family:serif;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;margin:0;overflow:hidden}
.panel{border:1px solid #FFE81F44;padding:20px;text-align:left;max-width:300px}
.btn{background:#FFE81F;color:#000;padding:15px 30px;text-decoration:none;font-weight:900;margin-top:20px;display:inline-block}
</style></head><body><h1>STAR WARS</h1><div class="panel"><h3>Instructions:</h3><ul><li>Tilt Up/Down to move</li><li>Hit drones to score</li></ul></div><a class="btn" href="/game">START</a></body></html>"""

# ---------- HTML PAGE 2 (GAME) ----------
html2 = b"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Game</title><style>
body{background:#000;margin:0;overflow:hidden;touch-action:none;color:#FFE81F;font-family:sans-serif}
canvas{display:block}#hud{position:fixed;top:0;width:100%;display:flex;justify-content:space-around;padding:10px;background:rgba(0,0,0,0.5)}
</style></head><body><div id="hud"><span>Score: <b id="sc">0</b></span><span>Lives: <b id="lv">3</b></span></div><canvas id="cv"></canvas>
<script>
var cv=document.getElementById('cv'),ctx=cv.getContext('2d'),W,H;
function res(){W=cv.width=window.innerWidth;H=cv.height=window.innerHeight;}res();
var score=0,lives=3,gx=0,gy=0,sx=0,sy=0,ALPHA=0.15,dead=0.5,cx=window.innerWidth/2,cy=window.innerHeight/2,drones=[];
function mk(){drones.push({x:Math.random()*W,y:-20,r:15+Math.random()*10,s:1+Math.random()});}
function loop(){
 if(lives<=0){alert('Game Over! Score: '+score);location.href='/';return;}
 ctx.fillStyle='#000';ctx.fillRect(0,0,W,H);
 let mx=Math.abs(gx)>dead?gx:0, my=Math.abs(gy)>dead?gy:0;
 sx+=(mx-sx)*ALPHA;sy+=(my-sy)*ALPHA;
 cx=Math.max(20,Math.min(W-20,cx+sx*2));cy=Math.max(20,Math.min(H-20,cy-sy*2));
 ctx.strokeStyle='#0f8';ctx.strokeRect(cx-15,cy-15,30,30);
 for(var i=drones.length-1;i>=0;i--){
  var d=drones[i];d.y+=d.s*2;
  ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(d.x,d.y,d.r,0,7);ctx.fill();
  if(Math.hypot(d.x-cx,d.y-cy)<d.r+15){score+=10;drones.splice(i,1);document.getElementById('sc').innerText=score;}
  else if(d.y>H){lives--;drones.splice(i,1);document.getElementById('lv').innerText=lives;}
 }
 if(Math.random()<0.03)mk();requestAnimationFrame(loop);
}
function poll(){
 fetch('/gyro').then(r=>r.json()).then(d=>{gx=d.gx;gy=d.gy;setTimeout(poll,30);}).catch(e=>setTimeout(poll,100));
}
poll();loop();
</script></body></html>"""

# ---------- SOCKET SERVER ----------
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(1)

print("Server ready. Navigate to ESP32 IP.")

while True:
    conn = None
    try:
        gc.collect() # Clean up memory before every request
        conn, addr = server.accept()
        request = conn.recv(1024).decode()
        
        path = "/"
        if "GET /gyro" in request:
            gx, gy, gz = read_gyro()
            response = '{"gx":%.2f,"gy":%.2f}' % (gx, gy)
            conn.send(b"HTTP/1.1 200 OK\nContent-Type: application/json\nConnection: close\n\n" + response)
        elif "GET /game" in request:
            conn.send(b"HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n" + html2)
        else:
            conn.send(b"HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n" + html1)
            
    except Exception as e:
        print("Error:", e)
    finally:
        if conn:
            conn.close()

