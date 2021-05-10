# AI Dungeon Content Archive Toolkit
A script that will automatically download your AI Dungeon worlds, scenarios, and adventures.

# [Latest Release](https://github.com/CuriousNekomimi/AIDCAT/releases)
### 2021-05-09: v0.5.7
```
Thanks to Eta for these suggestions:
UUID (access token) validation using python's built-in uuid library.
Cleaned up boolean checks.
Better file management. Saving files no longer risks a memory leak if the programmer forgets to call close().
```

Instructions below copied with edits from original script author's site (referenced files uploaded here for archival purposes):

## The wAIfupocalypse is upon us
### Let's save your stories!

Recently, [Latitude](https://latitude.io/blog/update-to-our-community-ai-test-april-2021/) has announced changes that will end AI cooms as we know them today. Going beyond just the explore page, employees may now ban you for content in your unpublished stories. For this reason, I have programmed a script that can automatically download all of the stories and scenarios in your account. Here are the instructions:

1. Before you can use the script, you must download and install the [Python 3 runtime](https://www.python.org/downloads/).
2. The script needs your access token so it can access your private stories. The token will only be used for that purpose, and it will not be stored. See how to access it in [Firefox](/firefox.webm) or [Chrome](/chrome.webm).
3. Download the aidcat.py script [here](https://github.com/CuriousNekomimi/AIDCAT/releases). Move it to where you want your stories saved and run it. (usually by double-clicking, or typing `python aidcat.py` or `python3 aidcat.py` in the command prompt while in the directory containing the script file).
4. Enter your login token and press enter. While you wait, think back to the good times you had with your fictional friends.
5. When the download is complete, a file called stories.json will be created containing all your stories.

I have also created a script that will turn that JSON file into HTML files so it's easier to read. Download it [here](/genhtml.py) and run it in the same folder as the JSON file. You might also want to get this [stylesheet](/style.css) (put in same folder as html files) to make things look a little nicer.

### For mobile users

You can run these scripts using [Termux](https://termux.com/) (Android) or [Pythonista](https://apps.apple.com/us/app/pythonista-3/id1085978097) (iOS). Since it's difficult to access your login token on a mobile browser, here is a script to help you with that: [login.py](/login.py) (1.1 KiB)

## Changelog
```
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
