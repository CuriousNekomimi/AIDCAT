import sys
import json
import html
import tkinter as tk
from tkinter import filedialog
from os import path, getcwd

# Variables for verifying file selections
adventure_path_ok = False
scenario_path_ok = False


# Methods
def escape(text):
    if type(text) is str:
        return html.escape(text)
    else:
        return "(null)"


def nl_escape(text):
    return escape(text).replace('\n', '<br>')


def get_load_path(dir, title, types):
    root = tk.Tk()
    root.attributes("-topmost", True)
    path = tk.filedialog.askopenfilename(
        initialdir=dir,
        title=title,
        filetypes=types
    )
    root.destroy()
    if (path != "" and path != None):
        return path
    else:
        return None


# Send welcome message
input("\nWelcome to the AIDCAT HTML Generator!\n\
First we'll ask for your Adventure file, press Enter to continue...")

# Ask for JSON file
while (not adventure_path_ok):
    path = get_load_path(getcwd(), "Select Adventures File", [("Json", "*.json")])
    if (not path):
        cont = input("\nThere was an issue getting your file. Would you like to try again? (y/n)")
        if (cont.lower() == "n" or cont.lower() == "no"):
            quit()
    else:
        adventure_path_ok = True

file = file = open(path, "r")
infile = json.load(file)

index = open('index.html', 'w', encoding='utf-8')
index.write("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width">
<link rel="stylesheet" href="style.css">
<title>AI Dungeon Archive</title>
</head>
<body>
<h1>AI Dungeon Archive</h1>
<h2>Stories</h2>
<ul>""")

for story in infile:
    try:
        index.write('<li title="%s"><a href="%s.html">%s</a></li>' % (
            story['createdAt'], story['publicId'], escape(story['title'])))
        html_file = open('%s.html' % story['publicId'], 'w', encoding='utf-8')
        html_file.write("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width">
<link rel="stylesheet" href="style.css">
<title>%s</title>
</head>
<body>
<h1>%s</h1>
<label id="underlineactions" style="display: none" title="Story is red, do is green, say is blue."><input autocomplete="off" onchange="document.body.className = this.checked ? 'showtypes' : ''" type="checkbox"> Underline actions</label>
<details><summary>Details</summary>Description: %s<br>Created at: %s<br>Updated at: %s<br>Remember: %s<br>Author's note: %s""" % (
            escape(story['title']), escape(story['title']), nl_escape(story['description']), escape(story['createdAt']),
            escape(story['updatedAt']), nl_escape(story['memory']), nl_escape(story['authorsNote'])))
        html_file.write('<details><summary>Discarded actions</summary>')
        for action in story['undoneWindow']:
            html_file.write('<span data-type="%s" title="%s">%s</span>' % (
                action['type'], escape(action['createdAt']), nl_escape(action['text'])))
            if action != story['undoneWindow'][-1]:
                html_file.write('<hr>')
        html_file.write('</details>')
        if 'worldInfo' in story and type(story['worldInfo']) is list and len(story['worldInfo']) > 0:
            html_file.write('<details><summary>World info</summary>')
            for entry in story['worldInfo']:
                if 'keys' in entry and 'entry' in entry:
                    html_file.write('<b>%s</b>: %s' % (escape(entry['keys']), nl_escape(entry['entry'])))
                    if entry != story['worldInfo'][-1]:
                        html_file.write('<hr>')
            html_file.write('</details>')
        html_file.write('</details>')
        for action in story['actions']:
            html_file.write('<span data-type="%s" title="%s">%s</span>' % (
                action['type'], escape(action['createdAt']), nl_escape(action['text'])))
        html_file.write('</body></html>')
        html_file.close()
    except Exception as e:
        print('An error occured converting story %s:' % story['title'])
        print('%s: %s' % (type(e).__name__, e))
        input("Press enter to dismiss...")

# Ask if Scenarios should be loaded as well
do_scenarios = input(
    "\nGreat! The HTML for your Adventures has been generated. Would you like to add your scenarios as well? (y/n)\n")

if (do_scenarios.lower() == "n" or do_scenarios.lower() == "no"):
    pass
