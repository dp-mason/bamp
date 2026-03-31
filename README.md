# BlendAmp!

Seamlessly design classic WinAmp skins with Blender.

## TODO:
- add option to define input and output directories from the CLI
- address small inconsistencies between the original winamp skin and the (winamp->blendamp->winamp) round trip skin:
  - player posbar is brighter in the round trip skin?
  - (PLAYPAUS.BMP IS SUPER BORKED) default player indicator missing/pink
  - extended bottom section missing win->blend


- define blendamp source layers and turn them into collections and view layers in the blender project file, use indirect or holdout or somthing
- add fallback option so that if a region is completely alpha it will pull from a different layer, this way the artist can decide not to do normal/pressed layers for every button and handle if they dont want to... actually this could just be done by starting with all the layers stacked and peeling away each one working backwards to the background
- add PLEDIT.txt and viscolor.txt support, just make it another texture that the script can reference to generate those text files
  - maybe use a separate texture called "palette" with regions labeled in the actual texture where colors can be defined.. for stuff like the eq visualizer too instead of a one pixel wide column of pixels. this could prob fit on the texture used for text and it would make sense to put it there, since it covers everything else up
- Add support for transparency (look as deus x skin and region.txt tool)

- FAR FUTURE: look at what Ivory skin is doing to do non-standard sizes and button placements in audacious
