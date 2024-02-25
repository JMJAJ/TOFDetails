import asyncio
import io
import os
from io import BytesIO

import aiohttp
import discord
import requests
from discord import File
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image
from tabulate import tabulate

from keep_alive import keep_alive

keep_alive()

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# link = https://discord.com/oauth2/authorize?client_id=1210764069439668235&permissions=1073817664&scope=bot


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.command()
async def help_catto(ctx):
    embed = discord.Embed(title="Tower of Catto Bot Commands",
                          color=discord.Color.blue())

    embed.add_field(name="Character",
                    value="Displays details about a character.",
                    inline=False)
    embed.add_field(name="",
                    value="Usage: !character [character_name], !character list",
                    inline=False)

    embed.add_field(name="Weapon",
                    value="Displays details about a weapon.",
                    inline=False)
    embed.add_field(name="",
                    value="Usage: !weapon [weapon_name], !weapon list",
                    inline=False)

    embed.add_field(name="Banner",
                    value="Displays details about a banner.",
                    inline=False)
    embed.add_field(name="",
                    value="Usage: !banner [character_name], !banner list",
                    inline=False)

    embed.add_field(name="Servant",
                    value="Displays details about a servant.",
                    inline=False)
    embed.add_field(name="",
                    value="Usage: !servant [servant_name], !servant list",
                    inline=False)

    embed.add_field(name="Matrix",
                    value="Displays details about a matrix.",
                    inline=False)
    embed.add_field(name="",
                    value="Usage: !matrix [character_name], !matrix list",
                    inline=False)

    embed.add_field(name="Gift",
                    value="Displays what specific character wants.",
                    inline=False)
    embed.add_field(
        name="", value="Usage: !gift [character_name]", inline=False)

    embed.add_field(name="Outfit",
                    value="Displays details about an outfit.",
                    inline=False)
    embed.add_field(name="",
                    value="Usage: outfit [outfit_name], !outfit list",
                    inline=False)

    embed.add_field(name="Relic",
                    value="Displays details about a relic.",
                    inline=False)
    embed.add_field(name="",
                    value="Usage: !relic [relic_name], !relic list",
                    inline=False)

    embed.add_field(name="Mount/Vehicle",
                    value="Displays details about a vehicle.",
                    inline=False)
    embed.add_field(name="",
                    value="Usage: !mount [mount_name], !mount list",
                    inline=False)

    embed.add_field(name="Achievement",
                    value="Displays details about an achievement.",
                    inline=False)
    embed.add_field(
        name="",
        value="Usage: !achievement [achievement_name], !achievement list",
        inline=False)

    embed.add_field(name="Gear",
                    value="Displays details about a gear stats.",
                    inline=False)
    embed.add_field(name="", value="Usage: !gear", inline=False)

    await ctx.send(embed=embed)


@commands.command(name='ping',
                  description='Check if the bot is responsive.',
                  aliases=['pong'],
                  usage='!ping',
                  examples=['!ping', '!pong'])
async def ping(ctx):
    await ctx.send('Pong!')


bot.add_command(ping)


@bot.command()
async def weapon(ctx, *, arg):
    if arg == "list":
        await list_all_weapons(ctx)
    else:
        await fetch_weapon_details(ctx, arg)


async def list_all_weapons(ctx):
    weapon_names = fetch_all_weapon_names()
    if weapon_names:
        table_data = [(weapon, ) for weapon in weapon_names]
        table = tabulate(table_data, tablefmt='plain')

        MAX_MESSAGE_LENGTH = 2000 - len("List of available weapons:\n``````")
        chunks = [
            table[i:i + MAX_MESSAGE_LENGTH]
            for i in range(0, len(table), MAX_MESSAGE_LENGTH)
        ]
        num_pages = len(chunks)
        current_page = 1

        def check_reaction(reaction, user):
            return user == ctx.author and str(
                reaction.emoji) in ['◀️', '▶️'] and reaction.message.id == msg.id

        while True:
            embed = discord.Embed(
                description=f"Page {
                    current_page}/{num_pages}:\n```{chunks[current_page - 1]}```"
            )
            embed.set_footer(
                text="React with ◀️ or ▶️ to navigate through pages.")

            msg = await ctx.send(embed=embed)
            if num_pages == 1:
                return

            if num_pages > 1:
                await msg.add_reaction('◀️')
                await msg.add_reaction('▶️')

                try:
                    reaction, user = await bot.wait_for('reaction_add',
                                                        timeout=60.0,
                                                        check=check_reaction)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    break

                await msg.clear_reactions()

                if str(reaction.emoji) == '▶️' and current_page < num_pages:
                    current_page += 1
                elif str(reaction.emoji) == '◀️' and current_page > 1:
                    current_page -= 1

    else:
        await ctx.send("No weapons found.")


async def fetch_weapon_details(ctx, arg):
    # Fetch weapon details using arg
    weapon_data = fetch_weapon_data(arg)

    if weapon_data:
        formatted_details = await format_weapon_details(ctx, weapon_data)
        await send_long_message(ctx, formatted_details)
    else:
        await ctx.send("Error fetching weapon details.")


async def send_long_message(ctx, message):
    MAX_MESSAGE_LENGTH = 2000

    chunks = [
        message[i:i + MAX_MESSAGE_LENGTH]
        for i in range(0, len(message), MAX_MESSAGE_LENGTH)
    ]

    for chunk in chunks:
        await ctx.send(chunk)


