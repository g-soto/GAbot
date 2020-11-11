from telethon.sync import TelegramClient
from telethon import sync, events
import asyncio
import regex as re  

MSG_ROSTER = None
MSG_ATKLIST = None
MSG_DEFLIST = None

USERS_IDs = [] #list of admins

main_admin = None #id 

CLIENT = None

RE_ROSTER = re.compile( '🦅Laughing_Coffin\n'
                        '(#\d{1,2} (?P<class>(🏹|⚔️|🛡|⚗️|📦|⚒){1,2})(?P<level>\d\d) \[(⚗️|.)\] (?P<player>(\d| |\w|\')+)\n?)+')

RE_ATKLIST = re.compile( '🦅Laughing_Coffin Attack Rating\n'
                        '(#\d{1,2} .(?P<atk>\d+) (?P<player>(\d| |\w|\')+)\n?)+')

RE_DEFLIST = re.compile( '🦅Laughing_Coffin Defence Rating\n'
                        '(#\d{1,2} .(?P<def>\d+) (?P<player>(\d| |\w|\')+)\n?)+')

PLAYERS = {}

def get_range(lvl):
    if lvl < 40:
        return 0
    elif lvl < 60:
        return 1
    else:
        return 2

@events.register(events.NewMessage(outgoing=False))
async def msg_handler(event):
    try:
        global MSG_ATKLIST, MSG_DEFLIST, MSG_ROSTER, PLAYERS
        if event.from_id in USERS_IDs:
            if event.raw_text == "/roster":
                if MSG_ROSTER:
                    await event.respond(MSG_ROSTER)
                else:
                    await event.respond("send me one 🥺 pls")
            elif event.raw_text == "/atklist":
                if MSG_ATKLIST:
                    await event.respond(MSG_ATKLIST)
                else:
                    await event.respond("send me one 🥺 pls")
            elif event.raw_text == "/deflist":
                if MSG_DEFLIST:
                    await event.respond(MSG_DEFLIST)
                else:
                    await event.respond("send me one 🥺 pls")
            elif event.raw_text == "/start":
                await event.respond("/roster - give the last sended roster\n"
                                    "/atklist - give the last sended atklist\n"
                                    "/deflist - give the last sended deflist")
            elif event.fwd_from:
                if event.fwd_from.from_id == 408101137:
                    match_roster = RE_ROSTER.search(event.raw_text)
                    if match_roster:
                        PLAYERS = {}
                        for _, lvl, ply in zip(match_roster.captures('class'), map(int,match_roster.captures('level')), match_roster.captures('player')):
                            PLAYERS[ply] = [lvl, 0, 0]
                        await event.respond('Majás list update')
                    else:
                        match_atk = RE_ATKLIST.search(event.raw_text)
                        if match_atk:
                            try:
                                for ply, atk in zip(match_atk.captures('player'), map(int,match_atk.captures('atk'))):
                                    PLAYERS[ply][1] = atk
                                await event.respond('Let us breach they')
                            except KeyError as k:
                                print(PLAYERS)
                                print(k)
                                await event.respond('WROG!')
                                PLAYERS = {}
                        else:
                            match_def = RE_DEFLIST.search(event.raw_text)
                            if match_def:
                                try:
                                    for ply, d in zip(match_def.captures('player'), map(int,match_def.captures('def'))):
                                        PLAYERS[ply][2] = d
                                    await event.respond('Let us wall they')
                                except KeyError as k:
                                    print(k)
                                    await event.respond('WROG!')
                                    PLAYERS = {}

            elif event.raw_text == '/stats_per_range':
                if PLAYERS == {}:
                    await event.respond("Dumbass, first give me something to work with")
                elif not next(iter(PLAYERS.values()))[0]:
                    await event.respond("Dumbass the roster 💆🏻‍♂️")
                elif not next(iter(PLAYERS.values()))[1]:
                    await event.respond("Dumbass the atklist 💆🏻‍♂️")
                elif not next(iter(PLAYERS.values()))[2]:
                    await event.respond("Dumbass the deflist 💆🏻‍♂️")
                else:
                    spr = [[0,0, 0], [0,0, 0], [0,0,0], [0,0,0]]
                    for lvl, atk, d in PLAYERS.values():
                        spr[get_range(lvl)][0] += atk
                        spr[get_range(lvl)][1] += d
                        spr[get_range(lvl)][2] += 1

                        spr[3][0] += atk
                        spr[3][1] += d
                        spr[3][2] += 1
                    try:
                        rv =    '```LC\n'\
                                '{:<10}{:^4}|{:^4}{:^2}\n'\
                                '{:<10}{:>4}|{:<4}{:>3}\n'\
                                '{:<10}{:>4}|{:<4}{:>3}\n'\
                                '{:<10}{:>4}|{:<4}{:>3}\n\n'\
                                '_____\n'\
                                '{:<10}{:>4}|{:<4}{:>3}```'.format(  'Rangos', "⚔️", '🛡', '👥',
                                                            '20-39',    spr[0][0], spr[0][1], spr[0][2],
                                                            '40-59',    spr[1][0], spr[1][1], spr[1][2],
                                                            '60+',      spr[2][0], spr[2][1], spr[2][2],
                                                            'Total',    spr[3][0], spr[3][1], spr[3][2])
                    except Exception as ex:
                        print(ex)
                    await event.respond(rv)
        else:
            await event.respond("New phone, who dis?")
            print(event.from_id)
    except Exception as ex:
        print(ex)

@events.register(events.NewMessage(outgoing=False, chats=main_admin))
def admin(event):
    global USERS_IDs
    if event.raw_text.startswith('/new_user'):
        USERS_IDs.append(event.raw_text.split('_')[-1])

async def main():
    api_id = 8888888
    api_hash = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    
    CLIENT = TelegramClient('LCGABOT', api_id, api_hash, connection_retries=None)
    
    CLIENT.add_event_handler(msg_handler)

    CLIENT.add_event_handler(admin)

    await CLIENT.start()

    print("ON")
    await CLIENT.run_until_disconnected()


if __name__ == '__main__':
    asyncio.run(main())