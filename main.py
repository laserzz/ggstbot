import hikari, lightbulb, dotenv, os

dotenv.load_dotenv()

intents = hikari.Intents.GUILD_MEMBERS | hikari.Intents.GUILDS

bot = lightbulb.BotApp(os.environ['TOKEN'], intents=intents)
bot.load_extensions_from("./extensions/")

@bot.command
@lightbulb.command("ping", description="pong!")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.SlashContext):
    await ctx.respond("pong!")

if __name__ == '__main__':
    bot.run()