def fetch_all_weapon_names():
    api_url = 'https://api.toweroffantasy.info/weapons?lang=en&include=true&includeUnreleased=true'
    response = requests.get(api_url)
    if response.status_code == 200:
        weapons = response.json()
        return [weapon['name'] for weapon in weapons]
    return None


def fetch_weapon_data(weapon_name):
    api_url = 'https://api.toweroffantasy.info/weapons?lang=en&include=true&includeUnreleased=true'
    response = requests.get(api_url)
    if response.status_code == 200:
        weapons = response.json()
        for weapon in weapons:
            if weapon['name'].lower() == weapon_name.lower():
                return weapon
    return None


async def send_icon_url(ctx, icon_url):
    icon_message = f"## Icon: [Click Here]({icon_url})"
    await ctx.send(icon_message)


async def format_weapon_details(ctx, weapon_data):
    weapon_name = weapon_data['name']
    rarity = weapon_data['rarity']
    description = weapon_data['description']
    icon_url = weapon_data['assets']['icon']
    weapon_effects = weapon_data['weaponEffects']
    weapon_advancements = weapon_data['weaponAdvancements']
    weapon_attacks = weapon_data['weaponAttacks']

    formatted_details = f"## Weapon Name: {weapon_name}\n"
    formatted_details += f"## Rarity: {rarity}*\n"
    formatted_details += f"## Description: {description}\n"

    if weapon_effects:
        formatted_details += "## Weapon Effects:\n"
        for effect in weapon_effects:
            formatted_details += f"- {effect['title']
                                      }: {effect['description']}\n"

    # Add weapon advancements section if present
    formatted_details += "## Weapon Advancements:\n"
    if not weapon_advancements:
        formatted_details += "No weapon advancements available.\n"
    else:
        for i, advancement in enumerate(weapon_advancements, start=1):
            formatted_details += f"- A{i}: {advancement['description']}\n"

    if weapon_attacks:
        formatted_details += "## Weapon Attacks:\n"
        for attack in weapon_attacks['normals']:
            formatted_details += f"- {attack['name']
                                      }: {attack['description']}\n"

    # Send just the icon URL in a new message
    await send_icon_url(ctx, icon_url)

    return formatted_details


@bot.command()
async def banner(ctx, *, arg=None):
    if arg == "list":
        await list_all_simulacrums(ctx)
    else:
        await fetch_simulacrum_details(ctx, arg)


async def list_all_simulacrums(ctx):
    api_url = 'https://api.toweroffantasy.info/extras/banners?includeUnreleased=true'
    simulacrum_data = fetch_simulacrum_data(api_url)

    if simulacrum_data:
        table_data = [(simulacrum.get(
            'simulacrumName', 'Unknown Name'
        ), f"{simulacrum.get('startDate', 'Unknown Version')} - {simulacrum.get('endDate', 'Unknown Version')}"
        ) for simulacrum in simulacrum_data]

        headers = ['Simulacrum Name', 'Date']
        characters_per_page = 10
        total_pages = (len(table_data) + characters_per_page -
                       1) // characters_per_page
        current_page = 1
        sent_messages = []

        while True:
            start_index = (current_page - 1) * characters_per_page
            end_index = start_index + characters_per_page
            current_simulacrums = table_data[start_index:end_index]

            table = tabulate(current_simulacrums,
                             headers=headers, tablefmt='plain')
            embed = discord.Embed(
                description=f"Page {current_page}/{total_pages}:\n```{table}```")

            if sent_messages:
                for message_id in sent_messages:
                    message = await ctx.fetch_message(message_id)
                    await message.delete()
                sent_messages.clear()

            message = await ctx.send(embed=embed)
            sent_messages.append(message.id)

            await message.add_reaction('◀️')
            await message.add_reaction('▶️')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['◀️', '▶️']

            try:
                reaction, user = await bot.wait_for('reaction_add',
                                                    timeout=60.0,
                                                    check=check)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

            await message.clear_reactions()

            if str(reaction.emoji) == '◀️' and current_page > 1:
                current_page -= 1
            elif str(reaction.emoji) == '▶️' and current_page < total_pages:
                current_page += 1
            else:
                break
    else:
        await ctx.send("Error fetching simulacrum data.")


async def fetch_simulacrum_details(ctx, simulacrum_name):
    api_url = 'https://api.toweroffantasy.info/extras/banners?includeUnreleased=true'
    simulacrum_data = fetch_simulacrum_data(api_url)
    if simulacrum_data:
        selected_simulacrum = find_simulacrum_by_name(simulacrum_data,
                                                      simulacrum_name)
        if selected_simulacrum:
            formatted_details = format_simulacrum_details(selected_simulacrum)
            await ctx.send(formatted_details)
        else:
            await ctx.send("Simulacrum not found.")
    else:
        await ctx.send("Error fetching simulacrum data.")


def fetch_simulacrum_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching simulacrum data: {response.status_code}')
        return None


def find_simulacrum_by_name(simulacrum_data, simulacrum_name):
    for simulacrum in simulacrum_data:
        if simulacrum['simulacrumName'].lower() == simulacrum_name.lower():
            return simulacrum
    return None


