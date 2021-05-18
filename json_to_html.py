import sys
import os
import json
import html

def escape(text):
    if type(text) is str:
        return html.escape(text)
    else:
        return "(null)"

def new_dir(folder):
    if folder:
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass
    with open('style.css', 'r') as file:
        style = file.read()
        with open(f'{folder}/style.css', 'w') as file:
            file.write(style)

def nlescape(text):
    return escape(text).replace('\n','<br>')

def to_html(json_file):
	infile = json.load(open(json_file))
	index = open('index.html', 'w', encoding='utf-8')
	if 'stories' in infile:
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
		new_dir('stories')
		story_number = {}
		for story in infile['stories']:
		    if story['title'] and "/" in story['title']:
		        story['title'] = story['title'].replace('/', '-')
		    try:
		        try:
		            story_number[story["title"]]
		        except:
		            # new story
		            story_number = {story["title"]: ""}
		        index.write(f'''
		                    <li title="{story["createdAt"]}">
		                        <a href="stories/{story["title"]}{story_number[story["title"]]}.html">
		                            {escape(story['title'])}{story_number[story["title"]]}
		                        <a/>
		                    </li>''')
		        if not os.path.exists(f'stories/{story["title"]}{story_number[story["title"]]}.html'):
		            htmlfile = open('stories/%s.html' % (story['title']), 'w',
		                                encoding='utf-8')
		        else:
		            # story from same scenario
		            if story_number[story["title"]]:
		                story_number[story["title"]] += 1
		                htmlfile = open('stories/%s%d.html' % (story['title'],
		                                    story_number[story["title"]]), 'w',
		                                    encoding='utf-8')
		            else:
		                story_number[story["title"]] = 2
		                htmlfile = open('stories/%s%d.html' % (story['title'],
		                                    story_number[story["title"]]), 'w',
		                                    encoding='utf-8')
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
		<details><summary>Details</summary><p id="id_title">Description: %s<br>Created at: %s<br>Updated at: %s<br>Remember: %s<br><p id="id_an">Author's note: %s""" % (escape(story['title']), escape(story['title']), nlescape(story['description']), escape(story['createdAt']), escape(story['updatedAt']), nlescape(story['memory']), nlescape(story['authorsNote'])))
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
		            htmlfile.write('<span id="id_action" data-type="%s" title="%s">%s</span>' % (action['type'], escape(action['createdAt']), nlescape(action['text'])))
		        htmlfile.write('</body></html>')
		        htmlfile.close()
		    except Exception as e:
		        print('An error occured converting story %s:' % story['title'])
		        print('%s: %s' % (type(e).__name__, e))
		        input("Press enter to dismiss...")

		index.write('</ul><h2>Scenarios</h2><ul>')
	if 'scenarios' in infile:
		new_dir('scenarios')
		subscen_paths = {}
		for scenario in infile['scenarios']:
		    # get rid of annoying "/"s that mess with mkdir
		    if scenario['title'] and '/' in scenario['title']:
		        scenario['title'] = scenario['title'].replace('/', '-')
		    try:
		        if 'isOption' not in scenario or scenario['isOption'] != True:
		            # base scenario, initializing the path
		            scenario['path'] = 'scenarios/'
		            index.write('<li title="%s"><a href="scenarios/%s.html">%s</a></li>' % (scenario['createdAt'], scenario['title'], escape(scenario['title'])))
		        else:
		            scenario['path'] = subscen_paths[scenario['title']]
		        htmlfile = open('%s%s.html' % (scenario['path'], scenario['title']), 'w', encoding='utf-8')
		        htmlfile.write("""<!DOCTYPE html>
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
	%s""" % (escape(scenario['title']), escape(scenario['title']), scenario['createdAt'], scenario['updatedAt'], nlescape(scenario['description']), nlescape(scenario['prompt']), nlescape(scenario['memory']), nlescape(scenario['authorsNote'])))
		        if 'quests' in scenario and type(scenario['quests']) is list and len(scenario['quests']) > 0:
		            htmlfile.write('<h2>Quests</h2>')
		            for quest in scenario['quests']:
		                # Latitude based chads made quests as a list of dicts
		                # terefore we have to get the item inside
		                # or all quests will be {'quest': 'bar'}.
		                # In this case it will write (null) since
		                # escape() detects a list and not a str.
		                quest_string = quest['quest']
		                htmlfile.write(nlescape(quest_string))
		                if quest != scenario['quests'][-1]:
		                    htmlfile.write('<hr>')
		        if 'options' in scenario and type(scenario['options']) is list and len(scenario['options']) > 0:
		            # adding the title to the child scenario path
		            htmlfile.write('<h2>Options</h2><ul>')
		            for subscen in scenario['options']:
		                # get rid of annoying "/"s
		                if subscen['title'] and '/' in subscen['title']:
		                    subscen['title'] = subscen['title'].replace('/', '-')
		                subscen['path'] = f'{scenario["path"]}{scenario["title"]}'
		                subscen_paths[subscen['title']] = subscen['path'] + '/'
		                htmlfile.write('<li title="%s"><a name="link_subscenario" href="%s/%s.html">%s</a></li>' % (subscen['createdAt'], scenario['title'], subscen['title'], escape(subscen['title'])))
		            # path for all its the subscenarios 
		            new_dir(subscen['path'])
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
		        fewwwef
		        print('An error occured converting scenario %s:' % scenario['title'])
		        print('%s: %s' % (type(e).__name__, e))
		        input("Press enter to dismiss...")

	index.write('</ul></body></html>')
	index.close()
	print("Your dose of (stuff) is ready for reading.")
if __name__ == '__main__':
    to_html('stories.json')
