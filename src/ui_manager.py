# My Prayers User Interface Manager (View of the MVC model)
#
# these objects are specific to the user interface technology the app uses
#
# this version uses the print() statement for the user interface

from mpo_model import Panel, PanelPgraph, Prayer, NewPrayers
import textwrap

debug = False  # todo read this from parm file


class Display:
    # instantiate a Display object
    # this class is the intermediary between the user and the data
    # class attributes shared by all instances
    last_panel = ''

    def __init__(self):
        # what are the attributes for this object?
        self.last_panel = ''


    def display_panel(self, panel=object):
        # display the PanelPgraph objects for a Panel
        if debug: print(f'Panel: {vars(panel)}')
        # iterate thru PanelPgraph objects associated with the Panel object
        for x in panel.pgraph_list:
            if debug: print(f'pgraph_list: x={x} {x.panel_seq} {x.pgraph_seq}'
                            f' {x.header} {x.verse} {x.text}')
            if x.header == x.header:  # true if not NaN (null)
                print(x.header, '\n')
                header = x.header
            print(textwrap.fill(x.text, 80))
            if x.verse == x.verse:  # false if NaN (null)
                print(x.verse, '\n')
            else:
                print('\n')
        return header

    def continue_prompt(self):
        input('hit return to continue')