def format_simulacrum_details(simulacrum_data):
    details_link = simulacrum_data['detailsLink']
    element = simulacrum_data['element']
    formatted_element = "Altered" if element == "Superpower" else element
    rerun = simulacrum_data['isRerun']
    formatted_rerun = "Yes" if rerun else "No"
    collab = simulacrum_data['isCollab']
    formatted_collab = "Yes" if collab else "No"

    formatted_details = f"Simulacrum Name: {
        simulacrum_data['simulacrumName']}\n"
    formatted_details += f"Start Date: {simulacrum_data['startDate']}\n"
    formatted_details += f"End Date: {simulacrum_data['endDate']}\n"
    formatted_details += f"Category: {simulacrum_data['category']}\n"
    formatted_details += f"Element: {formatted_element}\n"
    formatted_details += f"Rerun: {formatted_rerun}\n"
    formatted_details += f"Collab: {formatted_collab}\n"
    formatted_details += f"Details Link: [Click Here]({details_link})\n"

    return formatted_details


@bot.command()
async def matrix(ctx, *, arg=None):
    if arg is None or arg.lower() == "list":
        await list_all_matrix(ctx)
    else:
        await fetch_matrix_details(ctx, arg)


async def list_all_matrix(ctx):
    api_url = 'https://api.toweroffantasy.info/matrices?lang=en&include=true&includeUnreleased=true'
    matrix_data = fetch_matrix_data(api_url)
    if matrix_data:
        table_data = [(matrix['name'], ) for matrix in matrix_data]
        table = tabulate(table_data, tablefmt='plain')

        MAX_MESSAGE_LENGTH = 2000 - len("List of available matrices:\n``````")
        chunks = [
            table[i:i + MAX_MESSAGE_LENGTH]
            for i in range(0, len(table), MAX_MESSAGE_LENGTH)
        ]
        num_pages = len(chunks)
        current_page = 1

        def check_reaction(reaction, user):
            return user == ctx.author and str(
                reaction.emoji) in ['◀️', '▶️'] and reaction.message.id == msg.id

        while True:
            embed = discord.Embed(
                description=f"Page {
                    current_page}/{num_pages}:\n```{chunks[current_page - 1]}```"
            )
            embed.set_footer(
                text="React with ◀️ or ▶️ to navigate through pages.")

            msg = await ctx.send(embed=embed)
            if num_pages == 1:
                return

            if num_pages > 1:
                await msg.add_reaction('◀️')
                await msg.add_reaction('▶️')

                try:
                    reaction, user = await bot.wait_for('reaction_add',
                                                        timeout=60.0,
                                                        check=check_reaction)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    break

                await msg.clear_reactions()

                if str(reaction.emoji) == '▶️' and current_page < num_pages:
                    current_page += 1
                elif str(reaction.emoji) == '◀️' and current_page > 1:
                    current_page -= 1

    else:
        await ctx.send("Error fetching matrix data.")


async def fetch_matrix_details(ctx, matrix_name):
    api_url = 'https://api.toweroffantasy.info/matrices?lang=en&include=true&includeUnreleased=true'
    matrix_data = fetch_matrix_data(api_url)
    if matrix_data:
        selected_matrix = find_matrix_by_name(matrix_data, matrix_name)
        if selected_matrix:
            formatted_details = format_matrix_details(selected_matrix)
            await ctx.send(formatted_details)
        else:
            await ctx.send("Matrix not found.")
    else:
        await ctx.send("Error fetching matrix data.")


def fetch_matrix_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching data: {response.status_code}')
        return None


def find_matrix_by_name(matrix_data, matrix_name):
    for matrix in matrix_data:
        if matrix['name'].lower() == matrix_name.lower():
            return matrix
    return None


def format_matrix_details(matrix_data):
    matrix_name = matrix_data['name']
    rarity = matrix_data['rarity']
    icon_url = matrix_data['assets']['icon']
    description = matrix_data['description']

    # Constructing the details string
    formatted_details = f"Matrix Name: {matrix_name}\n"
    formatted_details += f"Rarity: {rarity}*\n"
    formatted_details += f"Description: {description}\n"
    formatted_details += f"Icon: [Click Here]({icon_url})\n"

    # Adding sets information
    formatted_details += "Sets:\n"
    for set_info in matrix_data['sets']:
        need = set_info['need']
        description = set_info['description']
        formatted_details += f"- Need: {need}\n"
        formatted_details += f"  Description: {description}\n"

    return formatted_details


@bot.command()
async def servant(ctx, *, arg=None):
    if arg is None or arg.lower() == "list":
        await list_all_servants(ctx)
    else:
        await fetch_servant_details(ctx, arg)


async def list_all_servants(ctx):
    api_url = 'https://api.toweroffantasy.info/servants'
    servant_data = fetch_servant_data(api_url)
    if servant_data:
        table_data = [(servant['name'], ) for servant in servant_data]
        table = tabulate(table_data, headers=[
                         'Servant Name'], tablefmt='plain')
        await ctx.send(f"List of available servants:\n```{table}```")
    else:
        await ctx.send("Error fetching servant data.")


async def fetch_servant_details(ctx, name):
    servant_id = find_servant_id_by_name(name)
    if servant_id:
        api_url = f'https://api.toweroffantasy.info/servants/{servant_id}'
        servant_data = fetch_servant_data(api_url)
        if servant_data:
            formatted_details = format_servant_details(servant_data)

            MAX_MESSAGE_LENGTH = 2000
            chunks = [
                formatted_details[i:i + MAX_MESSAGE_LENGTH]
                for i in range(0, len(formatted_details), MAX_MESSAGE_LENGTH)
            ]

            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send("Error fetching servant details.")
    else:
        await ctx.send("Servant not found.")


