import nextcord
import datetime
from nextcord.ext import commands
from nextcord import Interaction, SlashOption

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

def setup(bot):
    bot.add_cog(SlashCommands(bot)) 