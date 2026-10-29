import os
import sys
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import discord

# =====================================================================
# 🌍 RENDER / UPTIME ROBOT İÇİN ARKA PLAN WEB SUNUCUSU
# =====================================================================
def run_dummy_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"🌍 Web sunucusu aktif: {port}")
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# =====================================================================
# 🤖 SELF-BOT - 7/24 SES KANALINDA AFK
# =====================================================================

TOKEN = os.getenv("SELF_TOKEN")
SES_KANAL_STR = os.getenv("SES_KANAL_ID", "")

if not TOKEN:
    sys.exit("❌ HATA: SELF_TOKEN eksik!")
if not SES_KANAL_STR.isdigit():
    sys.exit("❌ HATA: SES_KANAL_ID hatalı veya eksik!")

SES_KANAL_ID = int(SES_KANAL_STR)

client = discord.Client()

async def ses_baglantisi_koru():
    await client.wait_until_ready()
    print("⏳ Ses kanalına bağlanmaya çalışıyor...")

    while not client.is_closed():
        try:
            kanal = client.get_channel(SES_KANAL_ID)
            if kanal is None:
                kanal = await client.fetch_channel(SES_KANAL_ID)

            # Zaten bağlıysa bir şey yapma
            if client.voice_clients:
                vc = client.voice_clients[0]
                if vc.channel and vc.channel.id == SES_KANAL_ID and vc.is_connected():
                    await asyncio.sleep(30)
                    continue

            # Bağlan
            print(f"🔊 Ses kanalına giriliyor: {kanal.name} ({SES_KANAL_ID})")
            vc = await kanal.connect(reconnect=True, timeout=60)
            print("✅ Ses kanalına başarıyla girildi! 7/24 AFK aktif.")

            # Bağlantı kopana kadar bekle
            while vc.is_connected():
                await asyncio.sleep(20)

            print("⚠️ Ses bağlantısı koptu, yeniden bağlanılacak...")

        except Exception as e:
            print(f"❌ Ses bağlantı hatası: {e}")
            await asyncio.sleep(15)

@client.event
async def on_ready():
    print("=========================================")
    print(f"🤖 Bağlantı başarılı: {client.user}")
    print(f"🔊 Hedef Ses Kanalı ID: {SES_KANAL_ID}")
    print("=========================================")
    client.loop.create_task(ses_baglantisi_koru())

@client.event
async def on_voice_state_update(member, before, after):
    # Kendimiz ses kanalından atılırsak tekrar girmeye çalışır
    if member.id == client.user.id:
        if before.channel and not after.channel:
            print("⚠️ Ses kanalından çıkarıldık, tekrar girilecek...")

client.run(TOKEN)
