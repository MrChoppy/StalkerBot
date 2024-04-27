import discord


class DiscordMessenger:
    @staticmethod
    async def send_message(message, channel=None):
        await channel.send(message)

    @staticmethod
    async def send_embed(title, description, color, channel, player_game_data=None):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        if player_game_data:
            embed.add_field(name="Role", value=player_game_data.team_position, inline=True)
            embed.add_field(name="Champion", value=player_game_data.champion_name, inline=True)
            embed.add_field(name="Kills", value=str(player_game_data.kills), inline=True)
            embed.add_field(name="Deaths", value=str(player_game_data.deaths), inline=True)
            embed.add_field(name="Assists", value=str(player_game_data.assists), inline=True)
            embed.add_field(name="Gold Earned", value=str(player_game_data.gold_earned), inline=True)
            # embed.add_field(name="Minions Killed", value=str(player_game_data.minions_killed), inline=True)
            embed.add_field(name="CS/M", value=str(player_game_data.csm), inline=True)
            embed.add_field(name="Wards Placed", value=str(player_game_data.wards_placed), inline=True)
            embed.add_field(name="Damage Dealt", value=str(player_game_data.damage_dealt), inline=True)
            embed.add_field(name="DPM", value=str(player_game_data.dpm), inline=True)
            # embed.add_field(name="Damage Taken", value=str(player_game_data.damage_taken), inline=True)
            # embed.add_field(name="Damage Struct.", value=str(player_game_data.damage_buildings), inline=True)
            # embed.add_field(name="Side", value=str(player_game_data.side), inline=True)
            embed.add_field(name="GD@15", value=str(player_game_data.gold_difference), inline=True)

        await channel.send(embed=embed)
