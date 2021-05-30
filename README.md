# AI Dungeon Content Archive Toolkit (AID CAT)

AID CAT is a command-line utility that will allow you to download JSON backups of:
 1. Your private and published AI Dungeon scenarios, adventures, posts, bookmarks, worlds, friends, followers, and following.
 2. <TEMPORARILIY DISABLED DUE TO LATITUDE BRICKING PUBLIC QUERIES> Any user's published scenarios, adventures, and posts, as well as their friends, followers, and following.
 3. Obfuscate all adventures' titles, descriptions, tags, memory, actions, undone actions, and world info with junk data.
<br>**WARNING! Obfuscating adventures wipes all adventures on an account and CANNOT BE UNDONE!**

Things AID CAT will **NEVER** do:
 1. Download another user's private content.
 2. Share your information with anyone else. All data transferred is strictly between your device and the aidungeon.io GraphQL backend.

## [Go check out KoboldAI!](https://github.com/KoboldAI/KoboldAI-Client)
**Saved AI Dungeon games exported using AID CAT can now be imported and played with [KoboldAI](https://github.com/KoboldAI/KoboldAI-Client)!** KoboldAI is a browser front-end for playing with multiple local & remote AI models. KoboldAI supports interact with the AI models via Tensorflow and includes a easy-to-use automated install process. Currently supported models are GPT Neo 1.3B/2.7B, GPT-2 Med/Large/XL, Megatron (via InferKit API) as well as the ability to run your fine-tuned custom GPT-Neo (e.g., Neo-horni) and custom GPT-2 (e.g., CloverEdition) models.

## [Latest Release](https://github.com/CuriousNekomimi/AIDCAT/releases)
### 2021-05-30: v0.6.9
```
Added the ability to obfuscate all adventures' title, description, tags, memory, actions, undone actions, and world info with junk data.
**WARNING! Obfuscating adventures wipes all adventures on an account and CANNOT BE UNDONE!**
Added an info page to sources documenting Latitude.
```
Instructions below copied with edits from original script author's site (referenced files uploaded here for archival purposes):

## The wAIfupocalypse is upon us
### Let's save your stories!

Recently, [Latitude](https://latitude.io/blog/update-to-our-community-ai-test-april-2021/) has announced changes that will end AI cooms as we know them today. Going beyond just the explore page, employees may now ban you for content in your unpublished stories. For this reason, I have programmed a script that can automatically download all of the stories and scenarios in your account. Here are the instructions:

1. Before you can use the script, you must download and install the [Python 3 runtime](https://www.python.org/downloads/). **Make sure to select "Add Python 3.X to PATH" on the first page of the installer.**
2. The script needs your access token so it can access your private stories. The token will only be used for that purpose, and it will not be stored. See how to access it in [Firefox](/firefox.webm) or [Chrome](/chrome.webm).
3. Download the aidcat.py script [here](https://github.com/CuriousNekomimi/AIDCAT/releases). Move it to where you want your stories saved and run it. (usually by double-clicking, or typing `python aidcat.py` or `python3 aidcat.py` in the command prompt while in the directory containing the script file).
4. Enter your login token and press enter. While you wait, think back to the good times you had with your fictional friends.
5. When the download is complete, a file called stories.json will be created containing all your stories.

I have also created a script that will turn that JSON file into HTML files so it's easier to read. Download it [here](/genhtml_edit.py) and run it in the same folder as the JSON file. You might also want to get this [stylesheet](/style.css) (put in same folder as html files) to make things look a little nicer.

### For mobile users

You can run these scripts using [Termux](https://termux.com/) (Android) or [Pythonista](https://apps.apple.com/us/app/pythonista-3/id1085978097) (iOS). Since it's difficult to access your login token on a mobile browser, here is a script to help you with that: [login.py](/login.py) (1.1 KiB)

## Changelog
```
2021-05-11: v0.6.7
 HUGE thanks to Eta for making these improvements and for refactoring the program to be object oriented:
- The phrase "any key" was changed to "Enter." (Actually waiting for any keypress is significantly more complicated).
- Option 1 of the auth menu previously said [1] Change your access access token, which was fixed.
- Added a missing error message on "Our Content" page.
- PEP 8 compliance:
  - The header docstring was changed to use """ instead of '''
  - Fixed whitespace around operators in code and method declarations
  - Fixed indentation in a couple places
  - Added whitespace between the # and the start of each comment
  - Added a newline at the end of the file
  - Added two lines of whitespace before and after function definitions
  - (Non-PEP 8) Changed menu choices to all be double quoted strings, for consistency
- Removed default values from actually-mandatory method parameters like save_json's content_type
- Separated the long as heck query strings from the rest of the code and moved them to the bottom of the file, just above if __name__ == '__main__', to improve readability
- Added a User class
  - This class encompasses the operations make_query (new), save_json, get_scenarios/subscenarios/adventures/posts/worlds/social, and get_saves (new, which calls all of the bookmarked operations together)
  - It holds the fields content_cache, and each of the query_s as instance variables (no longer global)
    - This means these can be maintained independently per user, which will help a lot with the batch download feature later on (it allows that to be multithreaded, for example)
- All of the menu code was changed to use User objects representing different users instead of passing around a username parameter
- The menu code was additionally refactored to cut down on duplicated code by a lot

2021-05-10: v0.5.7
Thanks to Eta for these suggestions:
UUID (access token) validation using python's built-in uuid library.
Cleaned up boolean checks.
Better file management. Saving files no longer risks a memory leak if the programmer forgets to call close().

2021-05-09: v0.5.6
Various improvements to the code in terms of efficiency and syntax, thanks Eta!

2021-05-09: v0.5.4
Changed aidcat.py to UTF-8 encoding. If you were seeing weird issues with screens, like corrupted text, this should fix that issue.
Thanks to Eta for the great suggestions for improving efficiency and helping with refactoring overall, including:
Menu headers are now all block quotes.
Reduced the number of escaped characters ( e.g. \' ).
More conventional print() statements.

Future Plans:
Proper GUID validation
HTML format export/converter. (Next priority)
Possibly add the ability to batch download all your friends' and followings' published content.
Ability to get the user's x-access-token from within the application. (Rather than digging around in the browser.)

2021-05-09: v0.5.2 (Completely new program written from scratch)
Command-line user interface with menus.
Download your scenarios, subscenarios, adventures, posts, and worlds (including official purchased worlds).
Download your saved scenarios, adventures, and posts (bookmarks).
Download a list of your friends, following, and followers.
Download other user's published scenarios, subscenarios, and posts.
Download a list of other user's friends, followers, and following.
Saved files tagged with ISO 8601 format times, so previous files aren't accidentally overwritten.
NOTE: Windows (Command prompt/PowerShell) doesn't display UTF-8 encoded characters. If someone has fancy UTF characters in their username, they will show up as empty boxes when pasted in, but the program will still work.

Future plans:
HTML format export/converter. (Next priority)
Possibly add the ability to batch download all your friends' and followings' published content.
Ability to get the user's x-access-token from within the application. (Rather than digging around in the browser.)

2021-05-02:
Added: Ability to save subscenarios (thanks to the original script author)!
Added: Ability to save bookmarks (thanks to the original script author)!
Added: Choice to save scenario bookmarks.
Added: Choice to save adventure bookmarks.

2021-05-02:
Added: Ability to choose whether or not to download scenarios, adventures, or worlds. Useful for users who have thousands of adventures and don't want to download them every time.
Added: More error catching and a reminder to report errors to https://github.com/CuriousNekomimi/AIDungeonRescue/issues.
Note: The original script author has released an update to download scenario options. I'll work on incorporating that code.

2021-05-02:
Added: Ability to save worlds!
Added: Ability to save x-access token for later use (token.txt).
Added: Scenarios, adventures, and worlds, now save to separate json files.
Added: Improved readability of saved scenario, adventure, and world json files with newlines and indents.
Added: Pause for user interaction after running so the user knows the program executed successfully.
Added: Notification that files saved successfully.
Added: Try/Except to main() for several methods.
Refactored: 'stories' to 'adventures'.
```
