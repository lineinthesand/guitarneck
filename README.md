# guitarneck
Python program to help visualizing/mastering scales on the guitar neck

I wrote this little tool for my own guitar study purposes.

It features a GUI in which you can see all the note names on a guitar neck.
The tuning of each string can be modified.
Notes on the fretboard can be marked:
- a left click marks the clicked note in all positions on the neck
- a right click marks an individual note
- a middle click on a note on the lowest string marks notes of the currently selected scale/mode in a three-notes-per-string manner in the current position
  Furthermore, it generates a labeled diagram of that scale (currently png, but svg is easily possible; it uses the drawSvg library for that purpose)
![Scale diagram](/example.png?raw=true "Scale diagram generated with guitarneck")