def fetch_servant_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def find_servant_id_by_name(name):
    api_url = 'https://api.toweroffantasy.info/servants'
    servant_data = fetch_servant_data(api_url)
    if servant_data:
        for servant in servant_data:
            if servant['name'].lower() == name.lower():
                return servant['id']
    return None


def format_servant_details(servant_data):
    name = servant_data['name']
    description = servant_data['description']
    rarity = servant_data['rarity']
    element = servant_data['element']
    servant_type = servant_data['type']
    pet_icon = servant_data['assets']['petIcon']
    activated_icon = servant_data['assets']['activatedIcon']
    item_icon = servant_data['assets']['itemIcon']
    skills = servant_data['skills']
    upgrade_items = servant_data['upgradeItems']

    formatted_details = f"Name: {name}\n"
    formatted_details += f"Description: {description}\n"
    formatted_details += f"Rarity: {rarity}\n"
    formatted_details += f"Element: {element}\n"
    formatted_details += f"Type: {servant_type}\n"

    formatted_details += "## Skills:\n"
    for skill in skills:
        formatted_details += f"- {skill['name']}: {skill['description']}\n"

    formatted_details += "\n"
    formatted_details += "## Upgrade Items:\n"
    for item in upgrade_items:
        material_name = item['material']['name']
        material_description = item['material']['description']
        exp = item['exp']
        formatted_details += f"- {material_name} (EXP: {exp}): {
            material_description}\n"

    formatted_details += f"## Pet Icon: [Click Here]({pet_icon})\n"
    formatted_details += f"## Activated Icon: [Click Here]({activated_icon})\n"
    formatted_details += f"## Item Icon: [Click Here]({item_icon})\n\n"

    return formatted_details


@bot.command()
async def gear(ctx):
    stat_ranges = [
        ["Altered Attack", "137", "249", "623", "2,317", "3,252"],
        ["Altered Resistance", "215", "390", "974", "3,625", "5,085"],
        ["Altered Resistance %", "7.87%", "9%", "9%", "52.87%", "52.87%"],
        ["Attack", "52", "93", "234", "870", "1,222"],
        ["Crit", "258", "468", "1,169", "4,351", "6,103"],
        ["Crit Rate %", "1.05%", "1.19%", "1.19%", "7%", "7%"],
        ["Flame Attack", "69", "125", "312", "1,162", "1,629"],
        ["Flame Attack %", "1.26%", "1.44%", "1.44%", "8.46%", "8.46%"],
        ["Flame Damage %", "0.65%", "0.72%", "0.72%", "4.25%", "4.25%"],
        ["Flame Resistance", "215", "390", "974", "3,625", "5,085"],
        ["Flame Resistance %", "7.87%", "9%", "9%", "52.87%", "52.87%"],
        ["Frost Attack", "69", "125", "312", "1,162", "1,629"],
        ["Frost Attack %", "1.26%", "1.44%", "1.44%", "8.46%", "8.46%"],
        ["Frost Damage %", "0.65%", "0.72%", "0.72%", "4.25%", "4.25%"],
        ["Frost Resistance", "215", "390", "974", "3,625", "5,085"],
        ["Frost Resistance %", "7.87%", "9%", "9%", "52.87%", "52.87%"],
        ["HP", "4,125", "7,480", "18,700", "69,575", "97,625"],
        ["HP %", "0.94%", "1.08%", "1.08%", "6.34%", "6.34%"],
        ["Physical Attack", "69", "125", "312", "1,162", "1,629"],
        ["Physical Attack %", "1.26%", "1.44%", "1.44%", "8.46%", "8.46%"],
        ["Physical Damage %", "0.65%", "0.72%", "0.72%", "4.25%", "4.25%"],
        ["Physical Resistance", "215", "390", "974", "3,625", "5,085"],
        ["Physical Resistance %", "7.87%", "9%", "9%", "52.87%", "52.87%"],
        ["Resistance", "64", "117", "292", "1,087", "1,524"],
        ["Volt Attack", "69", "125", "312", "1,162", "1,629"],
        ["Volt Attack %", "1.26%", "1.44%", "1.44%", "8.46%", "8.46%"],
        ["Volt Damage %", "0.65%", "0.72%", "0.72%", "4.25%", "4.25%"],
        ["Volt Resistance", "215", "390", "974", "3,625", "5,085"],
        ["Volt Resistance %", "7.87%", "9%", "9%", "52.87%", "52.87%"],
    ]

    table = tabulate(stat_ranges,
                     headers=[
                         "Stat", "Base value", "Min. roll value",
                         "Max. roll value", "Avg. total value at 5 rolls",
                         "Max. total value at 5 rolls"
                     ],
                     tablefmt="plain")

    # Save the table as a file in memory
    table_file = io.BytesIO(table.encode())

    # Send the file as an attachment
    await ctx.send(file=File(table_file, filename="gear_stats.txt"))


@bot.command()
async def character(ctx, *, arg=None):
    if arg is None or arg.lower() == "list":
        api_url = 'https://api.toweroffantasy.info/simulacra-v2?lang=en&include=true&includeUnreleased=true'
        character_data = fetch_character_data(api_url)
        if character_data:
            await list_all_characters(ctx, character_data)
        else:
            await ctx.send("Error fetching character data.")
    else:
        await fetch_character_details(ctx, arg)


