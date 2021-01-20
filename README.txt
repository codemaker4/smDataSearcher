SM database searcher made by CodeMaker_4
Version 1.0

Use this tool to search through the SM game files.

   ###   Installation   ###   
Make sure to have python3 installed (older python versions might work too, but are not officially supported)
Go to config.json and make sure the paths/main property is set to the correct folder.

   ###   Usage   ###   
Open a terminal in this folder and type "python3 main.py" or "python main.py" depending on how python is set up.
Try typing "help"

   #   The search command   #
Type "search"
Now you can either paste a uuid or type the name of an item. Partial names like "ood" will also work, the search simply checks if an items name contains the search term. Searching by name is not case sensitive.
You can also type '*' as a search term and it will act like every result was a match. Handy to export a full list of things in SM.
     
   #   The info command   #
Type "info"
Now you can either paste a uuid or type the name of an item, just like in search. The program will find blocks and parts, and print all data about the part, plus some extra properties the program adds as a JSON formatted list.

   #   The reload command   #
Type "reload" to reload all files. Handy if you modified something in the config or game files and don't want to need to restart the program.

   #   The getMake and getUse commands   #
getMake gets all the recipes that make a certain item, and getUse gets all the recipes that use a given item.
The item is always specified with a uuid for these commands, so title searching does NOT work here.