__author__ = 'Roger Logan'

# import Tkinter as tk

# if __name__ == '__main__':
#     window = tk.Tk()
#     window.geometry('400x300')
#     window.wm_title('Ya, this is my popup script')
#
#     # listb = tk.Listbox(window)
#     # listb.insert(0,'one')
#     # listb.insert(0,'two')
#     # listb.pack()
#
#     def Check():
#         input = ent.get()
#
#         if input == 'pass' or input == 'hi' :
#             print 'COrrect password'
#         elif input == 'passe':
#             print 'Close but not it'
#         else:
#             print 'wrong wrong wrong'
#
#         ent.delete(0,END)
#         ent.focus()
#
#     # def DrawList():
#     #     plist = ['Liz','Tom','Chi']
#
#     # listbox = tk.Listbox(window)
#     # listbox.pack() # this tells the listbox to come out
#     # button = tk.Button(window,text = "press me",command = DrawList)
#
#
#     # def Pressed():                          #function
#     #     print 'buttons are cool'
#
#     # button = tk.Button(window, text = 'Press', command = Pressed)
#     # button.pack(pady=20, padx = 20)
#     # Pressed()
#
#
#     ent = tk.Entry(window, bg = 'white')
#     button = tk.Button(window, text = 'Press', command = Check)
#
#     window.mainloop()

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

# import Tkinter as tk
# import ttk
#
# class App:
#     def __init__(self):
#         self.root = tk.Tk()
#         self.tree = ttk.Treeview()
#         self.tree.pack()
#         for i in range(10):
#             self.tree.insert("", "end", text="Item %s" % i)
#         self.tree.bind("<Double-1>", self.OnDoubleClick)
#         self.root.mainloop()
#
#     def OnDoubleClick(self, event):
#         item = self.tree.selection()[0]
#         print("you clicked on", self.tree.item(item,"text"))
#
# if __name__ == "__main__":
#     app = App()

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

from Tkinter import *
import ttk

root = Tk()

tree = ttk.Treeview(root)

tree["columns"]=("one","two")
tree.column("one", width=100 )
tree.column("two", width=100)
tree. heading("one", text="coulmn A")

tree.heading("two", text="column B")
tree.insert("" , 0,    text="Line 1", values=("1A","1b"))

# id2 = tree.insert("", 1, "dir2", text="Dir 2")
# tree.insert(id2, "end", "dir 2", text="sub dir 2", values=("2A","2B"))

##alternatively:
tree.insert("", 3, "dir2", text="Dir 2")
tree.insert("dir2", 3, text=" sub dir 2",values=("3A"," 3B"))
tree.insert("dir2", 3, "dir3", text="Dir 3")
tree.insert("dir3", 3, text=" sub dir 3",values=("3A"," 3B"))

tree.pack()
root.mainloop()

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