async def list_all_characters(ctx, character_data):
    try:
        table_data = [(character['name'], character.get('rarity', 'N/A'),
                       character.get('element', 'N/A'))
                      for character in character_data]

        headers = ['Name', 'Rarity', 'Element']
        characters_per_page = 10
        total_pages = (len(table_data) + characters_per_page -
                       1) // characters_per_page
        current_page = 1
        sent_messages = []

        while True:
            start_index = (current_page - 1) * characters_per_page
            end_index = start_index + characters_per_page
            current_characters = table_data[start_index:end_index]

            table = tabulate(current_characters,
                             headers=headers,
                             tablefmt='fancy_grid')
            embed = discord.Embed(title="List of Characters",
                                  description=f"Page {
                                      current_page}/{total_pages}",
                                  color=discord.Color.blue())
            embed.add_field(name="Character Details",
                            value=f"```{table}```",
                            inline=False)

            if sent_messages:
                for message_id in sent_messages:
                    message = await ctx.fetch_message(message_id)
                    await message.delete()
                sent_messages.clear()

            message = await ctx.send(embed=embed)
            sent_messages.append(message.id)

            await message.add_reaction('◀️')
            await message.add_reaction('▶️')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['◀️', '▶️']

            try:
                reaction, user = await bot.wait_for('reaction_add',
                                                    timeout=60.0,
                                                    check=check)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

            await message.clear_reactions()

            if str(reaction.emoji) == '◀️' and current_page > 1:
                current_page -= 1
            elif str(reaction.emoji) == '▶️' and current_page < total_pages:
                current_page += 1
            else:
                break

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


async def fetch_character_details(ctx, character_name):
    api_url = 'https://api.toweroffantasy.info/simulacra-v2?lang=en&include=true&includeUnreleased=true'
    character_data = fetch_character_data(api_url)
    if character_data:
        selected_character = find_character_by_name(
            character_data, character_name)
        if selected_character:
            formatted_details = await format_character_details(selected_character)
            await send_paginated_message(ctx, formatted_details)
        else:
            await ctx.send("Character not found.")
    else:
        await ctx.send("Error fetching character data.")


async def send_paginated_message(ctx, content):
    chunks = [content[i:i + 1900] for i in range(0, len(content), 1900)]
    for chunk in chunks:
        embed = discord.Embed(title="Character Details",
                              description=chunk,
                              color=discord.Color.blue())
        await ctx.send(embed=embed)


def fetch_character_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching character data: {response.status_code}')
        return None


def find_character_by_name(character_data, character_name):
    for character in character_data:
        if character.get('name', '').lower() == character_name.lower():
            return character
    return None


async def format_character_details(character_data):
    formatted_details = "# Character Details:\n"
    formatted_details += f"Name: {character_data.get('name', 'N/A')}\n"
    formatted_details += f"ID: {character_data.get('id', 'N/A')}\n"
    formatted_details += f"Rarity: {character_data.get('rarity', 'N/A')}\n"
    formatted_details += f"Version: {character_data.get('version', 'N/A')}\n"
    formatted_details += f"Released: {
        'Yes' if character_data.get('isReleased', False) else 'No'}\n"
    formatted_details += f"Gender: {character_data.get('gender', 'N/A')}\n"
    formatted_details += f"Birthday: {character_data.get('birthday', 'N/A')}\n"
    formatted_details += f"Height: {character_data.get('height', 'N/A')}\n"
    formatted_details += f"Affiliation: {
        character_data.get('affiliation', 'N/A')}\n"

    formatted_details += f"Avatar: [Click Here]({character_data.get(
        'assetsA0', {}).get('avatar', 'N/A')})\n"
    formatted_details += f"Character Artwork: [Click Here]({character_data.get(
        'assetsA0', {}).get('characterArtwork', 'N/A')})\n"
    formatted_details += f"Weapon Show Picture: [Click Here]({character_data.get(
        'assetsA0', {}).get('weaponShowPicture', 'N/A')})\n"

    weapon_info = character_data.get('weapon', {})
    formatted_details += "## Weapon:\n"
    formatted_details += f"- ID: {weapon_info.get('id', 'N/A')}\n"
    formatted_details += f"- Simulacrum ID: {
        weapon_info.get('simulacrumId', 'N/A')}\n"
    formatted_details += f"- Advance ID: {
        weapon_info.get('advanceId', 'N/A')}\n"

    matrix_info = character_data.get('matrix', {})
    formatted_details += "## Matrix:\n"
    formatted_details += f"- ID: {matrix_info.get('id', 'N/A')}\n"
    formatted_details += f"- Name: {matrix_info.get('name', 'N/A')}\n"
    formatted_details += f"- Version: {matrix_info.get('version', 'N/A')}\n"

    formatted_details += "## Gifts\n"
    formatted_details += "Liked Gift Types: " + ", ".join(
        character_data.get('likedGiftTypes', [])) + "\n"
    formatted_details += "Disliked Gift Types: " + ", ".join(
        character_data.get('dislikedGiftTypes', [])) + "\n"

    voicing_info = character_data.get('voicing', {})
    formatted_details += "## Voicing:\n"
    for language, voice_actor in voicing_info.items():
        formatted_details += f"- {language}: {voice_actor}\n"

    formatted_details += "## Banners:\n"
    for banner in character_data.get('banners', []):
        formatted_details += f"- Simulacrum ID: {
            banner.get('simulacrumId', 'N/A')}\n"
        formatted_details += f"- Weapon ID: {banner.get('weaponId', 'N/A')}\n"
        formatted_details += f"- Matrix ID: {banner.get('matrixId', 'N/A')}\n"

    formatted_details += "## Awakening:\n"
    for awakening in character_data.get('awakening', []):
        formatted_details += f"- Need: {awakening.get('need', 'N/A')}\n"
        formatted_details += f"- Name: {awakening.get('name', 'N/A')}\n"
        formatted_details += f"- Description: {
            awakening.get('description', 'N/A')}\n"

    formatted_details += "## Guidebook:\n"
    for guidebook in character_data.get('guidebook', []):
        formatted_details += f"- Title: {guidebook.get('title', 'N/A')}\n"
        formatted_details += f"- Description: {
            guidebook.get('description', 'N/A')}\n"
        # formatted_details += f"- Icon: [Click Here]({guidebook.get('icon', 'N/A')})\n"

    return formatted_details


