import re
import requests
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
        await interaction.followup.send(f"Pong! 応答速度: {latency}ms")
    
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
        
        await interaction.followup.send(embed=embed)

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

    @nextcord.slash_command(
        name="ipinfo",
        description="IP Addressから情報を取得します。"
    )
    async def invite_info(
        self, 
        interaction: Interaction,
        ip: str = SlashOption(
            name="ip",
            description="ip",
            required=True
        )
    ):
        ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if not re.match(ip_pattern, ip):
            await interaction.response.send_message("無効なIPアドレス形式です。正しいIPv4アドレスを入力してください。")
            return
            
        octets = ip.split('.')
        for octet in octets:
            if not 0 <= int(octet) <= 255:
                await interaction.response.send_message("無効なIPアドレスです。各オクテットは0から255の範囲内である必要があります。")
                return
                
        await interaction.response.defer()

        res = requests.get(f"https://ipinfo.io/{ip}").json()
        
        embed = nextcord.Embed(
                title=f"IP Lookup",
                description=f"IP: {ip}",
                color=nextcord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
        embed.add_field(name="ホスト名", value=res.get("hostname", "None"), inline=True)
        embed.add_field(name="都市", value=res.get("city", "None"), inline=True)
        embed.add_field(name="地域", value=res.get("region", "None"), inline=True)
        embed.add_field(name="国", value=res.get("country", "None"), inline=True)
        embed.add_field(name="郵便番号", value=res.get("postal", "None"), inline=True)
        embed.add_field(name="タイムゾーン", value=res.get("timezone", "None"), inline=True)
        embed.add_field(name="組織", value=res.get("org", "None"), inline=True)
        embed.add_field(name="位置情報", value=res.get("loc", "None"), inline=True)
        embed.add_field(name="Anycast", value=res.get("anycast", "None"), inline=True)
        await interaction.followup.send(embed=embed)
        
def setup(bot):
    bot.add_cog(SlashCommands(bot))