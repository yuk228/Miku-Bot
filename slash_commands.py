import nextcord
import datetime
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import re

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @nextcord.slash_command(
        name="ping",
        description="BOTの応答速度を表示します"
    )
    async def slash_ping(self, interaction: Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! 応答速度: {latency}ms")
    
    @nextcord.slash_command(
        name="userinfo",
        description="ユーザーの情報を表示します"
    )
    async def slash_userinfo(
        self, 
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="情報を表示するメンバー",
            required=False
        )
    ):
        if member is None:
            member = interaction.user

        created_at = member.created_at.strftime('%Y年%m月%d日')
        joined_at = member.joined_at.strftime('%Y年%m月%d日')
        
        roles = [role.mention for role in member.roles[1:]]
        roles_str = ", ".join(roles) if roles else "無し"
        
        embed = nextcord.Embed(
            title=f"{member.name}({member.display_name})の情報",
            color=member.color,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="アカウント作成日", value=created_at, inline=True)
        embed.add_field(name="サーバー参加日", value=joined_at, inline=True)
        embed.add_field(name=f"ロール({len(member.roles)})", value=roles_str, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(
        name="serverinfo",
        description="サーバーの情報を表示します"
    )
    async def slash_serverinfo(self, interaction: Interaction):
        guild = interaction.guild
        created_at = guild.created_at.strftime('%Y年%m月%d日')
        
        embed = nextcord.Embed(
            title=f"{guild.name}の情報",
            color=nextcord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="ID", value=guild.id, inline=True)
        embed.add_field(name="所有者", value=guild.owner.mention, inline=True)
        embed.add_field(name="作成日", value=created_at, inline=True)
        embed.add_field(name="メンバー数", value=guild.member_count, inline=True)
        embed.add_field(name="テキストチャンネル", value=len(guild.text_channels), inline=True)
        embed.add_field(name="ボイスチャンネル", value=len(guild.voice_channels), inline=True)
        
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(
        name="inviteinfo",
        description="招待リンクからサーバー情報を取得します"
    )
    async def invite_info(
        self, 
        interaction: Interaction,
        link: str = SlashOption(
            name="invite",
            description="Discordの招待リンク",
            required=True
        )
    ):
        await interaction.response.defer()
         
        match = re.search(r"(?:https?://)?(?:www\.)?discord(?:app)?\.(?:com/invite|gg)/([a-zA-Z0-9-]+)", link)
        
        if not match:
            await interaction.followup.send("❌ 有効なDiscord招待リンクではありません。\n例: `https://discord.gg/xxxx` または `discord.gg/xxxx`")
            return
        
        try:
            invite = await self.bot.fetch_invite(match.group(1), with_counts=True)
            embed = nextcord.Embed(
                title=f"{invite.guild.name}の情報",
                description=f"招待リンク: {link}",
                color=nextcord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            if invite.guild.icon.url:
                embed.set_thumbnail(url=invite.guild.icon.url)
            
            embed.add_field(name="サーバーID", value=invite.guild.id, inline=True)
            embed.add_field(name="メンバー数", value=invite.approximate_member_count, inline=True)
            embed.add_field(name="オンラインメンバー数", value=invite.approximate_presence_count, inline=True)
            
            if invite.inviter:
                embed.add_field(name="招待作成者", value=f"{invite.inviter.name} ({invite.inviter.id})", inline=True)
            
            if invite.channel:
                embed.add_field(name="招待チャンネル", value=f"#{invite.channel.name}", inline=True)
            
            if invite.guild.description:
                embed.add_field(name="説明", value=invite.guild.description, inline=False)
            
            if invite.expires_at:
                expires_at = invite.expires_at.strftime('%Y年%m月%d日 %H:%M:%S')
                embed.add_field(name="有効期限", value=expires_at, inline=True)

            if hasattr(invite.guild, "premium_subscription_count") and invite.guild.premium_subscription_count is not None:
                boost_level = invite.guild.premium_tier if hasattr(invite.guild, "premium_tier") else "不明"
                boost_count = invite.guild.premium_subscription_count
                embed.add_field(name="ブースト", value=f"レベル {boost_level} (ブースト数: {boost_count})", inline=True)
            
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"Error: ```{e}```")

def setup(bot):
    bot.add_cog(SlashCommands(bot)) 