@bot.command()
async def gift(ctx, name):
    api_url = 'https://api.toweroffantasy.info/simulacra-v2?lang=en&include=true&includeUnreleased=true'
    character_data = fetch_character_data(api_url)

    if character_data:
        character = next(
            (char
             for char in character_data if char['name'].lower() == name.lower()),
            None)

        if character:
            liked_gifts = "\n".join(character.get('likedGiftTypes', []))
            disliked_gifts = "\n".join(character.get('dislikedGiftTypes', []))

            embed = discord.Embed(title=f"Gift Preferences for {name}",
                                  color=discord.Color.blue())
            embed.add_field(name="Liked Gift",
                            value=liked_gifts if liked_gifts else "None",
                            inline=True)
            embed.add_field(name="Disliked Gift",
                            value=disliked_gifts if disliked_gifts else "None",
                            inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Character '{name}' not found.")
    else:
        await ctx.send("Error fetching character data.")


@bot.command()
async def outfit(ctx, *, name=None):
    api_url = 'https://api.toweroffantasy.info/outfits?lang=en&include=true'

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                outfit_data = await response.json()
                outfit_names = [outfit['name'] for outfit in outfit_data]

                if not name or name.lower() == 'list':
                    paginated_outfits = paginate(outfit_names, 10)
                    current_page = 1
                    total_pages = len(paginated_outfits)

                    await send_outfit_page(ctx, paginated_outfits, current_page,
                                           total_pages)
                else:
                    outfit = next((outfit for outfit in outfit_data
                                   if outfit['name'].lower() == name.lower()), None)
                    if outfit:
                        await send_outfit_details(ctx, outfit)
                    else:
                        await ctx.send("Outfit not found.")
            else:
                await ctx.send("Error fetching outfit data.")


async def send_outfit_details(ctx, outfit):
    embed = discord.Embed(title=outfit['name'], color=discord.Color.blue())
    embed.add_field(name="Type", value=outfit['type'], inline=False)
    embed.add_field(name="Description",
                    value=outfit['description'],
                    inline=False)
    embed.add_field(name="Source", value=outfit['source'], inline=False)

    if outfit['type'] == "Dress" or outfit['type'] == "Outfit":
        combined_image_url = await combine_images(ctx, outfit['icon'])
        embed.set_image(url=combined_image_url)
        await ctx.send(embed=embed)
    else:
        embed.set_image(url=outfit['icon'])
        await ctx.send(embed=embed)


# hate this xdd
async def combine_images(ctx, outfit_icon_url):
    response = requests.get(outfit_icon_url)
    if response.status_code == 200:
        outfit_icon = Image.open(BytesIO(response.content))
        male_icon_url = outfit_icon_url.replace("fashion_f", "fashion_m")
        response = requests.get(male_icon_url)
        if response.status_code == 200:
            male_icon = Image.open(BytesIO(response.content))

            # Calculate the dimensions of the combined image
            combined_width = outfit_icon.width + male_icon.width
            combined_height = max(outfit_icon.height, male_icon.height)

            # Create a new blank image with the calculated dimensions
            combined_image = Image.new(
                "RGBA", (combined_width, combined_height))

            # Paste the outfit and male icons onto the new image
            combined_image.paste(outfit_icon, (0, 0))
            combined_image.paste(male_icon, (outfit_icon.width, 0))

            # Save combined image locally
            combined_image_path = "combined_image.png"
            combined_image.save(combined_image_path)

            # Upload combined image to Discord
            with open(combined_image_path, "rb") as file:
                combined_image_file = discord.File(file)
                combined_message = await ctx.send(file=combined_image_file)
                await asyncio.sleep(0.1)  # Delay for 0.1 seconds
                await combined_message.delete()

            # Delete the image file from the local machine
            os.remove(combined_image_path)

            return combined_message.attachments[0].url

    return None


def paginate(items, items_per_page):
    return [
        items[i:i + items_per_page] for i in range(0, len(items), items_per_page)
    ]


async def send_outfit_page(ctx, paginated_outfits, current_page, total_pages):
    embed = discord.Embed(title="List of Outfits",
                          description=f"Page {current_page}/{total_pages}")
    embed.add_field(name="Outfit Names",
                    value="\n".join(paginated_outfits[current_page - 1]),
                    inline=False)

    message = await ctx.send(embed=embed)
    await message.add_reaction('◀️')
    await message.add_reaction('▶️')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['◀️', '▶️']

    try:
        while True:
            reaction, user = await bot.wait_for('reaction_add',
                                                timeout=60.0,
                                                check=check)

            if str(reaction.emoji) == '◀️' and current_page > 1:
                current_page -= 1
            elif str(reaction.emoji) == '▶️' and current_page < total_pages:
                current_page += 1

            await message.edit(
                embed=discord.Embed(title="List of Outfits",
                                    description=f"Page {
                                        current_page}/{total_pages}",
                                    color=discord.Color.blue()).
                add_field(name="Outfit Names",
                          value="\n".join(paginated_outfits[current_page - 1]),
                          inline=False))

            await message.remove_reaction(reaction, user)

    except asyncio.TimeoutError:
        await message.clear_reactions()


