from Tkinter import Tk, Label

root = Tk()
root.title('ROOT')

# set text at runtime
label_name = Label(root)
label_name.__setitem__('text', 'abc')
label_name.pack()

# "text" can not be omitted
label_phonetic = Label(root, text='phonetic:')
label_phonetic.pack()

label_meaning = Label(root, text='meaning:')
label_meaning.pack()

label_example = Label(root, text='example:')
label_example.pack()

root.mainloop()
