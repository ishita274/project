# This is a sample Python script.
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from flask import Flask, render_template, request
import urllib.parse, urllib.request, urllib.error, json
import logging
import csv
import random

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


app = Flask(__name__)
global_name = ''

def filter_poke():
    name_list = load_image_names()
    dict = {}
    for name in name_list:
        type_of_poke = get_type(name)
        if type_of_poke in dict:
            dict[type_of_poke] = dict[type_of_poke].append(name)
        else:
            #dict[type_of_poke] = [name]
            dict = {type_of_poke: [name]}

def get_type(poke_endpoint):
    """Uses the API to get back the type """
    # Use a breakpoint in the code line below to debug your script.
    # trying new endpoint
    baseurl = 'https://pokeapi.co/api/v2/pokemon/' + poke_endpoint +'/'
    hdr = {'User-Agent': 'Ish Pokemon App'}
    req = urllib.request.Request(baseurl, headers=hdr)
    response = urllib.request.urlopen(req).read()
    pokedata = json.loads(response)
    return pokedata['types'][0]['type']['name']

def get_effectiveness(poke_endpoint):
    """Uses API to get back a list of types that are super effective against the type parameter poke_endpoint"""
    #poke_endpoint is type
    baseurl = 'https://pokeapi.co/api/v2/type/' + poke_endpoint + '/'
    hdr = {'User-Agent': 'Ish Pokemon App'}
    req = urllib.request.Request(baseurl, headers=hdr)
    response = urllib.request.urlopen(req).read()
    pokedata = json.loads(response)
    effective = pokedata['damage_relations']['double_damage_from']
    super_effective = []
    for dict in effective:
        super_effective.append(dict['name'])
    print(pretty(effective))
    # return effective this was returning api data, now we return list
    return super_effective

def load_image_names():
    """Loads names of pokemon from th CSV file that correspond to image link index"""
    f = open('pokemon_image.csv', 'r',encoding='utf-8')
    name_list = []
    for line in f:
        line = line.rstrip()
        line = line.split(',')
        pokemon_name = line[0]
        pokemon_name = pokemon_name.lower()
        name_list.append(pokemon_name)
    return name_list

def load_images():
    """Loads images link from th CSV file"""
    f = open('pokemon_image.csv', 'r',encoding='utf-8')
    link_list = []
    name_list = []
    for line in f:
        line = line.rstrip()
        line = line.split(',')
        pokemon_img = line[1]
        pokemon_name = line[0]
        link_list.append(pokemon_img)
        name_list.append(pokemon_name)
    return link_list

def get_pokemon_image():
    """This selects a random image from the list of pokemon images"""
    # list of pokemon image links
    print('entered link function')
    pokemon_guess = load_images()
    ran_num = random.randint(0, 150)
    random_pokemon = pokemon_guess[ran_num]
    return random_pokemon

def get_pokemon_name(random_pokemon):
    """This mehod extracts the pokemon name from the link"""
    #random_pokemon = get_pokemon_image()
    slash_index = random_pokemon.rfind('/')
    pokemon_name = random_pokemon[slash_index + 1:len(random_pokemon) - 4]
    return pokemon_name

@app.route('/')
def hello():
    """ initial screen that loads main page"""
    app.logger.info('intial page')
    title = "Hello!"
    test_var = 'lets test this'
    random_pokemon = get_pokemon_image()
    pokemon_name = get_pokemon_name(random_pokemon)
    global global_name
    global_name = pokemon_name
    check_name = 'wonder if you will get the right answer'
    return render_template('index.html', title=title, random_pokemon=random_pokemon, test_var=test_var,
                           pokemon_name=global_name, check_name=check_name)

@app.route('/gresponse') # more input fields will need to be under the same one
def response_handler():
    """After the user has submitted"""
    # getting the value the user has for name
    name_typed = request.args.get('pokemonname')
    title = "Hello!"
    global global_name

    #getting the pokemon type guess value
    type_typed = request.args.get('pokemontype') #getting the users pokemon type value
    type_answer = get_type(global_name) # getting the correct pokemon type value

    #getting the pokemon effective against value
    effective_typed = request.args.get('pokemoneffective') # getting the users value for effectivess
    effective_answer = get_effectiveness(type_answer) # in list form, correct answers for what's super effective

    check_name = ''
    check_type = ''
    check_eff = ''
    if name_typed and type_typed and effective_typed: # if user typees both in
        name_typed = name_typed.lower()
        type_typed = type_typed.lower()
        effective_typed = effective_typed.lower()
        if name_typed == global_name:
            check_name = 'Yay you got the pokemon name right'
        else:
            check_name = 'nope, that is the wrong pokemon name'

        if type_typed == type_answer: # if the users answer matches correct answer
            check_type = 'Yay you got the Pokemon type right'
        else:
            check_type = 'Nope, that is the wrong Pokemon type'

        if effective_typed in effective_answer:
            check_eff = 'You got effectiveness right'
        else:
            check_eff = 'You got effectiveness wrong'
        return render_template('responsepokemon.html', check_name=check_name, check_type=check_type, check_eff=check_eff, pokemon_name=global_name, effective_answer=effective_answer, effective_typed=effective_typed)
    else:
        no_submit = 'You have to fill out all the forms'
        random_pokemon = get_pokemon_image()
        pokemon_name = get_pokemon_name(random_pokemon)
        return render_template('index.html', title=title, check_name=check_name, no_submit=no_submit, random_pokemon=random_pokemon, pokemon_name=pokemon_name)


