"""
Created on May 6, 2021

@author: Curious Nekomimi
"""
import json
import urllib.request
import urllib.error
import os
import sys
import uuid
from time import sleep, strftime

# Global variables
aidcat_version = '0.5.7'
access_token = ''
target_username = ''
content_cache = {
    'adventures': [], 'scenarios': [], 'scenario_options': [], 'worlds': [],
    'posts': [], 'friends': [], 'followers': [], 'following': []
}
continue_text = '\nPress any key to continue...'

ccs_scenario = """
    fragment ContentCardSearchable on Scenario {
    id
    publicId
    published
    title
    description
    tags
    createdAt
    updatedAt
    memory
    authorsNote
    mode
    prompt
    quests
    worldInfo
    gameCode
    isOwner
    
    user {
        username
    }
    
    options {
        publicId
        title
        createdAt
    }
}
"""

query_scenarios = {
    "variables": {
        "input": {
            "searchTerm": "",
            "saved": False,
            "trash": False,
            "contentType": "scenario",
            "sortOrder": "createdAt",
            "offset": 0
        },
        "username": ""
    },
    "query": ("""
query ($username: String, $input: SearchInput) {
    user (username: $username) {
        id
        search(input: $input) {
            ...ContentCardSearchable
        }
    }
}
""" + ccs_scenario).replace('\t', '')
}

query_options = {
    "variables": {
        "publicId": ""
    },
    "query": ("""
query ($publicId: String) {
    scenario(publicId: $publicId) {
        ...ContentCardSearchable
    }
}
""" + ccs_scenario).replace('\t', '')
}

query_adventures = {
    "variables": {
        "input": {
            "searchTerm": "",
            "saved": False,
            "trash": False,
            "contentType": "adventure",
            "sortOrder": "createdAt",
            "offset": 0
        },
        "username": ""
    },
    "query": """
query ($username: String, $input: SearchInput) {
    user (username: $username) {
        search(input: $input) {
            ...ContentCardSearchable
        }
    }
}

fragment ContentCardSearchable on Adventure {
    id
    publicId
    title
    description
    createdAt
    updatedAt
    type
    score
    memory
    authorsNote
    worldInfo
    score
    isOwner
    
    user {
        username
    }
    
    actions {
        ...ActionSubscriptionAction
    }

    undoneWindow {
        ...ActionSubscriptionAction
    }
}

fragment ActionSubscriptionAction on Action {
    id
    text
    type
    createdAt
}
""".replace('\t', '')
}

query_posts = {
    "variables": {
        "input": {
            "searchTerm": "",
            "saved": False,
            "trash": False,
            "contentType": "post",
            "sortOrder": "createdAt",
            "offset": 0
        },
        "username": ""
    },
    "query": """
query ($username: String, $input: SearchInput) {
    user (username: $username) {
        id search(input: $input) {
            ...ContentListSearchable __typename
        }
        __typename
    }
}
fragment ContentListSearchable on Searchable {
    ...ContentCardSearchable __typename
}
fragment ContentCardSearchable on Searchable {
    id publicId userId title description tags createdAt publishedAt updatedAt deletedAt published isOwner user {
        ...UserTitleUser __typename
    }
    ...on Adventure {
        actionCount userJoined scenario {
            id title publicId published deletedAt __typename
        }
        __typename
    }
    ...ContentOptionsSearchable...ContentStatsCommentable...ContentStatsVotable...DeleteButtonSearchable...SaveButtonSavable __typename
}
fragment ContentOptionsSearchable on Searchable {
    id publicId published isOwner tags title userId...on Savable {
        isSaved __typename
    }
    ...on Adventure {
        userJoined __typename
    }
    __typename
}
fragment ContentStatsCommentable on Commentable {
    ...CommentButtonCommentable __typename
}
fragment CommentButtonCommentable on Commentable {
    id publicId allowComments totalComments __typename
}
fragment ContentStatsVotable on Votable {
    ...VoteButtonVotable __typename
}
fragment VoteButtonVotable on Votable {
    id userVote totalUpvotes __typename
}
fragment DeleteButtonSearchable on Searchable {
    id publicId published __typename
}
fragment SaveButtonSavable on Savable {
    id isSaved __typename
}
fragment UserTitleUser on User {
    id username icon...UserAvatarUser __typename
}
fragment UserAvatarUser on User {
    id username avatar __typename
}""".replace('\t', '')
}

query_worlds = {
    "query": """
query {
    worlds {
        id
        worldName
        description
        userCreatedWorld
        isOwner
        ...WorldSummaryWorld
        worldGeneration
        __typename
    }
}
fragment WorldSummaryWorld on World {
    id
    tags
    genres
    hideWorldInfo
    nsfw
    ...WorldImageWorld
    __typename
}
fragment WorldImageWorld on World {
    id
    image
    __typename
}
""".replace('\t', '')
}

