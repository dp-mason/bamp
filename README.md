# BlendAmp!

Seamlessly design classic WinAmp skins with Blender.

## TODO:

- put all the pieces in 3d space and then organize them into discrete layers from there, use the snapping to quickly sort along z axis
- fix issue with the eq_enabled button on the main eq texture, it is off by one for some reason, I checked the mapping and it seemed fine, but when you press the button it appears to shift left by a pixel or two
- define blendamp source layers and turn them into collections and view layers in the blender project file, use indirect or holdout or somthing
- add fallback option so that if a region is completely alpha it will pull from a different layer, this way the artist can decide not to do normal/pressed layers for every button and handle if they dont want to... actually this could just be done by starting with all the layers stacked and peeling away each one working backwards to the background
- add PLEDIT.txt and viscolor.txt support, just make it another texture that the script can reference to generate those text files
  - maybe use a separate texture called "palette" with regions labeled in the actual texture where colors can be defined.. for stuff like the eq visualizer too instead of a one pixel wide column of pixels. this could prob fit on the texture used for text and it would make sense to put it there, since it covers everything else up
- Add support for transparency (look as deus x skin and region.txt tool)
- create a script that can reverse engineer winamp -> blendamp skin so that you can make a set of blendamp template layers from an existing winamp skin! Not only does this creat template layers, but it also creates a way to easily modify existing winamp skins by converting to blendamp and then back to winamp!!!

- FAR FUTURE: look at what Ivory skin is doing to do non-standard sizes and button placements in audacious
