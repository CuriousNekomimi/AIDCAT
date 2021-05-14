import sys
import json
import html
import tkinter as tk
from tkinter import filedialog
from os import path, getcwd

# Variables for verifying file selections
adventurepathok = False
scenariopathok  = False

# Methods
def escape(text):
	if type(text) is str:
		return html.escape(text)
	else:
		return "(null)"

def nlescape(text):
	return escape(text).replace('\n','<br>')

def getloadpath(dir, title, types):
    root = tk.Tk()
    root.attributes("-topmost", True)
    path = tk.filedialog.askopenfilename(
        initialdir=dir, 
        title=title, 
        filetypes = types
        )
    root.destroy()
    if(path != "" and path != None):
        return path
    else:
        return None

# Send welcome message
input("\nWelcome to the AIDCAT HTML Generator!\n\
First we'll ask for your Adventure file, press Enter to continue...")

# Ask for JSON file
while(not adventurepathok):
    path = getloadpath(getcwd(), "Select Adventures File", [("Json", "*.json")])
    if(not path):
        cont = input("\nThere was an issue getting your file. Would you like to try again? (y/n)")
        if(cont.lower() == "n" or cont.lower() == "no"):
            quit()
    else:
        adventurepathok = True

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
		index.write('<li title="%s"><a href="%s.html">%s</a></li>' % (story['createdAt'], story['publicId'], escape(story['title'])))
		htmlfile = open('%s.html' % story['publicId'], 'w', encoding='utf-8')
		htmlfile.write("""
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
<details><summary>Details</summary>Description: %s<br>Created at: %s<br>Updated at: %s<br>Remember: %s<br>Author's note: %s""" % (escape(story['title']), escape(story['title']), nlescape(story['description']), escape(story['createdAt']), escape(story['updatedAt']), nlescape(story['memory']), nlescape(story['authorsNote'])))
		htmlfile.write('<details><summary>Discarded actions</summary>')
		for action in story['undoneWindow']:
			htmlfile.write('<span data-type="%s" title="%s">%s</span>' % (action['type'], escape(action['createdAt']), nlescape(action['text'])))
			if action != story['undoneWindow'][-1]:
				htmlfile.write('<hr>')
		htmlfile.write('</details>')
		if 'worldInfo' in story and type(story['worldInfo']) is list and len(story['worldInfo']) > 0:
			htmlfile.write('<details><summary>World info</summary>')
			for entry in story['worldInfo']:
				if 'keys' in entry and 'entry' in entry:
					htmlfile.write('<b>%s</b>: %s' % (escape(entry['keys']), nlescape(entry['entry'])))
					if entry != story['worldInfo'][-1]:
						htmlfile.write('<hr>')
			htmlfile.write('</details>')
		htmlfile.write('</details>')
		for action in story['actions']:
			htmlfile.write('<span data-type="%s" title="%s">%s</span>' % (action['type'], escape(action['createdAt']), nlescape(action['text'])))
		htmlfile.write('</body></html>')
		htmlfile.close()
	except Exception as e:
		print('An error occured converting story %s:' % story['title'])
		print('%s: %s' % (type(e).__name__, e))
		input("Press enter to dismiss...")

# Ask if Scenarios should be loaded as well
doscenarios = input("\nGreat! The HTML for your Adventures has been generated. Would you like to add your scenarios as well? (y/n)\n")

if(doscenarios.lower() == "n" or doscenarios.lower() == "no"):
    pass
else:
    # Ask for Scenarios file    
    while(not scenariopathok):
        path = getloadpath(getcwd(), "Select Scenarios File", [("Json", "*.json")])
        if(not path):
            cont = input("\nThere was an issue getting your file. Would you like to try again? (y/n)")
            if(cont.lower() == "n" or cont.lower() == "no"):
                quit()
        else:
            scenariopathok = True
    
    file = file = open(path, "r")
    infile = json.load(file)

    # Start writing HTML
    index.write('</ul><h2>Scenarios</h2><ul>')
    for scenario in infile:
        try:
            if 'isOption' not in scenario or scenario['isOption'] != True:
                index.write('<li title="%s"><a href="%s.html">%s</a></li>' % (scenario['createdAt'], scenario['publicId'], escape(scenario['title'])))
            htmlfile = open('%s.html' % scenario['publicId'], 'w', encoding='utf-8')
            htmlfile.write("""
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
    """ % (escape(scenario['title']), escape(scenario['title']), scenario['createdAt'], scenario['updatedAt'], nlescape(scenario['description']), nlescape(scenario['prompt']), nlescape(scenario['memory']), nlescape(scenario['authorsNote'])))
            if 'quests' in scenario and type(scenario['quests']) is list and len(scenario['quests']) > 0:
                htmlfile.write('<h2>Quests</h2>')
                for quest in scenario['quests']:
                    htmlfile.write(nlescape(quest))
                    if quest != scenario['quests'][-1]:
                        htmlfile.write('<hr>')
            if 'options' in scenario and type(scenario['options']) is list and len(scenario['options']) > 0:
                htmlfile.write('<h2>Options</h2><ul>')
                for subscen in scenario['options']:
                    htmlfile.write('<li title="%s"><a href="%s.html">%s</a></li>' % (subscen['createdAt'], subscen['publicId'], escape(subscen['title'])))
                htmlfile.write('</ul>')
            if 'worldInfo' in scenario and type(scenario['worldInfo']) is list and len(scenario['worldInfo']) > 0:
                htmlfile.write('<details><summary><h2>World Info</h2></summary>')
                for entry in scenario['worldInfo']:
                    if 'keys' in entry and 'entry' in entry:
                        htmlfile.write('<b>%s</b>: %s' % (escape(entry['keys']), nlescape(entry['entry'])))
                        if entry != scenario['worldInfo'][-1]:
                            htmlfile.write('<hr>')
                htmlfile.write('</details>')
            if 'gameCode' in scenario and type(scenario['gameCode']) is dict:
                htmlfile.write('<details><summary><h2>Scripts</h2></summary>')
                if 'sharedLibrary' in scenario['gameCode']:
                    htmlfile.write('<h3>Shared library</h3><pre>%s</pre>' % escape(scenario['gameCode']['sharedLibrary']))
                if 'onInput' in scenario['gameCode']:
                    htmlfile.write('<h3>Input modifier</h3><pre>%s</pre>' % escape(scenario['gameCode']['onInput']))
                if 'onModelContext' in scenario['gameCode']:
                    htmlfile.write('<h3>Context modifier</h3><pre>%s</pre>' % escape(scenario['gameCode']['onModelContext']))
                if 'onOutput' in scenario['gameCode']:
                    htmlfile.write('<h3>Output modifier</h3><pre>%s</pre>' % escape(scenario['gameCode']['onOutput']))
                htmlfile.write('</details>')
            htmlfile.write('</body></html>')
            htmlfile.close()
        except Exception as e:
            print('An error occured converting scenario %s:' % scenario['title'])
            print('%s: %s' % (type(e).__name__, e))
            input("Press enter to dismiss...")

    index.write('</ul></body></html>')
    index.close()

print("\nGreat your HTML file should be ready! Open index.html in the AIDCAT directory to view it!\n")
input("Press any key to close this application...")