# on to 2nd tab, compare pokemon!
def info_locations(poke_endpoint):
    """Gets a list of locations this pokemon can be found in"""
    try:
        baseurl = 'https://pokeapi.co/api/v2/pokemon/' + poke_endpoint + '/encounters'
        hdr = {'User-Agent': 'Ish Pokemon App'}
        req = urllib.request.Request(baseurl, headers=hdr)
        response = urllib.request.urlopen(req).read()
        pokedata = json.loads(response)
        poke_locations = []
        for location in pokedata:
            poke_locations.append(location['location_area']['name'])
        return poke_locations
    except:
        return ['ERROR: One or more of these pokemon does not exist. Please double check your spelling']

def info_pokemon_species(poke_endpoint):
    """Pokemon Species endpoint, poke_endpoint = name of pokemon"""
    baseurl = 'https://pokeapi.co/api/v2/pokemon-species/' + poke_endpoint + '/'
    hdr = {'User-Agent': 'Ish Pokemon App'}
    req = urllib.request.Request(baseurl, headers=hdr)
    response = urllib.request.urlopen(req).read()
    pokedata = json.loads(response)
    return pokedata

@app.route('/comparepoke')
def poke_compare():
    """the page when user wants to compare 2 pokemon"""
    title='Comparing Page'
    compare1 = request.args.get('pokemon1')  # first pokemon the user wants to compare
    compare2 = request.args.get('pokemon2')  # second pokemon the user wants to compare
    image_names_list = load_image_names()  # list of pokemon names
    image_links_list = load_images()  # list of corresponding pokemon image links

    if compare1 and compare2:
        compare1 = compare1.lower()  # lower the users answer
        compare2 = compare2.lower()
        if compare1 not in image_names_list or compare2 not in image_names_list:
            error_message = 'ERROR: One or more of these pokemon does not exist.Try again'
            return render_template('compare.html', title=title, error_message=error_message)
        else:
            location1 = info_locations(compare1)  # list of locations the 1st pokemon is found in
            location2 = info_locations(compare2)  # list of locations the 2nd pokemon is found in

            compare1_index = image_names_list.index(compare1)  # index of the 1st pokemon in names list
            compare1_img_link = image_links_list[compare1_index]  # image link of the 1st pokemon
            compare2_index = image_names_list.index(compare2)  # index of the 2nd pokemon in names list
            compare2_img_link = image_links_list[compare2_index]  # image link of the 2nd pokemon

            growth_rate1 = info_pokemon_species(compare1)['growth_rate']['name']
            growth_rate2 = info_pokemon_species(compare2)['growth_rate']['name']

            is_legend1 = info_pokemon_species(compare1)['is_legendary']
            if is_legend1 == False:
                is_legend1 = 'This pokemon is not legendary'
            else:
                is_legend1 = "This pokemon is legendary"
            is_legend2 = info_pokemon_species(compare2)['is_legendary']
            if is_legend2 == False:
                is_legend2 = 'This pokemon is not legendary'
            else:
                is_legend2 = "This pokemon is legendary"
            return render_template('compare.html', title=title, location1=location1, location2=location2,
                                   compare1=compare1, compare2=compare2, compare1_img_link=compare1_img_link,
                                   compare2_img_link=compare2_img_link, growth_rate1=growth_rate1,
                                   growth_rate2=growth_rate2, is_legend1=is_legend1, is_legend2=is_legend2)
    else:
        return render_template('compare.html', title=title)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    name_list = load_image_names()
    print(name_list)
    test = filter_poke()
    print(test)
    #global global_name
    # pokemoninfo = get_type('venomoth') #** test for multiple types
    # print('try in main lol')
    # test_type = get_type('squirtle')
    # print(test_type)
    # #print(pokemoninfo['types'][0]['type']['name'])
    # print(pokemoninfo)
    # load_images()
    # test_link = get_pokemon_image()
    # print(test_link)
    # print(get_pokemon_name(test_link))
    #
    # print('testing name and image links')
    # print(len(load_image_names()))
    # print(len(load_images()))
    #
    # print('testing new endpoint')
    #
    # print('testing tab2')
    # test_species = info_pokemon_species('charmander')
    # print(pretty(test_species['is_legendary']))

    app.run(host="localhost", port=8080)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