else:
    # Ask for Scenarios file    
    while (not scenario_path_ok):
        path = get_load_path(getcwd(), "Select Scenarios File", [("Json", "*.json")])
        if (not path):
            cont = input("\nThere was an issue getting your file. Would you like to try again? (y/n)")
            if (cont.lower() == "n" or cont.lower() == "no"):
                quit()
        else:
            scenario_path_ok = True

    file = file = open(path, "r")
    infile = json.load(file)

    # Start writing HTML
    index.write('</ul><h2>Scenarios</h2><ul>')
    for scenario in infile:
        try:
            if 'isOption' not in scenario or scenario['isOption'] != True:
                index.write('<li title="%s"><a href="%s.html">%s</a></li>' % (
                    scenario['createdAt'], scenario['publicId'], escape(scenario['title'])))
            html_file = open('%s.html' % scenario['publicId'], 'w', encoding='utf-8')
            html_file.write("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width">
    <link rel="stylesheet" href="style.css">
    <title>%s</title>
    </head>
    <body>
    <h1>%s</h1>
    Created at: %s<br>
    Updated at: %s
    <h2>Description</h2>
    %s
    <h2>Prompt</h2>
    %s
    <h2>Remember</h2>
    %s
    <h2>Author's Note</h2>
    %s
    """ % (escape(scenario['title']), escape(scenario['title']), scenario['createdAt'], scenario['updatedAt'],
                nl_escape(scenario['description']), nl_escape(scenario['prompt']), nl_escape(scenario['memory']),
                nl_escape(scenario['authorsNote'])))
            if 'quests' in scenario and type(scenario['quests']) is list and len(scenario['quests']) > 0:
                html_file.write('<h2>Quests</h2>')
                for quest in scenario['quests']:
                    html_file.write(nl_escape(quest))
                    if quest != scenario['quests'][-1]:
                        html_file.write('<hr>')
            if 'options' in scenario and type(scenario['options']) is list and len(scenario['options']) > 0:
                html_file.write('<h2>Options</h2><ul>')
                for subscen in scenario['options']:
                    html_file.write('<li title="%s"><a href="%s.html">%s</a></li>' % (
                        subscen['createdAt'], subscen['publicId'], escape(subscen['title'])))
                html_file.write('</ul>')
            if 'worldInfo' in scenario and type(scenario['worldInfo']) is list and len(scenario['worldInfo']) > 0:
                html_file.write('<details><summary><h2>World Info</h2></summary>')
                for entry in scenario['worldInfo']:
                    if 'keys' in entry and 'entry' in entry:
                        html_file.write('<b>%s</b>: %s' % (escape(entry['keys']), nl_escape(entry['entry'])))
                        if entry != scenario['worldInfo'][-1]:
                            html_file.write('<hr>')
                html_file.write('</details>')
            if 'gameCode' in scenario and type(scenario['gameCode']) is dict:
                html_file.write('<details><summary><h2>Scripts</h2></summary>')
                if 'sharedLibrary' in scenario['gameCode']:
                    html_file.write(
                        '<h3>Shared library</h3><pre>%s</pre>' % escape(scenario['gameCode']['sharedLibrary']))
                if 'onInput' in scenario['gameCode']:
                    html_file.write('<h3>Input modifier</h3><pre>%s</pre>' % escape(scenario['gameCode']['onInput']))
                if 'onModelContext' in scenario['gameCode']:
                    html_file.write(
                        '<h3>Context modifier</h3><pre>%s</pre>' % escape(scenario['gameCode']['onModelContext']))
                if 'onOutput' in scenario['gameCode']:
                    html_file.write('<h3>Output modifier</h3><pre>%s</pre>' % escape(scenario['gameCode']['onOutput']))
                html_file.write('</details>')
            html_file.write('</body></html>')
            html_file.close()
        except Exception as e:
            print('An error occurred converting scenario %s:' % scenario['title'])
            print('%s: %s' % (type(e).__name__, e))
            input("Press enter to dismiss...")

    index.write('</ul></body></html>')
    index.close()

print("\nGreat your HTML file should be ready! Open index.html in the AIDCAT directory to view it!\n")
input("Press any key to close this application...")