query_social = {
    "variables": {
        "username": ""
    },
    'query': """
query($username: String) {
    user(username: $username) {
        id friends {
            ...UserTitleUser
            ...FriendButtonUser
            __typename
        }
        followers {
            ...UserTitleUser
            ...FollowButtonUser
            __typename
        }
        following {
            ...UserTitleUser
            ...FollowButtonUser
            __typename
        }
        __typename
    }
}
fragment FollowButtonUser on User {
    isCurrentUser
    isFollowedByCurrentUser
    __typename
}
fragment FriendButtonUser on User {
    id
    username
    isCurrentUser
    friendedCurrentUser
    friendedByCurrentUser
    __typename
}
fragment UserTitleUser on User {
    id
    username
    icon
    ...UserAvatarUser
    __typename
}
fragment UserAvatarUser on User {
    id
    username
    avatar
    __typename
}""".replace('\t', '')
}

screen_flash = """
 ▄▄▄       ██▓   ▓█████▄  █    ██  ███▄    █   ▄████ ▓█████  ▒█████   ███▄    █
▒████▄    ▓██▒   ▒██▀ ██▌ ██  ▓██▒ ██ ▀█   █  ██▒ ▀█▒▓█   ▀ ▒██▒  ██▒ ██ ▀█   █
▒██  ▀█▄  ▒██▒   ░██   █▌▓██  ▒██░▓██  ▀█ ██▒▒██░▄▄▄░▒███   ▒██░  ██▒▓██  ▀█ ██▒
░██▄▄▄▄██ ░██░   ░▓█▄   ▌▓▓█  ░██░▓██▒  ▐▌██▒░▓█  ██▓▒▓█  ▄ ▒██   ██░▓██▒  ▐▌██▒
 ▓█   ▓██▒░██░   ░▒████▓ ▒▒█████▓ ▒██░   ▓██░░▒▓███▀▒░▒████▒░ ████▓▒░▒██░   ▓██░
 ▒▒   ▓▒█░░▓      ▒▒▓  ▒ ░▒▓▒ ▒ ▒ ░ ▒░   ▒ ▒  ░▒   ▒ ░░ ▒░ ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒

     ██████╗ ██████╗ ███╗   ██╗████████╗███████╗███╗   ██╗████████╗
    ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔════╝████╗  ██║╚══██╔══╝
    ██║     ██║   ██║██╔██╗ ██║   ██║   █████╗  ██╔██╗ ██║   ██║
    ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██║╚██╗██║   ██║
    ╚██████╗╚██████╔╝██║ ╚████║   ██║   ███████╗██║ ╚████║   ██║
     ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝   ╚═╝
             █████╗ ██████╗  ██████╗██╗  ██╗██╗██╗   ██╗███████╗
            ██╔══██╗██╔══██╗██╔════╝██║  ██║██║██║   ██║██╔════╝
            ███████║██████╔╝██║     ███████║██║██║   ██║█████╗
            ██╔══██║██╔══██╗██║     ██╔══██║██║╚██╗ ██╔╝██╔══╝
            ██║  ██║██║  ██║╚██████╗██║  ██║██║ ╚████╔╝ ███████╗
            ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝
                    ████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗██╗████████╗
                    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝██║╚══██╔══╝
                       ██║   ██║   ██║██║   ██║██║     █████╔╝ ██║   ██║
                       ██║   ██║   ██║██║   ██║██║     ██╔═██╗ ██║   ██║
                       ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗██║   ██║
                       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝

AI Dungeon Content Archive Toolkit (AID CAT) v"""[1:]+aidcat_version+""" © 2021 Curious Nekomimi."""

# The copyright notice is intended to annoy the people who don't like copyright notices. >:D
screen_copyright = """
MIT License

Copyright (c) 2021 CuriousNekomimi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""[1:]

# Information to show on program close.
screen_quit = """
████████╗██╗  ██╗ █████╗ ███╗   ██╗██╗  ██╗    ██╗   ██╗ ██████╗ ██╗   ██╗██╗
╚══██╔══╝██║  ██║██╔══██╗████╗  ██║██║ ██╔╝    ╚██╗ ██╔╝██╔═══██╗██║   ██║██║
   ██║   ███████║███████║██╔██╗ ██║█████╔╝      ╚████╔╝ ██║   ██║██║   ██║██║
   ██║   ██╔══██║██╔══██║██║╚██╗██║██╔═██╗       ╚██╔╝  ██║   ██║██║   ██║╚═╝
   ██║   ██║  ██║██║  ██║██║ ╚████║██║  ██╗       ██║   ╚██████╔╝╚██████╔╝██╗
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝       ╚═╝    ╚═════╝  ╚═════╝ ╚═╝

...for using the AI Dungeon Content Archive Toolkit (AID CAT) v"""[1:]+aidcat_version+"""!

