# CSGONadesFromDemoApp
 A tool that visualizes utility thrown based on player, round, or utility type

## Requirements
Libraries: tkinter, matplotlib, pandas, functools, demoparser

Python 3

## Usage

Run with
```bash
python app.py
```
 
Select a demo file which is the format for in game replays in CSGO. Formated with .dem.

To select radar directory navigate to the game's directory using Steam > Browse local files. Then navigate to and select /csgo/resource/overviews as the radar folder.

Parse the demo first then input player, utility type, and round as parameters.

Round 0 will be treated as all rounds.



## Demonstration video


<div align="center">
  <video src="https://github.com/rabilmomin/CSGONadesFromDemoApp/assets/43860323/47861e99-b578-4f3a-a1eb-c095c14f25aa" width="800" />
</div>

## Acknowledgements
- Laihoe for their DemoParser https://github.com/LaihoE/Python-demoparser
- Valve for Radar Images
