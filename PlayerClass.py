from scraping_functions import replacement_list


def create_alt_names_dict():
    alt_names_dict = {}
    for replacement in replacement_list:
        if replacement_list[replacement] not in alt_names_dict:
            alt_names_dict[replacement_list[replacement]] = replacement
        else:
            alt_names_dict[replacement_list[replacement]] += ', %s' % replacement
    return(alt_names_dict)

def add_alt_name_to_dict(name, replacement):
    global alt_anmes_dict
    if name in alt_names_dict:
        alt_names_dict[name] += ', %s' % replacement
        return(alt_names_dict[name])
    else:
        return(False)
     
def save_alt_names_dict():
    final = ''
    global alt_names_dict
    for name in sorted(alt_names_dict):
        final += '%s: %s\n' % (name, alt_names_dict[name])

    file = open('Names.txt', 'w')
    file.write(final.strip('\n'))
    file.close()

alt_names_dict = create_alt_names_dict()

'''
class Player:
    def __init__(self,ID,name):
        self.id = ID
        self.name = name

    def get_alt_names(self):
        global alt_names_dict
        return(alt_names_dict[self.name])
'''

