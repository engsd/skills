# Workflow Reference

## Placeholder-Based Workflow

### Step 1: Analyze Article

1. Read article content
2. Estimate word count
3. Suggest segmentation count

### Step 2: Ask User for Confirmation

**If user specifies section count:** Use their number.

**If user doesn't specify:** Provide suggestion based on length:

| Word Count | Suggested Sections |
|------------|-------------------|
| < 500 | 2-3 |
| 500-1000 | 3-4 |
| 1000-2000 | 4-6 |
| > 2000 | 6-8 |

### Step 3: Insert Placeholders

Insert numbered placeholder comments at logical break points:

```markdown
# Article Title

<!-- IMAGE_PLACEHOLDER_1 -->

First section content...

<!-- IMAGE_PLACEHOLDER_2 -->

Second section content...

<!-- IMAGE_PLACEHOLDER_3 -->

Third section content...
```

### Step 4: Generate Images

Use asynchronous batch generation for every run, including one-image runs:

1. Analyze surrounding content
2. Generate one JSON prompt object per placeholder
3. Save all objects as a JSON array
4. Run `async_batch_generate.py`
5. Store returned Cloudinary URLs

```bash
python scripts/async_batch_generate.py --prompts "prompts.json" --article "article.md"
```

Do not loop over `generate_and_upload.py`; it waits per image and is only kept for single-image debugging.

### Step 5: Replace Placeholders

```markdown
![Section description](https://res.cloudinary.com/.../image.png)
```

## Fixed Settings

- **Resolution**: 1K (always)
- **Default Styles**: Oil painting / Chinese classical / Ink wash (random unless specified)
- **Aspect Ratio**: 16:9 or 3:4 preferred

## Script Usage

```bash
# Generate and replace all placeholders asynchronously
python scripts/async_batch_generate.py --prompts "prompts.json" --article "article.md"

# Control concurrency
python scripts/async_batch_generate.py --prompts "prompts.json" --submit-concurrency 3 --upload-concurrency 3
```

## Style Keywords

| Style | Keywords |
|-------|----------|
| Oil | "oil painting style", "classical brushwork", "rich textures" |
| Chinese | "traditional Chinese painting", "Gongbi technique", "elegant composition" |
| Ink | "Chinese ink wash", "sumi-e", "minimalist brushstrokes" |
