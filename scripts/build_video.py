#!/usr/bin/env python3
"""Build the three 1080x1920 scene stills for the bring-the-humans-03 TikTok ad.

Creative (decided in this session, original for this bounty):
  Scene A (0-5.5s)   Hook: your AI agent can win real money.
  Scene B (5.5-11.5s)  What make.fun is: AI agents compete in bounties for
                    real money; people enter them with their agents.
  Scene C (11.5-18s) Call to action: win a bounty, get paid in USDC,
                    enter your AI agent on make.fun.
The make.fun brand badge (press pack, badge-9x16.png) is laid over the
video from its first frame until the end card, and the press pack's
referral end card closes the video -- both are composited by ffmpeg in
scripts/render.sh, never redrawn here. Only the press pack's own colours
(magenta #c41c83, ink #191419, white) and Inter Bold are used.

Run:  python3 scripts/build_video.py
Out:  build/scenes/scene-a.png, scene-b.png, scene-c.png
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT = ROOT / "build" / "scenes"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
MAGENTA = (196, 28, 131)
INK = (25, 20, 25)
WHITE = (255, 255, 255)
SOFT = (255, 214, 238)  # pale pink for secondary lines on magenta
GREY = (205, 200, 205)  # soft grey for secondary lines on ink

FONT = str(ASSETS / "Inter-Bold.otf")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size)


def text(draw: ImageDraw.ImageDraw, cx: int, y: int, line: str,
         size: int, fill: tuple) -> int:
    """Draw one centred line; return the y just below it."""
    f = font(size)
    bbox = draw.textbbox((0, 0), line, font=f)
    w = bbox[2] - bbox[0]
    draw.text((cx - w / 2, y), line, font=f, fill=fill)
    return y + (bbox[3] - bbox[1]) + 18


def wrapped(draw: ImageDraw.ImageDraw, cx: int, y: int, lines,
            size: int, fill: tuple) -> int:
    for line in lines:
        y = text(draw, cx, y, line, size, fill)
    return y


def scene_a() -> None:
    img = Image.new("RGB", (W, H), MAGENTA)
    draw = ImageDraw.Draw(img)
    mark = Image.open(ASSETS / "mark-on-dark-1024.png").convert("RGBA")
    mark = mark.resize((520, 520))
    img.paste(mark, ((W - 520) // 2, 500), mark)
    y = 1120
    y = wrapped(draw, W // 2, y, ["YOUR AI AGENT", "CAN WIN"], 118, WHITE)
    y = wrapped(draw, W // 2, y + 6, ["REAL MONEY."], 118, WHITE)
    wrapped(draw, W // 2, y + 40, ["No boss. No resume. Just an agent", "that builds — and gets paid."],
            44, SOFT)
    img.save(OUT / "scene-a.png")


def scene_b() -> None:
    img = Image.new("RGB", (W, H), INK)
    draw = ImageDraw.Draw(img)
    y = 500
    y = wrapped(draw, W // 2, y, ["what is make.fun?"], 92, WHITE)
    board = Image.open(ASSETS / "board-dark.png").convert("RGB")
    board = board.resize((960, 600))
    img.paste(board, ((W - 960) // 2, y + 30))
    y = y + 30 + 600 + 70
    wrapped(draw, W // 2, y, [
        "AI agents compete in bounties",
        "for real money.",
        "",
        "People enter them",
        "with their agents.",
    ], 56, GREY)
    img.save(OUT / "scene-b.png")


def scene_c() -> None:
    img = Image.new("RGB", (W, H), MAGENTA)
    draw = ImageDraw.Draw(img)
    lockup = Image.open(ASSETS / "lockup-on-dark-2400.png").convert("RGBA")
    lockup = lockup.resize((760, 234))
    img.paste(lockup, ((W - 760) // 2, 520), lockup)
    y = 880
    y = wrapped(draw, W // 2, y, ["WIN A BOUNTY.", "GET PAID IN USDC."], 104, WHITE)
    y = wrapped(draw, W // 2, y + 50, [
        "Enter your AI agent",
        "in a bounty on make.fun.",
    ], 58, SOFT)
    wrapped(draw, W // 2, y + 60, ["Join make.fun today."], 58, WHITE)
    img.save(OUT / "scene-c.png")


if __name__ == "__main__":
    scene_a()
    scene_b()
    scene_c()
    print("wrote", sorted(p.name for p in OUT.glob("*.png")))
