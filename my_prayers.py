'''
Manage a list of prayers by allowing CRUD operations.
Modeled after YouVersion's Pray Now function.
1. Present a welcome message.
2. Present a message that honors God. 
3. Present a message that invites praying for your concerns and a Add Prayer button. 
4. Upon clicking the Add Prayer button, present a dialog to collect and save a prayer. Include a button to + add another prayer.
5. When no more prayers to add, present prayers from the prayer list 3 at a time with a Show More button. Repeat.
6. When the Show More button is not clicked, then present a message that invites God's will to be done.
7. Present a closing message.
'''
# import modules
import welcome, honor_God, my_concerns, Gods_will

# define functions

# define main function
def main():
	welcome.display_msg() # module_filename.function
	honor_God.display_msg()
	my_concerns.manage_prayers()
	Gods_will.display_msg()
 
if __name__ == "__main__":
    main()

# end of module