...to an anonymous anon who wishes to remain anonymous for:
    The original script and giving me the inspiration to create AID CAT.

...to Eta for:
    Helping me with code refactoring and suggestions that improved efficiency
    and neatness. *happy perfectionist noises*

Github repository:
    https://github.com/CuriousNekomimi/AIDCAT

Report issues here:
    https://github.com/CuriousNekomimi/AIDCAT/issues

License:
    https://github.com/CuriousNekomimi/AIDCAT/blob/main/LICENSE"""

# *hugs* Nya!
screen_surprise = r"""
                                   ,╓▄▄▄▄▄▄▄▄▄▄▄▄▄╓,         ,╓▄▄▄▒▓▓▓▓▓▓▓▓▓▄,
          ╓▒████▓▓▓▄▄,      ╓▄▄▓▓██████▀▀▀▀▀▀▀█████████▓▓▒▓████▀▀▀▀▀╠╠╠Ñ╠╠▀███
         #██▒#║╠╠╠▀▀▀██▓▄▓████▀▀▀╠Ñ╚╡╡╠┤┤┤┤┤┤┤╚╙╚║▒▒▒▒▒▒▀▀▀ÑWMMM╠╠┤┤┤┤┤┤┤║╢╠██
        ▒██┤╠╠╠╠╠╠╠╠╠║╠▀▀▀▀Ñ╡┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤││││∩, └╙▒▒╠║╠╡┤┤┤┤┤┤┤┤┤┤┤#║╠║╠╫█▌
       ╫██┤┤┤┤┤┤╠╠║║║╠╠╡┤┤┤┤┤┤┤╠║║║╢▒▒▒▒▒▒╡┤│││]||∩{∩∩││╚▒▒╡┤┤┤┤┤┤┤┤┤┤║║╠╠╠╠║█▌
      (██░┤┤┤┤┤┤┤┤┤╚╡┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤╚╠╠▒▒▒▒▒░W││∩||││WM┤┤╠║▒┤┤┤┤┤┤┤#║║╠║║╠╠║█▌
      ║█▌│┤┤┤┤┤┤┤╡┤┤┤┤┤┤┤┤╠╡┤┤┤┤┤┤┤┤┤┤┤┤┤╙╙╠▒▒▒░┤W│W┤┤┤┤┤┤┤┤╠║╠┤┤┤┤║▒"└"  └|║█▌
     (██▌│┤┤┤┤║╠╠┤┤┤┤┤┤┤┤┤┤╠╠┤┤┤┤┤┤┤┤││││││││┤╠▒▒╡┤┤┤┤┤┤┤┤┤┤┤┤╚║╡┤║▒      │#▓█▌
     ╫█▀▒▒┤┤▒╠┤┤#║╠┤┤┤┤┤┤┤┤┤┤╠╡┤┤┤┤┤┤│┤││││││┤┤┤╡╠║╡┤┤┤┤┤┤┤┤┤┤┤┤╠╢╢⌐     ╔╠║██
     ╫█C╢▒▒▒┤╠┤#║▒╡┤┤┤┤┤┤┤┤┤┤┤│╠┤│││||│││┤W││┤┤┤┤┤┤╠║╡┤╠╠╠┤┤┤╠╡┤┤╠║»     `╚██
     ▐█▒▐▓▒│┤┤┤║║▒╡┤│││┤┤││││││││╚MG]]│││┤┤┤┤┤┤┤┤┤┤┤╠║╡┤╠╠╠╠╠╠╠╠╡┤┤╠░,    ╓█▌
     ║█▒▒▒WM└││║╠║▒┤┤∩││┤G│]||│||││╙║M│┤┤┤┤┤┤┤┤┤┤╠╠┤┤┤║▒┤╠╠╠╠╠╠╠╠╠╡┤╠░    ║██▄
      ▀██║╠∩ ││║╠╠▒╡┤G]│┤┤G∩]|││⌠│┤┤┤┤╠╠╠┤┤┤┤┤┤┤┤┤┤╠╠╠╠║▒┤┤╠╠╠╠╠╠╠╠╠┤╠╠, ╔#╚▀██▄
     (██╠║╡Γ{││╠╠╠╠▒╡┤∩││┤┤M∩││W┤┤┤┤┤┤┤┤║▒▓▓▓▓▓▓╢║┤┤┤┤┤╠║▒┤┤╠╠╠╠╠╠╠╠╠╡╠║╓║║▒░╚██
     ║█▒▒▒╡┤MW┤┤║╠╠╠║╡┤││││┤┤┤┤┤┤┤┤┤┤┤#╫█▀▀Ñ╡╠╠╠┤┤┤┤┤┤┤┤┤║▒┤┤┤╠╠╠╠┤┤┤╠║╠║▒╠║║╠┤▀
    (██▒▒║╠╠╠╠┤┤┤║╠╠╠║╠┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤╠╠╠╠╠┤┤┤┤W║╡┤┤╠╠┤┤┤┤┤┤╠║╠║▒╠╠║║╡
    ║██▒▒║╙y╓╓└╙┤╠║╠╠╠║▒▒┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤╠╠╠╠║▒╡┤┤║╠╡┤┤┤┤┤╠║╡╠▒╠╠║║
   (██▓▒╙╙y║▒▓███▒▒║║▒███╜╠┤┤┤┤┤┤┤┤┤┤┤┤┤┤┤╠╡╡╡╡#║▒▒▓▓▒▒▒▒Ñ╙║╡││╠╠║╡┤┤┤┤┤║▒╡╠╢╠╠╠
   (██▒M(║║▒██╙ ╙▀████▒╠M └┘╚╠┤┤┤┤┤┤┤┤┤┤┤┤┤┤║▓███▀█████▒╙  ▐╠∩│║╠╠║╡┤┤┤┤╠║▒╠╠▒╠╠
   ╞██▒▒╓│▒██∩      ╙▀██▒∩    └╚║╡┤┤║║╠╚╚║║║║▒██▒▓▀▀╙└     │╠│┤║▒╠║╠┤┤┤┤╠║▒╠╠║▒║
   (██▒▒║▓██∩          ▀██▄       └╙╚╚║░»    ║▒▒╙.         ║╠┤║╢▒╠║╚└│││╠║▒▒╠║▒╠
██████▒║║██M¡,          └▀██▓▄╓              └"           (╠#╚│╢▒▒╚,{│││W║▒╚│║▒╠
╙╙╙▀▀▀████▀"                └▀██▓╓                       (╚╙└y║▒▒╚]⌠││││║▒┤│#╢║╠
        └*                      ▀█▓»                       |#▒▒╠┤┤WW┤┤┤╠┤##▒╠┤╠╠
    |                             ╙█▒,        .,         ,#╢╠╡┤┤┤┤┤┤╠▒▒▒╢▒▒▒▒┤╠╠
                                .#▓▒▀█▓▄      ╙∩       '╚║▒▒▒▒▒▒▒╢╢▒║║║║║▒╠║▒╠╠╠
                                ║▓█▀  ╙██▒M*          |(╔║╚┤┤╠╠╠╠╠║╠╠╠╠┤┤┤╠▒▒┤╠╠
                                '╚└     ▀█▒         {|{║╠▒▒▓█▓▓▓▓▒╡┤┤┤┤┤┤║╢▒│┤╠╠
                               ,        |║█N    ,{|||[║▓█▀╙└,,└└╙▀█▓▒┤#║▒▒▒╚││┤┤
                              └└"     || ║██▄▒▓▓███▓▒█▀╙|||||||{«,|▀█▓▒▒▒▒╚||││║
                ,▄▓▓▓▓▒▒░⌐          ||╓▄▒▓█▀▀╙╙└..└╙▀█▒∩||⌠∩||||||, ║██▒╜└  |╔▒╠
 |             (╫███▀▀╙└         ,|╓#▓▓▀╙          ,(██░∩|||||||||||,╙██C  ╓▒╠╠║
m ,         .,,              ,|▄▄▓██████▓▓▓▒▄▄▄,,,|╓▓█▀∩||||||||||||||╙██»#▒▒║╠╠
█∩ |, ,╔#M╢▓████▓▓▓▓▓▄▄,||,╓▒███▀▀╙╙└└└└╙╙╙▀▀▀██████▀╙|||||||||||||||│∩║██▒▒╠╚╠╠
█▓∩   ..,(▒█▌  └M  └╙▀▀██████╩.    ,||||||||||||└╙╙╙∩||||||||||||||{│││∩██▓╚│││╠
▀██▒▄  |#▓██▒,         │∩  ,│∩  ,|||||||||||||||||||└╠MW∩|||||]{{⌠│││││∩╙██M|│││"""[1:]

