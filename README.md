# Custom Legendary Modifications Remade

Source repository for **Custom Legendary Modifications Remade** (CLM), a Fallout 4 mod by Deadmansprice,
originally released in 2016-2017 on [Nexus Mods](https://www.nexusmods.com/fallout4/mods/5565) and Bethesda.net
(PC, Xbox One and PS4).

CLM adds hundreds of craftable legendary weapon and armor modifications, with a holotape configuration menu
that controls which categories show up at the workbench (free or costly recipes, perk variants, spawning,
variants, balanced or OP).

## Layout

- `docs/DESIGN.md` - how the mod works: naming, the configuration system, and techniques learned building it.
- `source/` - Papyrus sources (`.psc`) for the scripts in `data/SCRIPTS`. The 1.09 sources were lost; the terminal
  fragments were recovered from the compiled scripts by `tools/papyrus/rebuild_fragments.py` and verified to
  recompile to identical code.
- `data/` - everything that ships, laid out like the game's `Data` folder: the plugin plus the loose files that get
  packed into `Custom Legendary Modifications Remade - Main.ba2` (scripts, facegen mesh) and `- Textures.ba2`.

## History

The first commit is the **1.09 release exactly as shipped in 2017**. Every later change is its own commit, so the
history doubles as a changelog of the 2.0 overhaul.

## Requirements

The main plugin, `Custom Legendary Modifications Remade.esp`, needs only **Fallout 4** - no DLC. (Version 1.09
required all six DLC.)

Optional add-ons hold the legendaries that use a DLC's creatures, art or effects. Install the ones for the DLC you
own, after the main plugin. They are ESL-flagged, so they do not use a load-order slot:

| Add-on | Needs | Legendaries |
|---|---|---|
| `CLM - Automatron.esp` | Automatron | 13 robot spawns |
| `CLM - Far Harbor.esp` | Far Harbor | 9 creature and Trapper spawns, Paintball x6, Trappin' x4, Moby-Dick's, Silenced Harpoon Striker |
| `CLM - Nuka-World.esp` | Nuka-World | 12 creature and raider spawns |
| `CLM - Contraptions.esp` | Contraptions Workshop | Pyrotechnical x9, Weather Altering x3 |

## License

[CC BY 4.0](LICENSE): use, change and redistribute it, including parts of it in your own mods, as long as you credit the
original author. Fallout 4 and its DLC belong to Bethesda Softworks.

## Credits

From the original mod page. Thank you to everyone who helped shape CLM:

- **teaLz** - the Legendary Modification mod, which showed how to create craftable custom legendary modifications.
- **lilkandeekid** - help with the disintegration effects.
- **Bitflip** - permission to use the fire shield effect from his mod.
- **GLITCHEDMATRIX** - effects from the Fireclaw Whisky mod.
- **Sean_s** - explosion effects from the Grenade Expansion Pack.
- **Granverion** - suggested the Assaultron head laser effect.
- **fireundubh** - the script that adds the configuration holotape to the player's inventory without crashing.
- **shavkacagarikia** - help with the custom script behind Shavka's Explosive Striking.
- **keltas** - discovered that setting a weapon's ammo to none gives infinite ammo, the basis of the Factorium legendaries.
- **cdante** - help with scripts.
- **DankRafft** - years of compatibility patches for Legendary Crafting Framework, Crafting Framework and LEO.
- Everyone who sent requests, bug reports and feedback on Nexus Mods and Bethesda.net.