@bot.command()
async def relic(ctx, *, arg=None):
    if arg is None or arg.lower() == "list":
        await list_all_relics(ctx)
    else:
        await fetch_relic_details(ctx, arg)


async def list_all_relics(ctx):
    api_url = 'https://api.toweroffantasy.info/relics?lang=en&include=true'
    relic_data = fetch_relic_data(api_url)
    if relic_data:
        table_data = [(relic['name'], ) for relic in relic_data]
        table = tabulate(table_data, tablefmt='plain')

        MAX_MESSAGE_LENGTH = 2000 - len("List of available relics:\n``````")
        chunks = [
            table[i:i + MAX_MESSAGE_LENGTH]
            for i in range(0, len(table), MAX_MESSAGE_LENGTH)
        ]
        num_pages = len(chunks)
        current_page = 1

        def check_reaction(reaction, user):
            return user == ctx.author and str(
                reaction.emoji) in ['◀️', '▶️'] and reaction.message.id == msg.id

        while True:
            embed = discord.Embed(
                description=f"Page {
                    current_page}/{num_pages}:\n```{chunks[current_page - 1]}```"
            )
            embed.set_footer(
                text="React with ◀️ or ▶️ to navigate through pages.")

            msg = await ctx.send(embed=embed)
            if num_pages == 1:
                return

            if num_pages > 1:
                await msg.add_reaction('◀️')
                await msg.add_reaction('▶️')

                try:
                    reaction, user = await bot.wait_for('reaction_add',
                                                        timeout=60.0,
                                                        check=check_reaction)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    break

                await msg.clear_reactions()

                if str(reaction.emoji) == '▶️' and current_page < num_pages:
                    current_page += 1
                elif str(reaction.emoji) == '◀️' and current_page > 1:
                    current_page -= 1

    else:
        await ctx.send("Error fetching relic data.")


async def fetch_relic_details(ctx, relic_name):
    api_url = 'https://api.toweroffantasy.info/relics?lang=en&include=true'
    relic_data = fetch_relic_data(api_url)
    if relic_data:
        selected_relic = find_relic_by_name(relic_data, relic_name)
        if selected_relic:
            formatted_details = format_relic_details(selected_relic)
            await ctx.send(formatted_details)
        else:
            await ctx.send("Relic not found.")
    else:
        await ctx.send("Error fetching relic data.")


def fetch_relic_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching data: {response.status_code}')
        return None


def find_relic_by_name(relic_data, relic_name):
    for relic in relic_data:
        if relic['name'].lower() == relic_name.lower():
            return relic
    return None


def format_relic_details(relic_data):
    relic_name = relic_data['name']
    rarity = relic_data['rarity']
    icon_url = relic_data['icon']
    description = relic_data['description']

    # Constructing the details string
    formatted_details = f"Relic Name: {relic_name}\n"
    formatted_details += f"Rarity: {rarity}*\n"
    formatted_details += f"Description: {description}\n"
    formatted_details += f"Icon: [Click Here]({icon_url})\n"

    # Adding advancements information if present
    if 'advancements' in relic_data:
        formatted_details += "Advancements:\n"
        for advancement in relic_data['advancements']:
            formatted_details += f"- {advancement}\n"

    return formatted_details


@bot.command()
async def mount(ctx, *, arg=None):
    if arg is None or arg.lower() == "list":
        await list_all_mounts(ctx)
    else:
        await fetch_mount_details(ctx, arg)


async def list_all_mounts(ctx):
    api_url = 'https://api.toweroffantasy.info/mounts?lang=en&include=true'
    mount_data = fetch_mount_data(api_url)
    if mount_data:
        table_data = [(mount['name'], ) for mount in mount_data]
        table = tabulate(table_data, tablefmt='plain')

        MAX_MESSAGE_LENGTH = 2000 - len("List of available mounts:\n``````")
        chunks = [
            table[i:i + MAX_MESSAGE_LENGTH]
            for i in range(0, len(table), MAX_MESSAGE_LENGTH)
        ]
        num_pages = len(chunks)
        current_page = 1

        def check_reaction(reaction, user):
            return user == ctx.author and str(
                reaction.emoji) in ['◀️', '▶️'] and reaction.message.id == msg.id

        while True:
            embed = discord.Embed(
                description=f"Page {
                    current_page}/{num_pages}:\n```{chunks[current_page - 1]}```"
            )
            embed.set_footer(
                text="React with ◀️ or ▶️ to navigate through pages.")

            msg = await ctx.send(embed=embed)
            if num_pages == 1:
                return

            if num_pages > 1:
                await msg.add_reaction('◀️')
                await msg.add_reaction('▶️')

                try:
                    reaction, user = await bot.wait_for('reaction_add',
                                                        timeout=60.0,
                                                        check=check_reaction)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    break

                await msg.clear_reactions()

                if str(reaction.emoji) == '▶️' and current_page < num_pages:
                    current_page += 1
                elif str(reaction.emoji) == '◀️' and current_page > 1:
                    current_page -= 1

    else:
        await ctx.send("Error fetching mount data.")


