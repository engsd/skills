---
name: image-workflow
description: |
  Article to image generation workflow with placeholder-based insertion.
  Use when user wants to:
  (1) Segment article with placeholder markers (not ## headings)
  (2) Generate AI images and replace placeholders with Cloudinary URLs
  (3) Resolution fixed at 1K, aspect ratio biased to 16:9/3:4
  (4) Default styles: oil painting, Chinese classical, ink wash painting
  (5) Auto-remove citation markers like $ ^{3} $ unless user says "保留引用"

  Triggers: "generate images from article", "分段生成图片", "文章生图", "根据文章生成图片"
---

# Image Workflow

Generate and insert images into articles using placeholder-based insertion.

## Invocation Rules

**Rule 1:** If user invokes skill with no content:
```
@image-workflow
```
→ Show available styles and prompt template options.

**Rule 2:** If user doesn't specify a style:
```
@image-workflow "some article content"
```
→ List reference styles automatically.

**Rule 3:** If user mentions "默认" (default):
```
@image-workflow "默认语境总结"
```
→ Use default context: summarize based on the default skill behavior.

## Workflow

### Step 1: Read Article & Suggest Segmentation

After reading the article:
1. **Remove citations** (unless "保留引用"):
   ```bash
   python scripts/remove_citations.py --file "article.md"
   ```
2. Estimate content length
3. Suggest number of sections (1 section per image)
4. Ask user to confirm or modify

**Suggestion rules:**
- < 500 words: 2-3 sections
- 500-1000 words: 3-4 sections
- 1000-2000 words: 4-6 sections
- > 2000 words: 6-8 sections

### Step 2: Insert Placeholders

Insert `<!-- IMAGE_PLACEHOLDER_1 -->`, `<!-- IMAGE_PLACEHOLDER_2 -->`, etc. at contextually appropriate positions.

**Format:**
```markdown
<!-- IMAGE_PLACEHOLDER_1 -->

[content...]

<!-- IMAGE_PLACEHOLDER_2 -->

[more content...]
```

### Step 3: Generate & Replace

Always use asynchronous batch generation, even for one image:
1. Generate one JSON prompt object per placeholder
2. Save the objects as a JSON array in the output directory's `json/` subfolder
3. Run `scripts/async_batch_generate.py`
4. The script submits all GPT-Image-2 tasks first, polls all task IDs, downloads completed images, uploads them to Cloudinary, and replaces placeholders

**Command:**
```bash
python scripts/async_batch_generate.py --prompts "C:/Users/eng/Desktop/output-html/json/prompts.json" --article "article.md"
```

Do not loop over `generate_and_upload.py` for multiple images. That old pattern submits and waits one image at a time, which is too slow.

## Style Options

Default style themes (choose one, or let AI decide based on article theme):

| Style | Keywords |
|-------|----------|
| 油画风 (`oil_painting`) | "oil painting style", "classical brushwork", "rich textures" |
| 中国古典绘画 (`chinese_classical`) | "traditional Chinese painting", "Gongbi style", "elegant composition" |
| 水墨 (`ink_wash`) | "Chinese ink wash painting", "sumi-e", "minimalist brushstrokes" |

Each big theme must choose a smaller subtheme automatically, based on section content:

| Big theme | Good for | Example subthemes |
|-----------|----------|-------------------|
| 油画风 | war, rulers, ceremonies, political spectacle | dramatic power staging, military-political tableau, golden court spectacle |
| 中国古典绘画 | institutions, diplomacy, elite ritual, governance | Gongbi ritual hierarchy, scroll narrative, object-centered relic composition |
| 水墨 | wabi-sabi, tea rooms, silence, tragedy, interior tension | meditative emptiness, wabi-sabi interior, minimalist ritual space |

## Aspect Ratio

**Bias towards:** 16:9, 3:4 (higher probability)

**Rules:**
- Wide scenes (landscapes, battles): 16:9
- Portrait-oriented scenes (figures, interiors): 3:4
- Other ratios: 1:1, 4:3 (lower probability)

## Fixed Settings

- **Resolution**: 1K (fixed, no user override)
- **Styles**: Oil / Chinese Classical / Ink Wash (default)
- **Submission concurrency**: 3 parallel tasks max by default
- **Upload concurrency**: 3 parallel uploads max by default
- **Polling**: wait 10 seconds after submission, then poll every 5 seconds

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/async_batch_generate.py` | Preferred path: submit all GPT-Image-2 jobs asynchronously, poll, upload, replace placeholders |
| `scripts/batch_generate.py` | Compatibility wrapper that forwards to `async_batch_generate.py` |
| `scripts/generate_and_upload.py` | Legacy/debug single-image path; do not use for article batches |
| `scripts/remove_citations.py` | Remove citation markers like `$ ^{3} $` from markdown |

## Output Directory

Default output location: `C:\Users\eng\Desktop\output-html`

Keep this parent folder tidy by file type. Create subfolders if they do not exist:

| Subfolder | Contents |
|-----------|----------|
| `images/` | Downloaded/generated image files (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`) |
| `json/` | Prompt arrays, task state, and results files (`prompts.json`, `*_results.json`, retry JSON files) |
| `html/` | Final HTML pages and previews (`.html`) |

