# How to Target the TFN Music Library

Two meanings of "target" and how to do both.

---

## 1. In-product: How clients target (find) tracks in the library

**Current state:** The CTV Music platform (`/music/`) lets users filter by **genre** and **artist** and use **search**. Campaign creation uses a flat list of tracks (or cart). There is no filtering by sync-relevant attributes.

**Your data already supports it:** `Track` has `mood`, `bpm`, `key`, `genre_tag`, `duration`; `AdCampaign` uses `mood`, `target_audience`, `genre` for the internal ad brief.

### Recommended: Add sync-style filters on the music platform

- **Mood** – Use `Track.mood` (and/or map album/track genre to mood). Add a sidebar filter or dropdown (e.g. Happy, Calm, Energetic, Dramatic) so clients can narrow by vibe.
- **BPM** – Use `Track.bpm`. Add a range filter (e.g. 80–120) or buckets (Slow / Medium / Upbeat) so ad and CTV briefs can match tempo.
- **Key** – Use `Track.key`. Optional dropdown for music-savvy clients or supervisors.
- **Duration** – Use `Track.duration` or derive from audio. Filter “under 30s”, “30–60s”, “60s+” for cues and ads.

**Flow:** Client sets mood + BPM (and optionally genre, key) → view only matching tracks → add to cart → create campaign. That *is* “targeting” the TFN library to the campaign brief.

### Optional: “Sync brief” matching

- Add a small form: “Campaign mood”, “BPM range”, “Genre”, “Use case (e.g. CTV ad, bumper).”
- Back end: filter `Track` by those fields and return a suggested set (or pre-fill a “recommended for this brief” section).
- Reuse the same filters as above; the “brief” is just a saved set of criteria that runs the same query.

### Implementation notes

- **music_platform view:** Accept `GET` params (e.g. `?mood=calm&bpm_min=90&bpm_max=120&genre=Pop`). Filter `Track.objects.all()` with `.filter(mood=..., bpm__gte=..., bpm__lte=..., album__genre__name=...)` (and distinct if needed). Pass filtered queryset to template.
- **Front end:** Add filter controls in the sidebar (or above the track list). Use links or a form that submits GET so URLs are shareable and back-button friendly.
- **Tracks with no mood/BPM:** Either hide them when a mood/BPM filter is applied, or show them in a separate “Uncategorized” section. Ensure metadata is populated (e.g. via `librosa` or admin) so filtering is useful.

---

## 2. Market targeting: Where to put the TFN library in front of buyers

So the *right people* (CTV advertisers, music supervisors, sync buyers) can discover and license TFN tracks.

### CTV / streaming (ads and content)

| Channel | How TFN library gets targeted |
|--------|---------------------------------|
| **Roku, Tubi, Pluto TV, Hulu, Peacock** | Direct deals or via their preferred music/sync vendors. Package TFN as a “cleared music library for CTV ads” with metadata (mood, BPM, key, duration) and simple licensing. |
| **The Trade Desk / Amazon DSP / DV360** | Creative and audio are usually managed outside the DSP. TFN doesn’t “target” inside the DSP; you target *clients* who buy CTV there and offer TFN as their music source for those campaigns. |
| **MNTN, Roku OneView, Vizio Ads** | Same idea: TFN is the music library those advertisers use when building CTV creative; positioning is “music licensed and ready for CTV.” |

### Sync licensing platforms (music supervisors, editors)

| Platform | How to target TFN library there |
|----------|----------------------------------|
| **DISCO** | Used by many music supervisors. Get TFN on DISCO (upload catalog, metadata, stems if applicable) so supervisors can discover and pitch TFN in their workflow. |
| **That Pitch** | Distributes to 100+ sync libraries. Submit TFN catalog so it gets in front of their sync clients; you keep rights and negotiate rev share. |
| **Songtradr** | List TFN as a catalog/label for film, TV, ads, apps. Fill out metadata (genre, mood, BPM, key) so search and filters surface TFN tracks. |
| **MusicBed / Artlist / Epidemic Sound** | Different models (subscription vs. one-off). If TFN is B2B and sync-focused, a direct “TFN sync library” site or integration with one of these may be better than trying to become a generic subscription library. |

### Positioning that helps “targeting” work

- **One-line:** “TFN Music: cleared, metadata-rich catalog for CTV ads and sync.”
- **Metadata:** Ensure every track has at least genre, mood, BPM, key, duration. That’s what platforms and buyers use to *target* (filter) music.
- **Clear rights:** Copyright holder “TFN Music” and clear license type (e.g. sync, CTV, non-exclusive) so buyers know what they’re getting.

---

## Summary

| Goal | Action |
|------|--------|
| **Target the library inside your app** | Add mood, BPM, key (and optionally duration) filters to the music platform and, if useful, a “sync brief” that suggests tracks. Use existing `Track` fields and GET-based filtering. |
| **Target the library in the market** | Submit/upload TFN catalog to sync platforms (DISCO, That Pitch, Songtradr) and position TFN as a cleared, CTV-ready library for direct deals with Roku, Tubi, Pluto, etc. |
| **Make targeting effective** | Keep metadata (mood, BPM, key, genre) populated and consistent so both in-app filters and external platforms can target the TFN library accurately. |