# Headers for menus.
menu_header = '\nAvailable operations:\n'

menu_header_main = """
███╗   ███╗ █████╗ ██╗███╗   ██╗    ███╗   ███╗███████╗███╗   ██╗██╗   ██╗
████╗ ████║██╔══██╗██║████╗  ██║    ████╗ ████║██╔════╝████╗  ██║██║   ██║
██╔████╔██║███████║██║██╔██╗ ██║    ██╔████╔██║█████╗  ██╔██╗ ██║██║   ██║
██║╚██╔╝██║██╔══██║██║██║╚██╗██║    ██║╚██╔╝██║██╔══╝  ██║╚██╗██║██║   ██║
██║ ╚═╝ ██║██║  ██║██║██║ ╚████║    ██║ ╚═╝ ██║███████╗██║ ╚████║╚██████╔╝
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝"""[1:]

menu_header_your_content = """
███╗   ███╗██╗   ██╗    ███████╗████████╗██╗   ██╗███████╗███████╗
████╗ ████║╚██╗ ██╔╝    ██╔════╝╚══██╔══╝██║   ██║██╔════╝██╔════╝
██╔████╔██║ ╚████╔╝     ███████╗   ██║   ██║   ██║█████╗  █████╗
██║╚██╔╝██║  ╚██╔╝      ╚════██║   ██║   ██║   ██║██╔══╝  ██╔══╝
██║ ╚═╝ ██║   ██║       ███████║   ██║   ╚██████╔╝██║     ██║
╚═╝     ╚═╝   ╚═╝       ╚══════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝"""[1:]

