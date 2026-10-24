#!/usr/bin/env python3
"""Render the DealReasoner demo video from REAL CLI output.

Frames are PIL-rendered 1280x720 PNGs; ffmpeg assembles them. The terminal
frames show verbatim output captured from `python -m src.ui.cli`
(/tmp/demo-go.txt, /tmp/demo-escalate.txt) — no retyped or invented
output. The sponsor-status frame states the wiring status honestly:
clients implemented + mock-tested; live Cloud/HackOS creds pending.
"""
import os
import subprocess
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
BG = (15, 17, 21)
FG = (230, 237, 243)
DIM = (139, 148, 158)
GREEN = (63, 185, 80)
AMBER = (210, 153, 34)
ACCENT = (88, 166, 255)
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

OUT = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(OUT, "frames")
os.makedirs(FRAMES, exist_ok=True)


def font(path, size):
    return ImageFont.truetype(path, size)


def base():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, H - 34, W, H], fill=(22, 27, 34))
    d.text((24, H - 28), "DealReasoner  ·  Open Agent Hackathon 2026  ·  Track 03",
           font=font(SANS, 15), fill=DIM)
    return img, d


def wrap_lines(text, width):
    out = []
    for para in text.split("\n"):
        out.extend(textwrap.wrap(para, width) or [""])
    return out


def title_card(fname, title, lines, accent=ACCENT):
    img, d = base()
    d.rectangle([60, 150, 72, 430], fill=accent)
    d.text((110, 160), title, font=font(SANS_B, 54), fill=FG)
    y = 280
    for ln in lines:
        for wln in wrap_lines(ln, 62):
            if y > H - 60:
                break
            d.text((110, y), wln, font=font(SANS, 28), fill=DIM)
            y += 42
    img.save(os.path.join(FRAMES, fname))


def term_card(fname, header, body_text, header_color=GREEN):
    img, d = base()
    d.text((60, 40), header, font=font(MONO_B, 26), fill=header_color)
    d.line([60, 84, W - 60, 84], fill=(48, 54, 61), width=2)
    y = 104
    mono = font(MONO, 21)
    for ln in wrap_lines(body_text, 82):
        d.text((60, y), ln, font=mono, fill=FG)
        y += 30
        if y > H - 60:
            break
    img.save(os.path.join(FRAMES, fname))


def main():
    go = open("/tmp/demo-go.txt", encoding="utf-8").read().strip().split("\n")
    esc = open("/tmp/demo-escalate.txt", encoding="utf-8").read().strip().split("\n")

    shots = []
    # 1. Title
    title_card("01_title.png", "DealReasoner",
               ["Verifiable reasoning for freelancer",
                "client go / no-go decisions.",
                "",
                "Every claim cites its evidence. When evidence",
                "is thin, it escalates instead of guessing."],
               accent=GREEN)
    shots.append(("01_title.png", 7))
    # 2. Problem
    title_card("02_problem.png", "The problem",
               ["A freelancer gets vague inbound briefs every week.",
                "Each discovery call costs an hour — most of them",
                "were never a fit.",
                "",
                "There was no structured way to turn a vague",
                "brief into a reliable decision."])
    shots.append(("02_problem.png", 9))
    # 3. The brief
    term_card("03_brief.png", "$ brief in",
              "Hi, I run a real estate agency in Dubai with 40 agents.\n"
              "We spend $6k/month on ads but lead follow-up is manual\n"
              "and slow. Looking for an AI agent to qualify leads on\n"
              "WhatsApp. Budget around $5k for setup plus monthly.\n"
              "Can you do a quick call this week?")
    shots.append(("03_brief.png", 11))
    # 4. Pipeline
    title_card("04_pipeline.png", "THINK → ACT → DECIDE",
               ["ACT gathers evidence: brief signals, deal memory,",
                "profile constraints — each item gets a stable ID.",
                "",
                "THINK proposes 3 competing hypotheses, each",
                "citing evidence IDs.",
                "",
                "TRACE VERIFIER drops uncited claims.",
                "DECIDE scores deal-fit and calibrates the verdict."])
    shots.append(("04_pipeline.png", 11))
    # 5-6. GO verdict (verbatim CLI output, split across two frames)
    term_card("05_go1.png", "VERDICT: GO  ·  confidence 0.89  ·  scorer: jev",
              "\n".join(go[3:13]), header_color=GREEN)
    shots.append(("05_go1.png", 16))
    term_card("06_go2.png", "Reasoning trace — cited claims only",
              "\n".join(go[13:]), header_color=GREEN)
    shots.append(("06_go2.png", 14))
    # 7-8. ESCALATE case (verbatim)
    term_card("07_esc1.png", "When evidence is thin → ESCALATE, not a guess",
              "\n".join(esc[0:12]), header_color=AMBER)
    shots.append(("07_esc1.png", 16))
    term_card("08_esc2.png", "ESCALATE — hypotheses still cited, verdict abstains",
              "\n".join(esc[13:]), header_color=AMBER)
    shots.append(("08_esc2.png", 14))
    # 9. Reliability
    title_card("09_eval.png", "Measured, not claimed",
               ["Eval set: 12 briefs with expected verdicts.",
                "Latest runs: 12/12 correct.",
                "One earlier run: 11/12 — live Jev scoring varies",
                "slightly near thresholds. Reported honestly.",
                "",
                "Abstention policy: thin evidence or low scorer",
                "confidence → ESCALATE to the human."])
    shots.append(("09_eval.png", 12))
    # 10. Sponsor tech — honest status
    title_card("10_sponsors.png", "Sponsor tech — real status",
               ["Zetaris data layer: client implemented + tested;",
                "live Cloud dataset + token pending console access.",
                "",
                "Nemotron via Meterless: client implemented +",
                "tested (planner + fast models); API key issued",
                "in the HackOS workspace.",
                "",
                "Jev scoring: LIVE in every run above.",
                "Local fallback: offline only, labeled in output."])
    shots.append(("10_sponsors.png", 15))
    # 11. Closing
    title_card("11_close.png", "Agents that show their receipts.",
               ["DealReasoner — Track 03, Reasoning Architecture.",
                "",
                "github.com/Shivay00001/dealreasoner",
                "pip install: stdlib only. One command reproduces",
                "the demo: python -m src.ui.cli --brief \"...\""],
               accent=GREEN)
    shots.append(("11_close.png", 8))

    lst = os.path.join(OUT, "concat.txt")
    with open(lst, "w") as fh:
        for fname, dur in shots:
            fh.write(f"file '{os.path.join(FRAMES, fname)}'\n")
            fh.write(f"duration {dur}\n")
        fh.write(f"file '{os.path.join(FRAMES, shots[-1][0])}'\n")
    out_mp4 = os.path.join(OUT, "dealreasoner-demo.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
        "-vsync", "vfr", "-pix_fmt", "yuv420p", "-vf", "scale=1280:720",
        out_mp4], check=True, capture_output=True, text=True)
    total = sum(d for _, d in shots)
    print(f"video: {out_mp4}  frames={len(shots)}  duration~{total}s")


if __name__ == "__main__":
    main()