# import Tkinter as tk
# import tkFont
# import ttk
# #import re
# Actors_list = [("Rowan","Atkinson"),("John","Candy"),("Morgan","Freeman"),("James","Garner"),("Cary","Grant"),("Kate","Hudson"),
# ("Jack","Nicholson"),("William","Powell"),("Arnold","Schwarzenegger"),("Tom","Selleck"),("John","Wayne")]
# Movies_list = [[("Bean","1997"),("Mr. Bean's Holiday","2007"),("The Lion King","1994"),("Johnny English","2003"),("Johnny English Reborn","2011"),("Keeping Mum","2005"),("The Black Adder","1982-1983")],
# [("Dr. Zonk and the Zunkins","1974"),("Tunnel Vision","1976"),("SCTV","1976-1979"),("1941","1979")],
# [("The Pawnbroker","1964"),("Blade","1973"),("The Electric Company","1971-1977"),("Attica","1980"),
# ("Brubaker","1980"),("Street Smart","1980"),("Driving Miss Daisy","1989"),("Glory","1989"),("Unforgiven","1992"),
# ("Outbreak","1995"),("Se7en","1995"),("Amistad","1997"),("The Bucket List","2007")],
# [("Cash McCall","1960"),("Sugarfoot","1957"),("Cheyenne","1955-1957"),("Maverick","1957-1962"),("The Great Escape","1963")],
# [("Singapore Sue","1932"),("She Done Him Wrong","1933"),("I'm No Angel","1933"),("Born to be Bad","1934")],
# [("200 Cigarettes","1999"),("Almost Famous","2000"),("How to Lose a Guy in 10 Days","2003")],
# [("The Cry Baby Killer","1958"),("Seahunt","1961"),("Easy Rider","1969"),("One Flew Over the Cuckoo's Nest","1975")],
# [("Mr. Roberts","1955"),("Ziegfeld Follies","1945"),("Manhattan Melodrama","1934"),("The Thin Man","1934")],
# [("Hercules in New York","1969"),("Conan the Barbarian","1982"),("The Terminator","1984")],
# [("The Rockford Files","1978-1979"),("The Sacketts","1979"),("Magnum, P.I.","1980-1988"),("Blue Bloods","2010-")],
# [("The Shootist","1976"),("McQ","1974"),("The Cowboys","1972"),("Brown of Harvard","1926")]]
# actor_header = ['First Name','Last Name']
# movie_header = ['Movie','Date']
# class McListBox(object):
#     """use a ttk.TreeView as a multicolumn ListBox"""
#     def __init__(self,element_header,element_list):
#         self.element_header = element_header
#         self.element_list = element_list
#         self.tree = None
#         self._setup_widgets()
#         self._build_tree()
#     def _setup_widgets(self):
#         container = ttk.Frame()
#         container.pack(fill='both', expand=True)
#         # create a treeview with scrollbar
#         self.tree = ttk.Treeview(columns=self.element_header, show="headings")
#         vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
#         self.tree.configure(yscrollcommand=vsb.set)
#         self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
#         vsb.grid(column=1, row=0, sticky='ns', in_=container)
#         container.grid_columnconfigure(0, weight=1)
#         container.grid_rowconfigure(0, weight=1)
#         self.tree.bind( "<Double-Button-1>", self.OnClick)
#     def _build_tree(self):
#         for col in self.element_header:
#             self.tree.heading(col, text=col.title(),
#                 command=lambda c=col: sortby(self.tree, c, 0))
#             # adjust the column's width to the header string
#             self.tree.column(col, width=tkFont.Font().measure(col.title()))
#         for item in self.element_list:
#             self.tree.insert('', 'end', values=item)
#             # adjust column's width if necessary to fit each value
#             for ix, val in enumerate(item):
#                 col_w = tkFont.Font().measure(val)
#                 if self.tree.column(self.element_header[ix], width=None) < col_w:
#                     self.tree.column(self.element_header[ix], width=col_w)
#     def OnClick(self, event):
#         global return_index
#         item = self.tree.identify('item',event.x,event.y)
#         return_index = (int((item[1:4]),16) - 1)
#         reload_tree(return_index,self)
# def isnumeric(s):
#     """test if a string is numeric"""
#     for c in s:
#         if c in "1234567890-.":
#             numeric = True
#         else:
#             return False
#     return numeric
# def change_numeric(data):
#     """if the data to be sorted is numeric change to float"""
#     new_data = []
#     if isnumeric(data[0][0]):
#         # change child to a float
#         for child, col in data:
#             new_data.append((float(child), col))
#         return new_data
#     return data
# def sortby(tree, col, descending):
#     """sort tree contents when a column header is clicked on"""
#     # grab values to sort
#     data = [(tree.set(child, col), child) for child in tree.get_children('')]
#     # if the data to be sorted is numeric change to float
#     data = change_numeric(data)
#     # now sort the data in place
#     data.sort(reverse=descending)
#     for ix, item in enumerate(data):
#         tree.move(item[1], '', ix)
#     # switch the heading so that it will sort in the opposite direction
#     tree.heading(col,
#         command=lambda col=col: sortby(tree, col, int(not descending)))
# def reload_tree(tree_index,source_tree):
#     if source_tree == actor_listbox:
#         movie_listbox.tree.grid_forget()
#         movie_listbox.__init__(movie_header,Movies_list[tree_index])
#     elif source_tree == movie_listbox:
#         pass
# root = tk.Tk()
# root.wm_title("ttk.TreeView as multicolumn ListBox")
# actor_listbox = McListBox(actor_header,Actors_list)
# movie_listbox = McListBox(movie_header,Movies_list[0])
# root.mainloop()
# def main():
#     pass
if __name__ == '__main__':
    main()

