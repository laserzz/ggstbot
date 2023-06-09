import aiohttp, lightbulb, hikari
from ggst import GGSTWebScraper

web = GGSTWebScraper(aiohttp.ClientSession())

plugin = lightbulb.Plugin("Stats")


@plugin.command
@lightbulb.option("character", "GGST Character", str, required=True)
@lightbulb.option("user", "GGST user", str, required=True)
@lightbulb.add_cooldown(180, 1, lightbulb.UserBucket)
@lightbulb.command("elo", "see elo for a character", pass_options=True, auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def elo(ctx: lightbulb.SlashContext, user: str, character: str):
    try:
        user_page = await web.search_player(user)
        char_data = web.search_player_char_link(user_page, character)
        elo = await web.get_elo(char_data)
    except Exception as e:
        print(e)
        return await ctx.respond(
            "Something went wrong. Ensure you typed the usernames and characters correctly or try again later."
        )
    desc = f"**Character:** {elo['character']}\n**Rating:** {elo['elo']}\n **Offset:** {elo['offset']}\n**Games:** {elo['games']}\n**Position:** {elo['position']}"
    embed = hikari.Embed(
        title=f"ELO info for {user}",
        description=desc,
        color=hikari.Color.from_rgb(255, 25, 100),
    )
    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.option("character", "GGST Character", str, required=True)
@lightbulb.option("user", "GGST user", str, required=True)
@lightbulb.add_cooldown(180, 1, lightbulb.UserBucket)
@lightbulb.command(
    "matchups", "see your matchup stats", pass_options=True, auto_defer=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def matchups(ctx: lightbulb.SlashContext, user: str, character: str):
    try:
        user_page = await web.search_player(user)
        char_page = web.search_player_char_link(user_page, character)
        player = await web.get_player_char_page_data(char_page)
        player_data = web.get_matchup_stats(player)
        desc = "**Character** - **Matches** - **Win Rate**\n"
        for i in player_data:
            desc += f"{i['character']} - {i['matches']} - {i['win_rate']}\n"
        embed = hikari.Embed(
            title=f"Matchup info for {user}",
            description=desc,
            color=hikari.Color.from_rgb(255, 25, 100),
        )
        await ctx.respond(embed=embed)
    except Exception as e:
        print(e)
        return await ctx.respond(
            "Something went wrong. Ensure you typed the usernames and characters correctly or try again later."
        )


@plugin.listener(lightbulb.SlashCommandErrorEvent)
async def error_listener(event: lightbulb.SlashCommandErrorEvent):
    if isinstance(event.exception, lightbulb.errors.CommandIsOnCooldown):
        await event.context.respond("This command is currently on cooldown.")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)
