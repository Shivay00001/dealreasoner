#!/usr/bin/env python3
"""DealReasoner slide deck (reportlab PDF, 8 slides, 16:9)."""
import os

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

W, H = landscape((13.33 * inch, 7.5 * inch))
OUT = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(OUT, "dealreasoner-deck.pdf")
BG = (0.06, 0.07, 0.08)
FG = (0.90, 0.93, 0.95)
DIM = (0.55, 0.58, 0.62)
GREEN = (0.25, 0.73, 0.31)
AMBER = (0.82, 0.60, 0.13)
BLUE = (0.35, 0.65, 1.0)


def slide(c, title, bullets, accent=BLUE):
    c.setFillColorRGB(*BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColorRGB(*accent)
    c.rect(0.6 * inch, H - 1.5 * inch, 0.08 * inch, 0.9 * inch, fill=1, stroke=0)
    c.setFillColorRGB(*FG)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(0.9 * inch, H - 1.25 * inch, title)
    c.setFont("Helvetica", 17)
    y = H - 2.1 * inch
    for b in bullets:
        c.setFillColorRGB(*DIM)
        c.drawString(0.9 * inch, y, b)
        y -= 0.55 * inch
    c.setFillColorRGB(*DIM)
    c.setFont("Helvetica", 11)
    c.drawString(0.6 * inch, 0.4 * inch,
                 "DealReasoner  ·  Open Agent Hackathon 2026  ·  Track 03 Reasoning Architecture")
    c.showPage()


def main():
    c = canvas.Canvas(PDF, pagesize=landscape((13.33 * inch, 7.5 * inch)))
    slide(c, "DealReasoner", [
        "Verifiable reasoning for freelancer client go / no-go decisions.",
        "",
        "Every claim cites its evidence. When evidence is thin,",
        "it escalates instead of guessing.",
        "",
        "github.com/Shivay00001/dealreasoner"], accent=GREEN)
    slide(c, "The problem", [
        "Freelancers get vague inbound briefs every week.",
        "Each discovery call costs an hour — most were never a fit.",
        "No structured way to turn a vague brief into a reliable decision.",
        "",
        "DealReasoner turns a brief into GO / PILOT / NO-GO / ESCALATE."])
    slide(c, "How it reasons", [
        "ACT — gather evidence: brief signals, deal memory, profile constraints.",
        "      Each evidence item gets a stable ID (E1, E2, ...).",
        "THINK — propose 3 competing hypotheses, each citing evidence IDs.",
        "TRACE VERIFY — drop any claim that cites no valid evidence.",
        "DECIDE — score deal-fit, calibrate the verdict, apply policy.",
        "",
        "Pipeline: brief -> ACT -> THINK -> TRACE VERIFY -> DECIDE -> verdict"])
    slide(c, "Live demo — GO case (real output)", [
        "Brief: Dubai real estate agency, 40 agents, $5k setup budget,",
        "       WhatsApp lead-qualification agent.",
        "",
        "VERDICT: GO   ·   confidence 0.89   ·   scorer: Jev",
        "Why: Deal-fit 0.77 via Jev over 9 evidence items [E1].",
        "Reasoning trace: 3 cited claims kept, 0 uncited dropped.",
        "Ask on the call: success in 30 days? deadline? prior vendor?"],
        accent=GREEN)
    slide(c, "Live demo — ESCALATE case (real output)", [
        "Brief: clinic chain exploring ad management; no budget approved yet.",
        "",
        "VERDICT: ESCALATE   ·   confidence 0.73   ·   scorer: Jev",
        "Why: Not enough evidence to decide [E1]: budget undisclosed",
        "       and no red flags to rule on — human review needed.",
        "",
        "This is the reliability behaviour: abstain instead of guessing."],
        accent=AMBER)
    slide(c, "Measured, not claimed", [
        "Eval set: 12 briefs with expected verdicts (src/eval/eval_set.json).",
        "Latest runs: 12/12 correct. One earlier run: 11/12 —",
        "       live Jev scoring varies slightly near thresholds.",
        "",
        "Abstention policy: thin evidence or low scorer confidence",
        "       -> ESCALATE to the human. Pilot-first cap: cold deals",
        "       at or under $2,000 start as PILOT, never GO.",
        "",
        "Reproduce: python -m src.eval.run_eval   (stdlib only, $0)"])
    slide(c, "Sponsor tech — honest status", [
        "Zetaris (data layer): client implemented + tested against the",
        "       documented REST shape; live Cloud dataset + token pending",
        "       console access. Local-KB fallback is labeled in output.",
        "Nemotron via Meterless: client implemented + tested (planner model",
        "       for THINK, fast model for responder); API key issued in the",
        "       HackOS workspace.",
        "Cursor: Agent CLI installed (2026.10.22-27dcf5f); cloud runs need",
        "       a Cursor API key (login step, $0 budget — not available here).",
        "Jev scoring: LIVE in every run shown."])
    slide(c, "Why this wins Track 03", [
        "Reasoning architecture, not a chatbot wrapper: evidence IDs,",
        "competing hypotheses, verified trace, calibrated abstention.",
        "",
        "Impact: saves freelancers hours of dead discovery calls,",
        "       with a decision they can audit line by line.",
        "Technical: stdlib-only, reproducible in one command, $0 to run.",
        "Demo: real terminal output, GO + ESCALATE cases, 126-second video.",
        "",
        "github.com/Shivay00001/dealreasoner"], accent=GREEN)
    c.save()
    print("deck:", PDF)


if __name__ == "__main__":
    main()