menu_header_our_content = """
 ██████╗ ██╗   ██╗██████╗     ███████╗████████╗██╗   ██╗███████╗███████╗
██╔═══██╗██║   ██║██╔══██╗    ██╔════╝╚══██╔══╝██║   ██║██╔════╝██╔════╝
██║   ██║██║   ██║██████╔╝    ███████╗   ██║   ██║   ██║█████╗  █████╗
██║   ██║██║   ██║██╔══██╗    ╚════██║   ██║   ██║   ██║██╔══╝  ██╔══╝
╚██████╔╝╚██████╔╝██║  ██║    ███████║   ██║   ╚██████╔╝██║     ██║
 ╚═════╝  ╚═════╝ ╚═╝  ╚═╝    ╚══════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝"""[1:]

menu_header_auth_menu = """
 █████╗ ██╗   ██╗████████╗██╗  ██╗    ███╗   ███╗███████╗███╗   ██╗██╗   ██╗
██╔══██╗██║   ██║╚══██╔══╝██║  ██║    ████╗ ████║██╔════╝████╗  ██║██║   ██║
███████║██║   ██║   ██║   ███████║    ██╔████╔██║█████╗  ██╔██╗ ██║██║   ██║
██╔══██║██║   ██║   ██║   ██╔══██║    ██║╚██╔╝██║██╔══╝  ██║╚██╗██║██║   ██║
██║  ██║╚██████╔╝   ██║   ██║  ██║    ██║ ╚═╝ ██║███████╗██║ ╚████║╚██████╔╝
╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝    ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝"""[1:]


# Tries to clear the user's screen. Skips on exception.
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# Gets the user's x-access-token. Tries to load from file first.
# REFACTOR with UUID
def get_token():
    global access_token
    try:
        clear_screen()
        if access_token == '':
            print('Getting from file')
            with open('access_token.txt', 'r') as f:
                access_token = f.read().strip()
        try:
            uuid.UUID(access_token)
        except:
            print('Invalid token detected. Should be a valid UUID.')
            set_token()
    except:
        print('Saved token not found...')
        set_token()


# Prompts the user for an x-access-token and stores it globally.
# REFACTOR with UUID
def set_token():
    global access_token
    try:
        clear_screen()
        input_token = input('Please enter your access token (UUID with hyphens): ')
        uuid.UUID(input_token)
        access_token = input_token
        if input('Would you like to save your token for later? (y/n): ').lower().strip()[:1] == 'y':
            save_token()
    except:
        print('Invalid token detected. Should be a valid UUID. Please try again.')
        input(continue_text)


def save_token():
    global access_token
    try:
        clear_screen()
        with open('access_token.txt', 'w') as f:
            f.write(access_token)
        print("Token saved to 'access_token.txt'.")
    except:
        print('Something went wrong saving your access token.')
    input(continue_text)


def auth_user():
    while access_token == '':
        try:
            get_token()
        except:
            set_token()


def get_scenarios(target_user='', is_saved=False):
    global content_cache
    global query_scenarios
    content_cache['scenarios'] = []
    content_cache['scenario_options'] = []
    if not is_saved:
        print('Getting scenarios...')
    else:
        print('Getting saved scenarios...')
    query_scenarios['variables']['input']['saved'] = is_saved
    query_scenarios['variables']['input']['offset'] = 0
    query_scenarios['variables']['username'] = target_user
    while True:
        req = urllib.request.Request('https://api.aidungeon.io/graphql',
                                     headers={"x-access-token": access_token, "content-type": "application/json"})
        res = None
        
        try:
            res = urllib.request.urlopen(req, data=json.dumps(query_scenarios).encode('utf8'))
        except urllib.error.HTTPError as e:
            print(e)
            print(e.read())
            break
        
        result = json.loads(res.read())
        
        if 'data' in result:
            if result['data']['user']['search']:
                content_cache['scenarios'] += result['data']['user']['search']
                print('Got %d scenarios...' % len(content_cache['scenarios']))
                query_scenarios['variables']['input']['offset'] = len(content_cache['scenarios'])
                for scenario in result['data']['user']['search']:
                    if 'options' in scenario and type(scenario['options']) is list:
                        for option in scenario['options']:
                            content_cache['scenario_options'].append(option['publicId'])
            else:
                print('No more scenarios found.')
                break
        else:
            print('There was no data...')
            break
    get_subscenarios()
    if content_cache['scenarios']:
        save_json(target_user, is_saved, 'scenarios')
    else:
        print('No scenarios to save!')


