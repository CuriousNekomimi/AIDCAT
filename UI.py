import sys
import os
from time import sleep

from aidcat import User, Token, clear_screen

menu_header = '\nAvailable operations:\n'

auth_menu_choices = [
    "[1] Change your access token.",
    "[2] Save your access token (saves token to 'access_token.txt').",
    "[3] Wipe your access token (deletes 'access_token.txt').",
    "[4] View your token. WARNING! NEVER LET ANYONE SEE YOUR TOKEN!",
    "[0] Return to main menu. [Default].\n"
]

your_content_menu_choices = [
    "[1] Download your scenarios.",
    "[2] Download your adventures.",
    "[3] Download your posts.",
    "[4] Download your worlds (includes purchased worlds).",
    "[5] Download your friends, followers, and following.",
    "[6] Download your saves (bookmarks).",
    "[7] Download all of the above.",
    "[0] Return to main menu. [Default]\n"
]

main_menu_choices = [
    "[1] Download your saved content. [Default]",
    "[2] <TEMPORARILY DISABLED> Download another user's published content.\n    *Latitude has disabled the ability to save other users' published content.",
    "[3] Change, wipe, or view your access token.",
    "[0] Quit program.\n"
]

# Load screen flash string from a file, since we 
# do not want all that "stuff" laying around here, right?
def load_media(file_name):
    with open(file_name) as file: 
        return file.read().strip()

def pause():
    input('\nPress Enter to continue...')

# Close the program.
def program_quit():
    clear_screen()
    print(load_media('screen_quit'))
    pause()
    clear_screen()
    print('SURPRISE HUG!')
    sleep(1.5)
    for line in load_media('screen_surprise').split('\n'):
        print(line)
        sleep(0.01)
    input('\nPress Enter to nya...')
    sys.exit()

def auth_menu(user):
    while True:
        # Set the default menu choice.
        choice = 0
        clear_screen()
        print(load_media('menu_header_auth_menu'), 
                menu_header,
                *auth_menu_choices, 
                sep='\n')
        num_choices = len(auth_menu_choices) - 1
        try:
            choice = int(input(f'Operation [0-{num_choices}]: '))
        except ValueError:
            pass
        
        # Return to the main menu.
        if choice == 0:
            break
        
        # Set access_token.
        elif choice == 1:
            # If Token.promp() returns None, don't change the value of User.access_token.
            User.access_token = Token.prompt(can_exit=True) or User.access_token
        
        # Save access_token to file.
        elif choice == 2:
            Token.save(User.access_token)
        
        # Wipe access_token.
        elif choice == 3:
            clear_screen()
            if os.path.exists("access_token.txt"):
                os.remove("access_token.txt")
                print('Deleted access_token.txt.')
            else:
                print("No access_token.txt exists.")
            pause()
       
        elif choice == 4:
            clear_screen()
            print('WARNING! Never share this token! It grants full control of your AI Dungeon account!',
                  f'\nStored x-access-token: {User.access_token}')
            pause()
            
        else:
            print(f'ERR: Input must be an integer from 0 to {num_choices}. Try again!')
            sleep(1)

def your_content_menu(user):

    actions = [user.get_scenarios, user.get_adventures, user.get_posts,
               user.get_worlds, user.get_social, user.get_saves]
    content_types = ["scenarios", "adventures", "posts",
                     "worlds", "friends, followers, and following", "bookmarks", ]
    
    while True:
        # Set the default menu choice.
        choice = 0
        clear_screen()
        print(load_media('menu_header_your_content'),
                menu_header,
                *your_content_menu_choices, sep='\n')
        num_choices = len(your_content_menu_choices) - 1
        try:
            choice = int(input(f'Operation [0-{num_choices}]: '))
        except ValueError:
            pass
        
        if choice != 0:
            clear_screen()
        
        # Return to the main menu.
        if choice == 0:
            break
        
        elif 1 <= choice <= 6:
            action = actions[choice - 1]
            content_type = content_types[choice - 1]
            try:
                action()
            except Exception as e:
                print(f'An error occurred saving your {content_type}.')
                print(e)
        
        elif choice == 7:
            for action, content_type in zip(actions, content_types):
                try:
                    action()
                except Exception as e:
                    print(f'An error occurred saving your {content_type}.')
                    print(e)
        else:
            print(f'ERR: Input must be an integer from 0 to {num_choices}. Try again!')
            sleep(1)
            continue
        
        pause()


def our_content_menu_choices(target_username):
    return [
        f"[1] Download {target_username}'s published scenarios.",
        f"[2] Download {target_username}'s published adventures.",
        f"[3] Download {target_username}'s published posts.",
        f"[4] Download {target_username}'s friends, followers, and following.",
        "[5] Download all of the above.",
        "[6] Change target user.",
        "[0] Return to main menu. [Default]\n"
    ]


# Other user content download menu
def our_content_menu():
    target_username = ''
    while not target_username:
        clear_screen()
        target_username = input("Target user's AI Dungeon username: ")
    while True:
        menu_choices = our_content_menu_choices(target_username)
        num_choices = len(menu_choices) - 1
        target_user = User(target_username)
        
        actions = [target_user.get_scenarios, target_user.get_adventures, target_user.get_posts, target_user.get_social]
        content_types = ["scenarios", "adventures", "posts", "friends, followers, and following"]
        
        # Set the default menu choice.
        choice = 0
        clear_screen()
        print(load_media('menu_header_our_content'),
                menu_header,
                *menu_choices, sep='\n')
        try:
            choice = int(input(f'Operation [0-{num_choices}]: '))
        except ValueError:
            pass
        
        if choice != 0:
            clear_screen()
        
        # Return to the main menu.
        if choice == 0:
            break
        
        elif 1 <= choice <= 4:
            action = actions[choice - 1]
            content_type = content_types[choice - 1]
            try:
                action()
            except Exception:
                print(f"An error occurred saving {target_username}'s {content_type}.")
        
        elif choice == 5:
            for action, content_type in zip(actions, content_types):
                try:
                    action()
                except Exception:
                    print(f"An error occurred saving {target_username}'s {content_type}.")
        
        elif choice == 6:
            try:
                target_username = input("Target user's AI Dungeon username: ")
            except Exception:
                print('An error occurred setting the target user.')
        
        else:
            print(f'ERR: Input must be an integer from 0 to {num_choices}. Try again!')
            sleep(1)
            continue
        
        pause()

# The main menu.
def main_menu(user):
    while True:
        # Set the default menu choice.
        choice = 1
        clear_screen()
        print(load_media('menu_header_main'),
                menu_header,
                *main_menu_choices, sep='\n')
        num_choices = len(main_menu_choices) - 1
        try:
            choice = int(input(f'Operation [0-{num_choices}]: '))
        except ValueError:
            pass
        if choice == 0:
            program_quit()
        elif choice == 1:
            your_content_menu(user)
        # elif choice == 2:
        #     our_content_menu()
        elif choice == 3:
            auth_menu(user)
        else:
            print(f'ERR: Input must be an integer from 0 to {num_choices}. Try again!')
            sleep(1)

if __name__ == '__main__':
    try:
        user = User()
        clear_screen()
        print(load_media('screen_flash'))
        pause()
        clear_screen()
        print(load_media('screen_copyright'))
        pause()
        #
        user.auth_user()
        main_menu(user)
    except KeyboardInterrupt:
        from signal import SIGINT
        sys.exit(SIGINT.value)