async def fetch_mount_details(ctx, mount_name):
    api_url = 'https://api.toweroffantasy.info/mounts?lang=en&include=true'
    mount_data = fetch_mount_data(api_url)
    if mount_data:
        selected_mount = find_mount_by_name(mount_data, mount_name)
        if selected_mount:
            formatted_details = format_mount_details(selected_mount)
            await ctx.send(formatted_details)
        else:
            await ctx.send("Mount not found.")
    else:
        await ctx.send("Error fetching mount data.")


def fetch_mount_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching data: {response.status_code}')
        return None


def find_mount_by_name(mount_data, mount_name):
    for mount in mount_data:
        if mount['name'].lower() == mount_name.lower():
            return mount
    return None


def format_mount_details(mount_data):
    mount_name = mount_data['name']
    rarity = mount_data['rarity']
    icon_url = mount_data['assets']['icon']
    description = mount_data['description']

    # Constructing the details string
    formatted_details = f"Mount Name: {mount_name}\n"
    formatted_details += f"Rarity: {rarity}*\n"
    formatted_details += f"Description: {description}\n"
    formatted_details += f"Icon: [Click Here]({icon_url})\n"

    # Adding unlock items information if present
    if 'unlockItems' in mount_data:
        formatted_details += "Unlock Item:\n"
        for unlock_item in mount_data['unlockItems']:
            item_name = unlock_item['item']['name']
            formatted_details += f"- {item_name}\n"

    return formatted_details


@bot.command()
async def achievement(ctx, *, arg=None):
    if arg is None or arg.lower() == "list":
        await list_all_achievements(ctx)
    else:
        await fetch_achievement_details(ctx, arg)


async def list_all_achievements(ctx):
    api_url = 'https://api.toweroffantasy.info/achievements?lang=en&include=true'
    achievement_data = fetch_achievement_data(api_url)
    if achievement_data:
        table_data = [(achievement['name'], )
                      for achievement in achievement_data]
        table = tabulate(table_data, tablefmt='plain')

        MAX_MESSAGE_LENGTH = 2000 - \
            len("List of available achievements:\n``````")
        chunks = [
            table[i:i + MAX_MESSAGE_LENGTH]
            for i in range(0, len(table), MAX_MESSAGE_LENGTH)
        ]
        num_pages = len(chunks)
        current_page = 1

        def check_reaction(reaction, user):
            return user == ctx.author and str(
                reaction.emoji) in ['◀️', '▶️'] and reaction.message.id == msg.id

        while True:
            embed = discord.Embed(
                description=f"Page {
                    current_page}/{num_pages}:\n```{chunks[current_page - 1]}```"
            )
            embed.set_footer(
                text="React with ◀️ or ▶️ to navigate through pages.")

            msg = await ctx.send(embed=embed)
            if num_pages == 1:
                return

            if num_pages > 1:
                await msg.add_reaction('◀️')
                await msg.add_reaction('▶️')

                try:
                    reaction, user = await bot.wait_for('reaction_add',
                                                        timeout=60.0,
                                                        check=check_reaction)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    break

                await msg.clear_reactions()

                if str(reaction.emoji) == '▶️' and current_page < num_pages:
                    current_page += 1
                elif str(reaction.emoji) == '◀️' and current_page > 1:
                    current_page -= 1

    else:
        await ctx.send("Error fetching achievement data.")


async def fetch_achievement_details(ctx, achievement_name):
    api_url = 'https://api.toweroffantasy.info/achievements?lang=en&include=true'
    achievement_data = fetch_achievement_data(api_url)
    if achievement_data:
        selected_achievement = find_achievement_by_name(achievement_data,
                                                        achievement_name)
        if selected_achievement:
            formatted_details = format_achievement_details(
                selected_achievement)
            await ctx.send(formatted_details)
        else:
            await ctx.send("Achievement not found.")
    else:
        await ctx.send("Error fetching achievement data.")


def fetch_achievement_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching data: {response.status_code}')
        return None


def find_achievement_by_name(achievement_data, achievement_name):
    for achievement in achievement_data:
        if achievement['name'].lower() == achievement_name.lower():
            return achievement
    return None


def format_achievement_details(achievement_data):
    achievement_name = achievement_data['name']
    description = achievement_data['description']
    icon_url = achievement_data['icon']
    tags = ", ".join(achievement_data['tags'])
    awards = achievement_data.get('awards', [])

    # Constructing the details string
    formatted_details = f"Achievement Name: {achievement_name}\n"
    formatted_details += f"Description: {description}\n"
    formatted_details += f"Tags: {tags}\n"
    formatted_details += f"Icon: [Click Here]({icon_url})\n"

    # Adding awards information if present
    if awards:
        formatted_details += "Awards:\n"
        for award in awards:
            award_type = award['type']
            amount = award['amount']
            formatted_details += f"- {award_type}: {amount}\n"

    return formatted_details


bot.run("TOKEN")
