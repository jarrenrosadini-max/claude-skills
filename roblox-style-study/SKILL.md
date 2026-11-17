---
name: roblox-style-study
description: Study a Roblox game's look (UI, HUD, buttons, fonts, colors, map, lighting, thumbnail and icon style) from gameplay videos, YouTube/TikTok links, game page links, or screenshots, and write a style guide with exact Roblox values. Also applies a saved style guide to the user's game. Use when the user wants their game to look or feel like another Roblox game, or asks to study a game's UI or aesthetic.
---

# Roblox Style Study

Capture *how a Roblox game looks* and turn it into a style guide that can be built in Studio: real colors, fonts, UI shapes, layout and lighting.

## Rules
- **Capture the style, never copy assets.** Don't reuse another game's logo, name, images, decals, or characters. Recreate the *feel* (palette, shapes, layout, mood) with original work. Copying assets can get a game taken down.
- **Save tokens:** max **15 images** looked at per game. Look at one at a time. Use `palette.py` for colors instead of guessing from images. Never read raw JSON or long command output.
- Never invent details. If something wasn't visible, say so.

## Inputs (use whatever the user gives; ask for screenshots if there's nothing)
1. **Screenshots** (most accurate for UI): ask the user to play the game and take screenshots with **Cmd + Shift + 4** of: the main HUD, a shop/menu, an inventory or upgrade screen, a popup or notification, the lobby/map, and anything they especially like. Put them in `knowledge/style/<game-slug>/shots/`.
2. **YouTube or TikTok gameplay link**: grab frames (see step 2).
3. **Roblox game page link** (`roblox.com/games/<placeId>/...`): get the icon and thumbnails (see step 3).

## Steps

1. **Folders**: notes go in `knowledge/style/<game-slug>/`; temporary work in `.style-work/` (deleted at the end).

2. **Frames from a video** (no full download):
   ```
   yt-dlp --skip-download --print "%(title)s | %(duration)s" "<URL>"
   URL_V=$(yt-dlp -g -f "bv*[height<=1080]/b[height<=1080]/b" "<URL>" | head -1)
   ffmpeg -loglevel error -ss <seconds> -i "$URL_V" -frames:v 1 .style-work/f_<seconds>.jpg
   ```
   Pick 6–10 moments spread across the video, favoring ones where menus, shops or popups are open. If the video has captions, skim the cleaned transcript (`~/.claude/skills/youtube-study/clean_vtt.py`) to find those moments.

3. **Icon and thumbnails from a game page link**:
   ```
   PLACE=<placeId from the URL>
   UNI=$(curl -s "https://apis.roblox.com/universes/v1/places/$PLACE/universe" | python3 -c "import json,sys; print(json.load(sys.stdin)['universeId'])")
   curl -s "https://thumbnails.roblox.com/v1/games/icons?universeIds=$UNI&size=512x512&format=Png" | python3 -c "import json,sys; print(json.load(sys.stdin)['data'][0]['imageUrl'])" | xargs curl -s -o .style-work/icon.png
   curl -s "https://thumbnails.roblox.com/v1/games/multiget/thumbnails?universeIds=$UNI&size=768x432&format=Png&countPerUniverse=3" | python3 -c "import json,sys; [print(t['imageUrl']) for t in json.load(sys.stdin)['data'][0]['thumbnails']]" | head -3 | while read u; do curl -s -o ".style-work/thumb_$RANDOM.png" "$u"; done
   ```
   If any call fails, skip it and continue with what you have.

4. **Get exact colors** with the script next to this file:
   ```
   python3 ~/.claude/skills/roblox-style-study/palette.py <images...> --top 8
   ```
   For UI only, crop to the HUD/menu area with fractions, e.g. bottom bar: `--crop 0,0.8,1,0.2`, right side panel: `--crop 0.7,0,0.3,1`. Run it separately for: whole scene, UI areas, icon/thumbnails.

5. **Look at the images** and note: fonts (closest Roblox `Enum.Font`), corner roundness, outlines/strokes, gradients, shadows, button shapes and sizes, layout (where HUD elements sit), text style (all caps? outlined? bold?), icon style, animations hinted at (pop, bounce, shine), map style (low-poly, realistic, cartoon), materials, lighting and sky mood.

6. **Write `knowledge/style/<game-slug>/style-guide.md`** (keep it tight):
   - **Source**: game name, links, date studied
   - **Vibe in one line** (e.g. "bright, bubbly, rounded cartoon simulator")
   - **Palette**: table of role → hex → `Color3.fromRGB(...)` (background, panel, primary button, secondary button, accent, text, text outline, currency/gold)
   - **Fonts**: titles, buttons, body → `Enum.Font` names; sizes relative to screen; stroke on text yes/no
   - **UI shapes**: `UICorner` radius (as `UDim.new(scale, offset)`), `UIStroke` thickness/color, `UIGradient` colors and rotation, shadows
   - **Layout**: where each HUD element sits (as `UDim2` positions), button sizes, spacing, mobile considerations
   - **Motion**: tween ideas (button hover scale, popup bounce) with rough durations
   - **World**: art style, main materials, lighting (`Lighting` properties: ClockTime, Brightness, Ambient, Atmosphere, ColorCorrection), sky mood
   - **Thumbnail & icon**: composition, colors, text style, what makes it clickable
   - **Do / Don't**: 3–5 bullets each
   - **Not captured**: anything you couldn't see

7. **Index**: add one line to `knowledge/INDEX.md` (create it if missing):
   `- [<game> style](style/<game-slug>/style-guide.md) — style: <vibe in a few words>`

8. **Clean up**: `rm -rf .style-work`. Keep the user's screenshots.

9. **Report back** briefly: the vibe, the palette, and where the guide is. Offer to apply it.

## Applying a style guide to the user's game
When asked to apply a style (in Roblox Studio via the Studio connection):
- Read only the relevant `style-guide.md`.
- Create one `ModuleScript` named `Theme` in `ReplicatedStorage` holding the palette, fonts, corner radius and stroke settings. UI code reads from `Theme`, so restyling later is a one-file change.
- Restyle one screen at a time (HUD first, then shop, then menus). Playtest and take one screenshot after each to check it, then continue.
- Lighting/world changes come after UI, and only when the user asks.
- Make it the user's own: same feel, original names, icons and art.
