# BlendAmp!


## TODO:
- address small inconsistencies between the original winamp skin and the (winamp->blendamp->winamp) round trip skin:
  - player posbar is brighter in the round trip skin?
- extended bottom section missing win->blend
- make sure the default and template skins process back and forth


- add PLEDIT.txt and viscolor.txt support, just make it another texture that the script can reference to generate those text files
  - maybe use a separate texture called "palette" with regions labeled in the actual texture where colors can be defined.. for stuff like the eq visualizer too instead of a one pixel wide column of pixels. this could prob fit on the texture used for text and it would make sense to put it there, since it covers everything else up
- Add support for transparency (look as deus x skin and region.txt tool)
- Reorganize the layers so that the alpha channel of elements such as the eq, volume, and panning handles are compostited over the animated backgrounds