def get_subscenarios():
    global content_cache
    global query_options
    for pubid in content_cache['scenario_options']:
        print('Getting subscenario %s...' % pubid)
        query_options['variables']['publicId'] = pubid
        req = urllib.request.Request('https://api.aidungeon.io/graphql',
                                     headers={"x-access-token": access_token, "content-type": "application/json"})
        res = None
        
        try:
            res = urllib.request.urlopen(req, data=json.dumps(query_options).encode('utf8'))
        except urllib.error.HTTPError as e:
            print(e)
            print(e.read())
            break
        
        result = json.load(res)
        
        if 'data' in result and 'scenario' in result['data']:
            result['data']['scenario']['isOption'] = True
            content_cache['scenarios'].append(result['data']['scenario'])
            if 'options' in result['data']['scenario'] and type(result['data']['scenario']['options']) is list:
                for option in result['data']['scenario']['options']:
                    content_cache['scenario_options'].append(option['publicId'])
        else:
            print('There was no data...')
    content_cache['scenario_options'] = []


def get_adventures(target_user='', is_saved=False):
    global content_cache
    global query_adventures
    content_cache['adventures'] = []
    if not is_saved:
        print('Getting adventures...')
    else:
        print('Getting saved adventures...')
    query_adventures['variables']['input']['saved'] = is_saved
    query_adventures['variables']['input']['offset'] = 0
    query_adventures['variables']['username'] = target_user
    while True:
        req = urllib.request.Request('https://api.aidungeon.io/graphql',
                                     headers={"x-access-token": access_token, "content-type": "application/json"})
        res = None
        
        try:
            res = urllib.request.urlopen(req, data=json.dumps(query_adventures).encode('utf8'))
        except urllib.error.HTTPError as e:
            print(e)
            print(e.read())
            break
        
        result = json.loads(res.read())
        
        if 'data' in result:
            if result['data']['user']['search']:
                content_cache['adventures'] += result['data']['user']['search']
                print('Got %d adventures...' % len(content_cache['adventures']))
                query_adventures['variables']['input']['offset'] = len(content_cache['adventures'])
            else:
                print('No more adventures found.')
                break
        else:
            print('There was no data...')
            break
    if content_cache['adventures']:
        save_json(target_user, is_saved, 'adventures')
    else:
        print('No adventures to save!')


def get_posts(target_user='', is_saved=False):
    global content_cache
    global query_posts
    content_cache['posts'] = []
    if not is_saved:
        print('Getting posts...')
    else:
        print('Getting saved posts...')
    query_posts['variables']['input']['saved'] = is_saved
    query_posts['variables']['input']['offset'] = 0
    query_posts['variables']['username'] = target_user
    while True:
        req = urllib.request.Request('https://api.aidungeon.io/graphql',
                                     headers={"x-access-token": access_token, "content-type": "application/json"})
        res = None
        
        try:
            res = urllib.request.urlopen(req, data=json.dumps(query_posts).encode('utf8'))
        except urllib.error.HTTPError as e:
            print(e)
            print(e.read())
            break
        
        result = json.loads(res.read())
        
        if 'data' in result:
            if result['data']['user']['search']:
                content_cache['posts'] += result['data']['user']['search']
                print('Got %d posts...' % len(content_cache['posts']))
                query_posts['variables']['input']['offset'] = len(content_cache['posts'])
            else:
                print('No more posts found.')
                break
        else:
            print('There was no data...')
            break
    
    if content_cache['posts']:
        save_json(target_user, is_saved, 'posts')
    else:
        print('No posts to save!')


def get_worlds():
    global content_cache
    global query_worlds
    content_cache['worlds'] = []
    print('Getting worlds...')
    req = urllib.request.Request('https://api.aidungeon.io/graphql',
                                 headers={"x-access-token": access_token, "content-type": "application/json"})
    res = None
    
    try:
        res = urllib.request.urlopen(req, data=json.dumps(query_worlds).encode('utf8'))
    except urllib.error.HTTPError as e:
        print(e)
        print(e.read())
    
    result = json.loads(res.read())
    
    if 'data' in result:
        content_cache['worlds'] = result['data']['worlds']
    else:
        print('There was no data...')
    
    if content_cache['worlds']:
        save_json('', False, 'worlds')
    else:
        print('No worlds to save!')


