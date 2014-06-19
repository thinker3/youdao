#z::
temp_txt = %userprofile%\git\youdao\word.txt
tempClipboard = %ClipboardAll%
Clipboard =
Send, ^c
ClipWait
FileDelete, %temp_txt%
FileAppend, %Clipboard%, %temp_txt%
Clipboard = %tempClipboard%  ; ClipboardAll no allowed as an output variable
tempClipboard =
return
