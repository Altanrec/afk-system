import discord
import asyncio
import threading
import os

class AFKBot:
    def __init__(self, token, guild_id, channel_id):
        self.token = token
        self.guild_id = int(guild_id)
        self.channel_id = int(channel_id)
        self.client = None
        self.voice_client = None
        self.thread = None
        self.loop = None
        self.running = False
        self.status = "başlatılıyor"

    def start(self):
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        intents = discord.Intents.default()
        intents.voice_states = True
        intents.guilds = True

        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready():
            self.status = "bağlandı"
            print(f"[+] {self.client.user} giriş yaptı")
            await self._join_voice()

        try:
            self.loop.run_until_complete(self.client.start(self.token))
        except Exception as e:
            self.status = f"hata: {str(e)[:80]}"
            print(f"[!] Hata: {e}")

    async def _join_voice(self):
        try:
            guild = self.client.get_guild(self.guild_id)
            if not guild:
                self.status = "sunucu bulunamadı"
                return

            channel = guild.get_channel(self.channel_id)
            if not channel:
                self.status = "kanal bulunamadı"
                return

            self.voice_client = await channel.connect(self_deaf=True)
            self.running = True
            self.status = f"AFK: {channel.name}"
            print(f"[+] {channel.name} kanalına katıldı")
        except Exception as e:
            self.status = f"ses hatası: {str(e)[:80]}"
            print(f"[!] Ses hatası: {e}")

    def stop(self):
        self.running = False
        if self.loop and self.client:
            async def _disconnect():
                try:
                    if self.voice_client and self.voice_client.is_connected():
                        await self.voice_client.disconnect()
                    await self.client.close()
                except Exception:
                    pass
            asyncio.run_coroutine_threadsafe(_disconnect(), self.loop)
        self.status = "durduruldu"


class BotManager:
    def __init__(self):
        self.bots = {}

    def add_bot(self, bot_id, token, guild_id, channel_id):
        if bot_id in self.bots:
            self.bots[bot_id].stop()
        bot = AFKBot(token, guild_id, channel_id)
        bot.start()
        self.bots[bot_id] = bot
        return bot

    def remove_bot(self, bot_id):
        if bot_id in self.bots:
            self.bots[bot_id].stop()
            del self.bots[bot_id]
            return True
        return False

    def get_all(self):
        return {
            bid: {
                "status": bot.status,
                "guild_id": bot.guild_id,
                "channel_id": bot.channel_id
            }
            for bid, bot in self.bots.items()
        }