def get_social(target_user=''):
    global content_cache
    global query_social
    content_cache['friends'] = []
    content_cache['followers'] = []
    content_cache['following'] = []
    print('Getting friends, followers, and following...')
    query_social['variables']['username'] = target_user
    req = urllib.request.Request('https://api.aidungeon.io/graphql',
                                 headers={"x-access-token": access_token, "content-type": "application/json"})
    res = None
    
    try:
        res = urllib.request.urlopen(req, data=json.dumps(query_social).encode('utf8'))
    except urllib.error.HTTPError as e:
        print(e)
        print(e.read())
    
    result = json.loads(res.read())
    
    if 'data' in result:
        if 'friends' in result['data']['user']:
            content_cache['friends'] = result['data']['user']['friends']
        if 'followers' in result['data']['user']:
            content_cache['followers'] = result['data']['user']['followers']
        if 'following' in result['data']['user']:
            content_cache['following'] = result['data']['user']['following']
    else:
        print('There was no data...')
    
    if content_cache['friends']:
        save_json(target_user, False, 'friends')
    else:
        print('No friends to save!')
    
    if content_cache['followers']:
        save_json(target_user, False, 'followers')
    else:
        print('No followers to save!')
    
    if content_cache['following']:
        save_json(target_user, False, 'following')
    else:
        print('No following to save!')


# Close the program.
def program_quit():
    clear_screen()
    print(screen_quit)
    input(continue_text)
    clear_screen()
    print('SURPRISE HUG!')
    sleep(1.5)
    for line in screen_surprise.split('\n'):
        print(line)
        sleep(0.01)
    input('\nPress any key to nya...')
    sys.exit()


# Expects a username, whether or not the data is from a bookmark
def save_json(target_user='', is_saved=False, content_type=''):
    # Current local time in ISO 8601 format.
    time_now = strftime('%Y%m%dT%H%M%S')
    file_name = ''
    if target_user == '':
        target_user = 'your'
    if not is_saved:
        file_name = f'{target_user}_{content_type}_{time_now}.json'
    else:
        file_name = f'{target_user}_saved_{content_type}_{time_now}.json'
    
    with open(file_name, 'x', encoding='utf8') as f:
        json.dump(content_cache[content_type], f, ensure_ascii=False, indent=8)
    print(f'Saved to {file_name}.')


# Authorization menu choices.
auth_menu_choices = [
    '[1] Change your access token.',
    "[2] Save your access token (saves token to 'access_token.txt')",
    "[3] Wipe your access token (deletes 'access_token.txt').",
    '[4] View your token. WARNING! NEVER LET ANYONE SEE YOUR TOKEN!',
    '[0] Return to main menu. [Default].\n'
]


# The authorization menu.
def auth_menu():
    while True:
        # Set the default menu choice.
        choice = 0
        clear_screen()
        print(menu_header_auth_menu, menu_header, *auth_menu_choices, sep='\n')
        try:
            choice = int(input(f'Operation [0-{len(auth_menu_choices) - 1}]: '))
        except:
            pass
        
        # Return to the main menu.
        if choice == 0:
            break
        
        # Set access access_token.
        elif choice == 1:
            set_token()
        
        # Save access token to file.
        elif choice == 2:
            save_token()
        
        # Wipe access access_token.
        elif choice == 3:
            clear_screen()
            if os.path.exists("access_token.txt"):
                os.remove("access_token.txt")
                print('Deleted access_token.txt.')
            else:
                print("No access_token.txt exists.")
            input(continue_text)
       
        elif choice == 4:
            clear_screen()
            print('WARNING! Never share this token! It grants full control of your AI Dungeon account!',
                  f'\nStored x-access-token: {access_token}')
            input(continue_text)
            
        else:
            print(f'ERR: Input must be an integer from 0 to {len(auth_menu_choices) - 1}. Try again!')
            sleep(1)


your_content_menu_choices = [
    '[1] Download your scenarios.',
    '[2] Download your adventures.',
    '[3] Download your posts.',
    '[4] Download your worlds (includes purchased worlds).',
    '[5] Download your friends, followers, and following.',
    '[6] Download your saves (bookmarks).',
    '[7] Download all of the above.',
    '[0] Return to main menu. [Default]\n'
]