Do not write generated files directly into `C:\Users\eng\Desktop\output-html` unless the user explicitly asks for a flat layout. If a filename already exists, write a safe renamed file rather than overwriting. Do not delete or clean up files unless the user explicitly confirms each deletion.

## Prompt Generation Rules

1. **Extract key elements**: subject, scene, mood, style
2. **Select big theme**: choose one of `油画风`, `中国古典绘画`, `水墨`
3. **Select subtheme**: choose a smaller direction under the big theme to match the section
4. **Use JSON input**: each image prompt must be represented as a JSON object
5. **Add composition**: "wide composition", "establishing shot", avoid "close-up portrait"

**JSON prompt format:**
```json
{
  "id": 1,
  "placeholder": "IMAGE_PLACEHOLDER_1",
  "title": "section or image title",
  "style_theme": "油画风",
  "style_key": "oil_painting",
  "subtheme": "dramatic power staging",
  "aspect_ratio": "16:9",
  "alt": "short Chinese alt text",
  "prompt": "English generation prompt, including subject, scene, mood, composition, and no close-up portrait"
}
```

When calling the generation script, pass the JSON array file from `output-html/json/` to `async_batch_generate.py`; it reads each object's `prompt`, `style_key`, and `aspect_ratio` fields.

## Async Generation Details

`async_batch_generate.py` follows the official APIMart GPT-Image-2 async flow:

1. `POST /v1/images/generations` for every prompt; each response returns `task_id`.
2. Wait briefly before polling.
3. Poll pending tasks with `POST /v1/tasks/batch` when available, falling back to `GET /v1/tasks/{task_id}`.
4. Read completed image URL from `data.result.images[0].url[0]`.
5. Download immediately and upload to Cloudinary, because APIMart result URLs can expire.

Useful options:
```bash
python scripts/async_batch_generate.py \
  --prompts "C:/Users/eng/Desktop/output-html/json/prompts.json" \
  --article "article.md" \
  --output-dir "C:/Users/eng/Desktop/output-html" \
  --submit-concurrency 3 \
  --upload-concurrency 3
```

With the default `--output-dir`, the script writes PNG files to `output-html/images/` and the results JSON to `output-html/json/`.

## Placeholder Format

Use numbered placeholders in comments:
```
<!-- IMAGE_PLACEHOLDER_1 -->
<!-- IMAGE_PLACEHOLDER_2 -->
```

After processing, replace with:
```markdown
![Description](https://res.cloudinary.com/.../image.png)
```

## Citation Removal

**Auto-remove patterns** (unless user says "保留引用"):
- `$ ^{3} $`, `$ ^{2} $`, etc. (LaTeX-style)
- `^{number}` (bare superscript)
- `[^1]`, `[1]` (Wikipedia-style)

**Usage:**
```bash
python scripts/remove_citations.py --file "article.md"
python scripts/remove_citations.py --file "article.md" --dry-run  # preview
```

## Lessons Learned

1. **Placeholders first**: Insert during segmentation, replace after generation
2. **Fixed 1K resolution**: No user override allowed
3. **Style rotation**: Use different default styles for variety
4. **Biased ratios**: 16:9/3:4 more likely than others
5. **Ask before execute**: Always confirm segmentation plan with user
