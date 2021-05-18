'''
Created on May 6, 2021

@author: Curious Nekomimi
'''
import json
import requests
import os
import uuid
from time import strftime
from json_to_html import to_html

aidcat_version = '0.6.4'


class User():
    def __init__(self, user=''):
        self.user = user
        self.access_token = None
        self.content_cache = {
            'adventures': [], 'scenarios': [], 'scenario_options': [], 'worlds': [],
            'posts': [], 'friends': [], 'followers': [], 'following': []
        }

        self.ccs_scenario = '''
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
        '''

        self.scenarios_query_string = ('''
        query ($username: String, $input: SearchInput) {
            user (username: $username) {
                id
                search(input: $input) {
                    ...ContentCardSearchable
                }
            }
        }
        ''' + self.ccs_scenario)

        self.options_query_string = ('''
        query ($publicId: String) {
            scenario(publicId: $publicId) {
                ...ContentCardSearchable
            }
        }
        ''' + self.ccs_scenario)

        self.adventures_query_string = '''
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
            userId
            title
            description
            tags
            createdAt
            publishedAt
            updatedAt
            deletedAt
            published
            isOwner
            type
            thirdPerson
            score
            memory
            authorsNote
            worldInfo
            score
            isOwner
            user {
                id
                username
                icon
                avatar
                __typename
            }
            actionCount
            userJoined
            scenario {
                id
                title
                publicId
                published
                deletedAt
                __typename
            }
            __typename
            isSaved
            allowComments
            totalComments
            userVote
            totalUpvotes
            allPlayers {
                id
                userId
                characterName
                __typename
            }
            actionWindow {
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
            adventureId
            decisionId
            undoneAt
            deletedAt
            createdAt
            __typename
        }
        '''

        self.posts_query_string = '''
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
        }'''

        self.worlds_query_string = '''
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
        '''

        self.social_query_string = '''
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
        }'''
        self.query_scenarios = {
            "variables": {
                "input": {
                    "searchTerm": "",
                    "saved": False,
                    "trash": False,
                    "contentType": "scenario",
                    "sortOrder": "createdAt",
                    "offset": 0
                },
                "username": self.user
            },
            "query": self.scenarios_query_string
        }
        self.query_options = {
            "variables": {
                "publicId": ""
            },
            "query": self.options_query_string
        }
        self.query_adventures = {
            "variables": {
                "input": {
                    "searchTerm": "",
                    "saved": False,
                    "trash": False,
                    "contentType": "adventure",
                    "sortOrder": "createdAt",
                    "offset": 0
                },
                "username": self.user
            },
            "query": self.adventures_query_string
        }
        self.query_posts = {
            "variables": {
                "input": {
                    "searchTerm": "",
                    "saved": False,
                    "trash": False,
                    "contentType": "post",
                    "sortOrder": "createdAt",
                    "offset": 0
                },
                "username": self.user
            },
            "query": self.posts_query_string
        }
        self.query_worlds = {
            "query": self.worlds_query_string
        }
        self.query_social = {
            "variables": {
                "username": self.user
            },
            "query": self.social_query_string
        }
        
        # requests settings
        self.session = requests.Session()
        self.session.headers.update({'content-type': 'application/json',
                                        'x-access-token': self.access_token})
        self.url = 'https://api.aidungeon.io/graphql'

    def make_query(self, query, token=None):
        if token is None:
            token = self.access_token
        self.session.headers.update({'x-access-token': token})
        res = self.session.post(self.url, data=json.dumps(query)).json()
        return res
     
    def auth_user(self):
        t = Token(self)
        self.access_token = t.get()
    
    # Expects a username, whether or not the data is from a bookmark
    def save_json(self, content_type, is_saved=False):
        # Current local time in ISO 8601 format.
        time_now = strftime('%Y%m%dT%H%M%S')
        if is_saved:
            file_name = f'{self.user or "your"}_saved_{content_type}_{time_now}.json'
        else:
            file_name = f'{self.user or "your"}_{content_type}_{time_now}.json'
        
        with open(file_name, 'x', encoding='utf-8') as f:
            json.dump(self.content_cache, f, ensure_ascii=False, indent=8)
            # Transform json into a well-formatted hmtl
            # (XXX) Only Stories and Scenarios
        to_html(file_name)
        print(f'Saved to {file_name}.')
    
    def get_scenarios(self, is_saved=False):
        self.content_cache['scenarios'] = []
        self.content_cache['scenario_options'] = []
        if not is_saved:
            print('Getting scenarios...')
        else:
            print('Getting saved scenarios...')
        self.query_scenarios['variables']['input']['saved'] = is_saved
        self.query_scenarios['variables']['input']['offset'] = 0
        try:
            while True:
                result = self.make_query(self.query_scenarios)
                
                if 'data' in result:
                    if result['data']['user']['search']:
                        self.content_cache['scenarios'] += result['data']['user']['search']
                        print('Got %d scenarios...' % len(self.content_cache['scenarios']))
                        self.query_scenarios['variables']['input']['offset'] = len(self.content_cache['scenarios'])
                        for scenario in result['data']['user']['search']:
                            if 'options' in scenario and isinstance(scenario['options'], list):
                                for option in scenario['options']:
                                    self.content_cache['scenario_options'].append(option['publicId'])
                    else:
                        print('No more scenarios found.')
                        break
                else:
                    print('There was no data...')
                    break
        except requests.HTTPError as e:
            print(e)
            print(e.read())
        
        self.get_subscenarios()
        if self.content_cache['scenarios']:
            self.save_json('scenarios', is_saved)
        else:
            print('No scenarios to save!')
    
    def get_subscenarios(self):
        try:
            for pubid in self.content_cache['scenario_options']:
                print('Getting subscenario %s...' % pubid)
                self.query_options['variables']['publicId'] = pubid
                result = self.make_query(self.query_options)
                
                if 'data' in result and 'scenario' in result['data']:
                    result['data']['scenario']['isOption'] = True
                    self.content_cache['scenarios'].append(result['data']['scenario'])
                    if 'options' in result['data']['scenario'] and \
                            isinstance(result['data']['scenario']['options'], list):
                        for option in result['data']['scenario']['options']:
                            self.content_cache['scenario_options'].append(option['publicId'])
                else:
                    print('There was no data...')
        except requests.HTTPError as e:
            print(e)
            print(e.read())
        self.content_cache['scenario_options'] = []
    
    def get_adventures(self, is_saved=False):
        self.content_cache['adventures'] = []
        if not is_saved:
            print('Getting adventures...')
        else:
            print('Getting saved adventures...')
        self.query_adventures['variables']['input']['saved'] = is_saved
        self.query_adventures['variables']['input']['offset'] = 0
        try:
            while True:
                result = self.make_query(self.query_adventures)
                
                if 'data' in result:
                    if result['data']['user']['search']:
                        self.content_cache['adventures'] += result['data']['user']['search']
                        print('Got %d adventures...' % len(self.content_cache['adventures']))
                        self.query_adventures['variables']['input']['offset'] = len(self.content_cache['adventures'])
                    else:
                        print('No more adventures found.')
                        break
                else:
                    print('There was no data...')
                    break
        except requests.HTTPError as e:
            print(e)
            print(e.read())
        if self.content_cache['adventures']:
            self.save_json('adventures', is_saved)
        else:
            print('No adventures to save!')
    
    def get_posts(self, is_saved=False):
        self.content_cache['posts'] = []
        if not is_saved:
            print('Getting posts...')
        else:
            print('Getting saved posts...')
        self.query_posts['variables']['input']['saved'] = is_saved
        self.query_posts['variables']['input']['offset'] = 0
        while True:
            result = self.make_query(self.query_posts)
            
            if 'data' in result:
                if result['data']['user']['search']:
                    self.content_cache['posts'] += result['data']['user']['search']
                    print('Got %d posts...' % len(self.content_cache['posts']))
                    self.query_posts['variables']['input']['offset'] = len(self.content_cache['posts'])
                else:
                    print('No more posts found.')
                    break
            else:
                print('There was no data...')
                break
        
        if self.content_cache['posts']:
            self.save_json('posts', is_saved)
        else:
            print('No posts to save!')
    
    def get_worlds(self):
        self.content_cache['worlds'] = []
        print('Getting worlds...')
        try:
            result = self.make_query(self.query_worlds)
            
            if 'data' in result:
                self.content_cache['worlds'] = result['data']['worlds']
            else:
                print('There was no data...')
            
            if self.content_cache['worlds']:
                self.save_json('worlds')
            else:
                print('No worlds to save!')
        except requests.HTTPError as e:
            print(e)
            print(e.read())
    
    def get_social(self):
        self.content_cache['friends'] = []
        self.content_cache['followers'] = []
        self.content_cache['following'] = []
        print('Getting friends, followers, and following...')
        
        try:
            result = self.make_query(self.query_social)
            
            if 'data' in result:
                if 'friends' in result['data']['user']:
                    self.content_cache['friends'] = result['data']['user']['friends']
                if 'followers' in result['data']['user']:
                    self.content_cache['followers'] = result['data']['user']['followers']
                if 'following' in result['data']['user']:
                    self.content_cache['following'] = result['data']['user']['following']
            else:
                print('There was no data...')
        except requests.HTTPError as e:
            print(e)
            print(e.read())
        
        if self.content_cache['friends']:
            self.save_json('friends')
        else:
            print('No friends to save!')
        
        if self.content_cache['followers']:
            self.save_json('followers')
        else:
            print('No followers to save!')
        
        if self.content_cache['following']:
            self.save_json('following')
        else:
            print('No following to save!')
    
    def get_saves(self):
        self.get_scenarios(True)
        self.get_adventures(True)
        self.get_posts(True)

