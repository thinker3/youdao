; win: #, ctrl: ^, alt: !, shift: +
#z::
!z::
+z::
temp_txt = %userprofile%\selected_word.txt
tempClipboard = %ClipboardAll%
Clipboard =
Send, ^c
ClipWait, 1
FileDelete, %temp_txt%
if (Clipboard != "") {
    FileAppend, %Clipboard%, %temp_txt%
}
Clipboard = %tempClipboard%  ; ClipboardAll no allowed as an output variable
tempClipboard =
return
