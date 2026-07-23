# Bamp!

A modern way to create classic WinAmp skins. Edit with ease, retain full control, use the tools you prefer.

TODO: Link to website

## About

TODO: Improve Intro Paragraph
- make it clear EXACTLY what this being done... bamp converts and existing winamp skin to a stack of images laid out like the final user interface would be, with all elements that would occupy the same space separated across stacked layers

Bamp is a modern alternative specification for WinAmp skins that allows for ease of editing in your graphic design tool of choice. The corresponding converter allows for conversion to and from the standard WinAmp specification allowing you to test changes or modify existing WinAmp skins.
There are two primary advantages to editing skins in Bamp over WinAmp. The first is the layered approach. In the standard specification, each UI element is found in a different area in 2D space, across a wide variety of files of different dimensions, with very little to no relationship to its actual position in the user interface. Alternatively, Bamp provides users with a set of textures whose layout is much closer to how each element would appear when the skin is loaded. For example, the unpressed and pressed state of buttons are defined in the same 2D space across different layers. All the user needs to do after defining the unpressed state  is copy that element to the layer directly above in order to begin work on the pressed state. The way that the converter is written also allows artists to leverage the alpha channel to make the bare minimum changes necessary or to completely omit buttons from their design. This really comes in handy for elements such as the eq, balance, and volume faders that each have 27 states.

**TODO: show image examples**

The second is Bamp allows you to never leave you image editor. In the original WinAmp specification there are two text files: `pledit.txt` and `viscolor.txt` that contain text representations of colors used in the visualization and playlist editor. Instead of requiring the tedious entry of RGB values and hexcodes, Bamp simply asks the user to set these colors in `text.png`. Artists can utilize the palette management tools in their preferred editor to make sure the same colors are used. The converter will generate the necessary text files after converting to the WinAmp specification

**TODO: image examples**

## Quick Start

TODO: verify that this works
1. Download an existing skin you would like to modify from the WinAmp skin museum or if you would like to make a new one from scratch, download your favorite template skin
2. install this repo as a pip package
  - `pip install ./bamp`
3. use the Bamp CLI to convert the winamp skin you downloaded to the Bamp specification. wsz and zip files are supported.
  - `python -m bamp --to-bamp --bamp-dir /path/to/output/bamp/directory --winamp-dir /path/to/winamp/skin.zip`
4. edit the png image layers provided by Bamp in your editor
5. convert back to the WinAmp specification
  - `python -m bamp --to-winamp --bamp-dir /path/to/existing/bamp/directory --winamp-dir /path/to/new/winamp/output.zip`
6. load the output WinAmp skin in an audio player that supports WinAmp skins

## Preservation of History

There are often extraneous files within WinAmp skins that tell a brilliant story about why they were made, who made them, and the cultural context they were made in. Effort has been made to ensure all files that do not directly contribute to the appearance of the skin are preserved in a directory named `extra` in the root of the skin. If you make a new skin or edit an existing one you are encouraged to leave something behind in this directory.

## Motivation

Passionate artists and programmers have kept WinAmp alive as a personalized way to listen to music for 30 years. The skins you find run the gamut from charming, to hilarious, to downright beautiful. People are tickled when they see that a piece of software they use every day can be a meticulously themed after a video game they played in the 80s or in the architectural style of their country. If they memorize the positions of the buttons they can use skins that replace the UI with elvish runes or remove them entirely to make more space for Jackie Chan. Within these small collections of heavily specified bitmaps and text there is a bounty of possible expression.
Given how difficult it is to create a fully featured WinAmp skin, it is impressive how many of them exist. Still, there is room for many more. My hope is that Bamp allows an artist to craft a fully implemented skin or modify an existing one in much less time due to the ease of iteration and ability to leverage the tools provided by their preferred art software, in my case Blender [(I'm serious)](TODO:_URL_HERE).
**TODO:** add embedded links to the skin examples you mentioned.

## TODO

I would love to add support for transparent skins. There are some old programs written in maybe pascal for generating region.txt files that could be translated to python, but this is a bit too much of an undertaking for the beta. If you want to edit and existing skin with transparency just make sure its regions.txt ends up in the root folder. It should be in the `extra` directory after the round trip conversion from WinAmp->Bamp->WinAmp. If anyone would like to help develop this support, open an issue if one does not exist at the time of reading this. I have a general idea of what is needed.


- extended bottom section missing win->blend
- Add support for transparency (look as deus x skin and region.txt tool)