# User content download menu.
def your_content_menu():
    while True:
        # Set the default menu choice.
        choice = 0
        clear_screen()
        print(menu_header_your_content, menu_header, *your_content_menu_choices, sep='\n')
        try:
            choice = int(input(f'Operation [0-{len(your_content_menu_choices) - 1}]: '))
        except:
            pass
        
        # Return to the main menu.
        if choice == 0:
            break
        
        elif choice == 1:
            clear_screen()
            try:
                get_scenarios()
            except:
                print('An error occurred saving your scenarios.')
            input(continue_text)
        
        elif choice == 2:
            clear_screen()
            try:
                get_adventures()
            except:
                print('An error occurred saving your adventures.')
            input(continue_text)
        
        elif choice == 3:
            clear_screen()
            try:
                get_posts()
            except:
                print('An error occurred saving your posts.')
            input(continue_text)
        
        elif choice == 4:
            clear_screen()
            try:
                get_worlds()
            except:
                print('An error occurred saving your worlds.')
            input(continue_text)
        
        elif choice == 5:
            clear_screen()
            try:
                get_social()
            except:
                print('An error occurred saving your friends, followers, and following.')
            input(continue_text)
        
        elif choice == 6:
            clear_screen()
            try:
                get_scenarios('', True)
                get_adventures('', True)
                get_posts('', True)
            except:
                print('An error occurred saving your bookmarks.')
            input(continue_text)
        
        elif choice == 7:
            clear_screen()
            try:
                get_scenarios()
            except:
                print('An error occurred saving your scenarios.')
            
            try:
                get_adventures()
            except:
                print('An error occurred saving your adventures.')
            
            try:
                get_posts()
            except:
                print('An error occurred saving your posts.')
            
            try:
                get_worlds()
            except:
                print('An error occurred saving your worlds.')
            
            try:
                get_social()
            except:
                print('An error occurred saving your friends, followers, and following.')
            
            try:
                get_scenarios('', True)
                get_adventures('', True)
                get_posts('', True)
            except:
                print('An error occurred saving your bookmarks.')
            input(continue_text)
        
        else:
            print(f'ERR: Input must be an integer from 0 to {len(your_content_menu_choices) - 1}. Try again!')
            sleep(1)


def our_content_menu_choices():
    return [
        f"[1] Download {target_username}'s published scenarios.",
        f"[2] Download {target_username}'s published adventures.",
        f"[3] Download {target_username}'s published posts.",
        f"[4] Download {target_username}'s friends, followers, and following.",
        '[5] Download all of the above.',
        '[6] Change target user.',
        '[0] Return to main menu. [Default]\n'
    ]


# Other user content download menu
def our_content_menu():
    global target_username
    while len(target_username) <= 0:
        clear_screen()
        target_username = input("Target user's AI Dungeon username: ")
    while True:
        # Set the default menu choice.
        choice = 0
        clear_screen()
        print(menu_header_our_content, menu_header, *our_content_menu_choices(), sep='\n')
        try:
            choice = int(input(f'Operation [0-{len(our_content_menu_choices()) - 1}]: '))
        except:
            pass
        
        # Return to the main menu.
        if choice == 0:
            break
        
        elif choice == 1:
            clear_screen()
            try:
                get_scenarios(target_username)
            except:
                pass
            input(continue_text)
        
        elif choice == 2:
            clear_screen()
            try:
                get_adventures(target_username)
            
            except:
                pass
            input(continue_text)
        
        elif choice == 3:
            clear_screen()
            try:
                get_posts(target_username)
            except:
                pass
            input(continue_text)
        
        elif choice == 4:
            clear_screen()
            try:
                get_social(target_username)
            except:
                pass
            input(continue_text)
        
        elif choice == 5:
            clear_screen()
            
            try:
                get_scenarios(target_username)
            except:
                print(fr"An error occurred saving {target_username}'s scenarios.")
            
            try:
                get_adventures(target_username)
            except:
                print(fr"An error occurred saving {target_username}'s adventures.")
            
            try:
                get_posts(target_username)
            except:
                print(fr"An error occurred saving {target_username}'s posts.")
            
            try:
                get_social(target_username)
            except:
                print(fr"An error occurred saving {target_username}'s friends, followers, and following.")
            input(continue_text)
        
        elif choice == 6:
            clear_screen()
            try:
                target_username = input("Target user's AI Dungeon username: ")
            except:
                print('An error occurred setting the target user.')
            input(continue_text)
        
        else:
            print(f'ERR: Input must be an integer from 0 to {len(our_content_menu_choices()) - 1}. Try again!')
            sleep(1)


# Main menu choices.
main_menu_choices = [
    '[1] Download your saved content. [Default]',
    "[2] Download another user's published content.",
    '[3] Change, wipe, or view your access token.',
    '[0] Quit program.\n'
]


# The main menu.
def main_menu():
    while True:
        # Set the default menu choice.
        choice = 1
        clear_screen()
        print(menu_header_main, menu_header, *main_menu_choices, sep='\n')
        try:
            choice = int(input(f'Operation [0-{len(main_menu_choices) - 1}]: '))
        except:
            pass
        if choice == 0:
            program_quit()
        elif choice == 1:
            your_content_menu()
        elif choice == 2:
            our_content_menu()
        elif choice == 3:
            auth_menu()
        else:
            print(f'ERR: Input must be an integer from 0 to {len(main_menu_choices) - 1}. Try again!')
            sleep(1)


def main():
    clear_screen()
    print(screen_flash)
    input(continue_text)
    clear_screen()
    print(screen_copyright)
    input(continue_text)
    auth_user()
    main_menu()


if __name__ == '__main__':
    main()
