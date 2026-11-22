// bring-the-humans-03 entrypoint (Node 22, standard library only).
//
// The entry is the video itself: an original 18-second vertical ad for
// make.fun, posted publicly on TikTok. This program only hands the house
// the video's address: it reads VIDEO.json from the repository root,
// checks it is a JSON object with a TikTok video URL, and copies it to
// /output/VIDEO.json, where the gate reads it. Nothing this program
// writes about the video is scored -- the house reads the video itself
// from TikTok and counts its views.
//
// The ad (ad.mp4 in this repository) was made in the agent session that
// wrote this file: scripts/build_video.py draws its three scenes and
// scripts/render.sh composites them with the press pack's brand badge
// (from the first frame) and referral end card (last 2.5 s, referral
// code hvn9m3q0) via ffmpeg. See README.md for the caption to post it
// with and for the video's current posting status.
//
// Local run:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const source = join(BOT_DIR, 'VIDEO.json');
const parsed = JSON.parse(readFileSync(source, 'utf8')) as unknown;
if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
  console.error('VIDEO.json must be a JSON object like {"url": "..."}');
  process.exit(1);
}
const url = (parsed as { url?: unknown }).url;
const TIKTOK_VIDEO = /^https:\/\/www\.tiktok\.com\/@[^/\s]+\/video\/\d+$/;
if (typeof url !== 'string' || !TIKTOK_VIDEO.test(url)) {
  console.error(
    'VIDEO.json "url" must be a real posted TikTok video address like\n' +
      'https://www.tiktok.com/@<handle>/video/<numeric id> -- placeholders\n' +
      'such as @<handle>/video/<id> are refused.',
  );
  process.exit(1);
}

mkdirSync(OUTPUT_DIR, { recursive: true });
copyFileSync(source, join(OUTPUT_DIR, 'VIDEO.json'));
console.log(`VIDEO.json copied to ${OUTPUT_DIR} (${url})`);
