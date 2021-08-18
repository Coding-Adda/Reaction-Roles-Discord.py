from os import read
from discord.ext import commands
import aiosqlite
import discord
import asyncio


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.bot.loop.create_task(self.connect_database())

    async def connect_database(self):
        self.db = await aiosqlite.connect("database.db")

    @commands.group()
    async def rr(self, ctx):
        pass

    @rr.command(name="add")
    async def rr_add(
        self,
        ctx,
        message_id: int,
        channel: discord.TextChannel,
        role: discord.Role,
    ):
        msg = await ctx.send("React with a emoji that you want to bind with that role.")
        try:
            p = await self.bot.wait_for(
                "raw_reaction_add",
                check=lambda p: p.user_id == ctx.author.id and p.message_id == msg.id,
            )
        except asyncio.TimeoutError:
            return await ctx.send("You haven't responded in time.")

        if p.emoji.is_unicode_emoji():
            emoji_id = ord(str(p.emoji)[0])
        else:
            emoji_id = p.emoji.id

        await self.db.execute(
            "INSERT into 'reaction-roles' (guild_id, channel_id, role_id, message_id, emoji_id, is_custom_emoji) values(?, ?, ?, ?, ?, ?)",
            (
                ctx.guild.id,
                channel.id,
                role.id,
                message_id,
                emoji_id,
                p.emoji.is_custom_emoji(),
            ),
        )

        await self.db.commit()
        await ctx.send("Setup Successfull.")
        message = await channel.fetch_message(message_id)
        await message.add_reaction(str(p.emoji))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.is_unicode_emoji():
            emoji_id = ord(str(payload.emoji)[0])
        else:
            emoji_id = payload.emoji.id

        async with self.db.execute(
            "SELECT role_id from 'reaction-roles' where message_id = ? and emoji_id = ? and is_custom_emoji = ?",
            (payload.message_id, emoji_id, payload.emoji.is_custom_emoji()),
        ) as cursor:
            record = await cursor.fetchone()

        if record is None:
            print("Role doesn't exists")
            return
        guild = self.bot.get_guild(payload.guild_id)
        role = guild.get_role(record[0])
        await payload.member.add_roles(role, reason="Reaction roles working.")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.emoji.is_unicode_emoji():
            emoji_id = ord(str(payload.emoji)[0])
        else:
            emoji_id = payload.emoji.id

        async with self.db.execute(
            "SELECT role_id from 'reaction-roles' where message_id = ? and emoji_id = ? and is_custom_emoji = ?",
            (payload.message_id, emoji_id, payload.emoji.is_custom_emoji()),
        ) as cursor:
            record = await cursor.fetchone()

        if record is None:
            print("Role doesn't exists")
            return
        guild = self.bot.get_guild(payload.guild_id)
        role = guild.get_role(record[0])
        member = await guild.fetch_member(payload.user_id)
        await member.remove_roles(role, reason="Reaction roles working.")


def setup(bot):
    bot.add_cog(ReactionRoles(bot))
