# Text Animation Effects

Text is one of the most powerful animation surfaces in a terminal UI because it creates motion without requiring images.

## EFFECT.TEXT.INSTANT

Render the full string immediately. This is the default for ordinary data.

## EFFECT.TEXT.TYPEWRITER

Reveal a message character-by-character or in small batches.

Best for:

- leader dialogue;
- historical narration;
- major announcements;
- dramatic results.

Never hide critical error details behind an animation that can be missed.

## EFFECT.TEXT.CENTER_REVEAL

Reveal a centered title outward from its midpoint.

```text
          D
         DI
        DIS
       DISC
      DISCOVERY
```

Use for technology, wonder, palace, and victory titles.

## EFFECT.TEXT.SCRAMBLE

Optional terminal-era transition where placeholder glyphs resolve into a final label.

```text
??????
M?TH??
MATHE?
MATHEMATICS
```

This should be rare and never used for ordinary controls.

## EFFECT.TEXT.NUMBER_ROLL

Changes a number through intermediate values before settling on the authoritative value.

Example:

```text
TREASURY: 149
TREASURY: 150
TREASURY: 153
```

The final number must come from the view model; intermediate values are presentation-only.

## EFFECT.TEXT.REVEAL_WORDS

Reveal a sentence a word at a time. Useful for reports and historical text where character-level animation would be too slow.

## EFFECT.TEXT.ERASE

Remove a line or title from the bottom/top/center before a scene transition. Use sparingly.

## Text safety rules

- preserve terminal width by reserving maximum line length;
- do not animate control labels so fast that keyboard navigation becomes confusing;
- avoid cursor movement that resembles user input while a field is not editable;
- provide a static final representation for screenshots and reduced motion;
- do not use ANSI control sequences directly in canonical semantic references.
