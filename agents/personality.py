"""
Personality system — varies the look and feel per video.
Each personality defines voice, subtitle colors, layout, and b-roll category.
"""

from dataclasses import dataclass


@dataclass
class Personality:
    voice: str
    subtitle_color: str          # hex or named color → converted to ASS &HAABBGGRR
    subtitle_highlight_color: str
    layout: str                  # "split_screen" or "single_clip"
    broll_category: str          # "city", "nature", "interior", "mixed"

    def ass_primary_color(self) -> str:
        """Convert hex color to ASS &H00BBGGRR format."""
        return _hex_to_ass(self.subtitle_color)

    def ass_highlight_color(self) -> str:
        return _hex_to_ass(self.subtitle_highlight_color)


def _hex_to_ass(color: str) -> str:
    """Convert a color name or #RRGGBB hex to ASS &H00BBGGRR format."""
    named = {
        "white": "&H00FFFFFF",
        "yellow": "&H0000FFFF",
        "red": "&H000000FF",
    }
    lower = color.lower().strip()
    if lower in named:
        return named[lower]
    if lower.startswith("#") and len(lower) == 7:
        r, g, b = lower[1:3], lower[3:5], lower[5:7]
        return f"&H00{b.upper()}{g.upper()}{r.upper()}"
    # Fallback: assume it's already ASS format or return white
    if lower.startswith("&h"):
        return color
    return "&H00FFFFFF"


PERSONALITIES = [
    Personality(
        voice="en-US-ChristopherNeural",
        subtitle_color="white",
        subtitle_highlight_color="white",
        layout="split_screen",
        broll_category="city",
    ),
    Personality(
        voice="en-US-GuyNeural",
        subtitle_color="yellow",
        subtitle_highlight_color="yellow",
        layout="single_clip",
        broll_category="nature",
    ),
    Personality(
        voice="en-US-EricNeural",
        subtitle_color="white",
        subtitle_highlight_color="white",
        layout="split_screen",
        broll_category="interior",
    ),
    Personality(
        voice="en-US-AndrewNeural",
        subtitle_color="#00FF88",
        subtitle_highlight_color="#00FF88",
        layout="single_clip",
        broll_category="mixed",
    ),
    Personality(
        voice="en-US-BrianNeural",
        subtitle_color="#FF6B6B",
        subtitle_highlight_color="#FF6B6B",
        layout="split_screen",
        broll_category="nature",
    ),
    Personality(
        voice="en-US-JennyNeural",
        subtitle_color="white",
        subtitle_highlight_color="white",
        layout="single_clip",
        broll_category="city",
    ),
]


def get_personality(story_index: int) -> Personality:
    """Pick a personality based on story index (cycles through all 6)."""
    p = PERSONALITIES[story_index % len(PERSONALITIES)]
    
    # A/B test for layout
    layout_cycle = story_index % 3
    if layout_cycle == 0:
        layout = "split_screen"
    else:
        layout = "single_clip"
        
    return Personality(
        voice=p.voice,
        subtitle_color=p.subtitle_color,
        subtitle_highlight_color=p.subtitle_highlight_color,
        layout=layout,
        broll_category=p.broll_category,
    )
