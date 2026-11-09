# MSNgram launcher icon variants

Implemented all 15 stable launcher choices using the approved ribbon M silhouette, including its original folds, highlights, orbit and sparkles. Each choice has its own palette and framing geometry, not merely a different hue. Existing enum keys, manifest component names, title resources and default Blue selection remain intact.

## Artwork and mapping

- Default: cyan orbit on navy
- Google: warm folded M over four colored rounded tiles
- Colorful: cyan folded M with multicolor diamond confetti
- DarkGreen: emerald hexagon
- Neon: glowing cyan rounded frame
- Niello: muted metallic coin with concentric rims
- Blue: clean cyan/blue dimensional mark
- DarkBlue: blue diamond frame
- BlurBlue: cloud glow
- Telegram: pale messaging bubble with cyan M
- Vintage: copper postage stamp
- Aqua: teal waves
- Premium: gold shield
- Turbo: coral speed streaks
- Nox: silver/cyan eclipse

`validation.json` records every alias/resource mapping, style, composite SHA-256, and generated path. All 15 manifest aliases resolve to their exact new preview layers through the existing adaptive XML resource names. Each alias has square and round legacy PNG fallbacks across mdpi, hdpi, xhdpi, xxhdpi and xxxhdpi. Monochrome themed icons intentionally retain the shared approved M silhouette: Android supplies the user's theme color.

## Files

- Generator: `scripts/generate-msngram-icon-variants.py`
- Enum: `TMessagesProj/src/main/java/org/telegram/ui/LauncherIconController.java`
- Preview geometry correction: `TMessagesProj/src/main/java/org/telegram/ui/Cells/AppIconsSelectorCell.java`
- 150 new density-specific adaptive background/foreground PNGs: `res/drawable-{density}/msngram_{choice}_{background|foreground}.png`
- 150 square/round legacy fallback PNGs: existing alias resource basenames in `res/mipmap-{density}/`
- 30 adaptive square/round XMLs: existing alias resource basenames in `res/mipmap-anydpi-v26/`
- Evidence: `docs/branding/icon-variants/approved-m-source.png`, 15 named composites, `contact-sheet.png`, `validation.json`, this report.

The preview view previously suppressed the foreground for Default and used independent background/foreground scale factors. It now composites both layers using the launcher's 108dp layer / central 72dp visible crop inside its circle. The shared premium preview can supply its background via either image drawable or background drawable. This small additional source change is necessary for preview/launcher geometry parity; artwork alone would leave a smaller mark and incorrect Default preview. Launcher shapes themselves remain controlled by the user's launcher; frame geometry remains visibly different within every mask.

## Executed validation

Generator executed successfully with system Python and Pillow, without installation. Output: 15 unique SHA-256 composite hashes, 330 generated resource files, 315 checked PNGs, zero purple pixels. Purple definition: hue 250–315 degrees, saturation >0.20, value >0.08, alpha >=24. Resampling introduced one edge pixel in that range initially; final save sanitizes only disallowed hues while preserving brightness and alpha. `validation.json` supplies detailed results and paths.

XML parsing and assertions checked every enum's real manifest icon and roundIcon mapping, adaptive layer references and five-density square/round fallback coverage. `git diff --check` passed. Contact-sheet visual review was performed in three crops after full-sheet image analysis timed out: all 15 retain the folded M, distinctive frames were confirmed, and no M clipping was found. Frame clipping at circular boundaries is intentional. No old N title resources were introduced or edited.

System `python3.10` initially inherited an incompatible Pillow path; working invocation is `env -u PYTHONPATH /usr/bin/python3 scripts/generate-msngram-icon-variants.py`. Pillow emitted getdata deprecation warnings only. Generator needs roughly a minute on this host; run with an adequate command timeout.

No build, SDK installation, commit, push or release was performed. Source/resource validation is complete; packaged APK and device rendering remain untested as requested. Other concurrent edits in the shared checkout were left intact.