class Token():
    def __init__(self, user):
        self.user = user
    # This is a class which groups together static methods for handling x-access-tokens.
    
    # Gets the user's x-access-token. Tries to load from file first, and will prompt the user otherwise.
    def get(self):
        return self.load() or self.prompt()
    
    # Loads the user's x-access-token from a file.
    def load(self):
        clear_screen()
        print('Getting from file')
        try:
            with open('access_token.txt', 'r') as f:
                token = f.read().strip()
                token = self.validate(token)
                print(f'Token loaded for account {self.username(token)}.')
                return token
        except IOError:
            print('Saved token not found...')
        except ValueError as e:
            print(e)
        
        return None

    # Prompts the user for an x-access-token until a valid one is given, and prompts to save the given token.
    def prompt(self, can_exit=False):
        while True:
            # Loop until a valid token is given
            clear_screen()
            if can_exit:
                token = input('Please enter your access token (UUID), or press Enter to go back: ')
                if not token.strip():
                    return None
            else:
                token = input('Please enter your access token (UUID): ').strip()
            try:
                token = self.validate(token)
                print(f'\nToken loaded for account {self.username(token)}.')
                if input('Would you like to save your token for later? (y/n): ').lower().strip()[:1] == 'y':
                    self.save(token)
                return token
            except ValueError as e:
                print(e, 'Please try again.')
                pause()
    
    # Save's the user's x-access-token to 'access_token.txt'.
    def save(self, token):
        clear_screen()
        try:
            with open('access_token.txt', 'w') as file:
                file.write(token)
            print("Token saved to 'access_token.txt'.")
        except IOError:
            print('Something went wrong saving your access token.')
        pause()

    # Retrieves the account username associated with a token. Returns None for an invalid token.
    def username(self, token):

        result = self.user.make_query({'query': '{user {username}}'}, token)
        if result['data']['user']:
            return result['data']['user']['username']
        else:
            return None

    # Validates a user token. Returns the correct token on success, otherwise raises a ValueError.
    def validate(self, token):
        try:
            token = str(uuid.UUID(token))  # validates the token as a UUID
        except ValueError:
            raise ValueError("Invalid token format detected. Should be a valid UUID.")
        if self.username(token) is None:
            raise ValueError("Invalid token detected. The token provided is not associated with any account.")
       
        return token

# Tries to clear the user's screen. Skips on exception.
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input('\nPress Enter to continue...')
